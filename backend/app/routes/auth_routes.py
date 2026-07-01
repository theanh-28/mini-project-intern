import logging

from flask import Blueprint, request, jsonify, g
from pydantic import ValidationError
from datetime import datetime, timezone

from app.schemas.auth import LoginRequest, LoginResponse
from app.db.session import get_db
from app.services.user_service import UserService
from app.repositories.user_repository import UserRepository
from app.core.security import create_access_token, decode_access_token
from app.services.redis_service import redis_service
from app.core.hook import login_required  


auth_bp = Blueprint('auth', __name__)
logger = logging.getLogger(__name__)

@auth_bp.route('/auth/login', methods=['POST'])
def login():
    try:
        data = LoginRequest(**request.json)
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400
    
    db = get_db()

    user_service = UserService(UserRepository(db))

    user, error = user_service.auth_user(data.email, data.password)

    if not user:
        return jsonify({'error': error}), 401
    
    if not user.is_active:
        return jsonify({'error': "Tài khoản đang bị khóa"}), 403

    user.last_login = datetime.now()
    db.commit()

    access_token = create_access_token(user.user_id, user.is_admin)
    logger.info("User logged in: id=%s, is_admin=%s", user.user_id, user.is_admin)

    response_data = LoginResponse(access_token=access_token, is_admin=user.is_admin)
    return jsonify(response_data.model_dump()), 200


@auth_bp.route('/auth/logout', methods=['POST'])
def logout():
    try:
        # Lây thông tin payload từ g object đã lưu trong login_required()
        payload = g.get("current_user")
        jti = payload.get("jti")
        exp = payload.get("exp")
        
        # Tính TTL còn lại bằng giây
        now = datetime.now(timezone.utc).timestamp()
        ttl = int(exp - now)
        
        # Nếu token vẫn chưa hết hạn thì cho vào blacklist
        if ttl > 0:
            redis_service.blacklist_token(jti, ttl)

        logger.info(f"User logged out: id={payload.get('sub')}")
            
        return jsonify({"message": "Đăng xuất thành công"}), 200
        
    except Exception as e:
        # Lỗi trong quá trình xử lý logout (redis service)
        logger.error(f"Lỗi xư lý bên server khi logout: {str(e)}")

        # Nếu có lỗi, vẫn trả về thành công để bên client xóa token
        return jsonify({"message": "Đăng xuất thành công"}), 200

         

