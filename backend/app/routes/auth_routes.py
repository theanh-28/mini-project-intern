import logging

from flask import Blueprint, request, jsonify, g
from pydantic import ValidationError
from datetime import datetime, timezone

from app.schemas.auth import LoginRequest, LoginResponse
from app.core.security import create_access_token
from app.services.user_service import get_user_service
from app.core.security import create_access_token
from app.core.exceptions import AuthException

auth_bp = Blueprint('auth', __name__)
logger = logging.getLogger(__name__)

@auth_bp.route('/auth/login', methods=['POST'])
def login():
    try:
        data = LoginRequest(**(request.json or {}))
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400
    
    user_service = get_user_service()
    
    try:
        user = user_service.auth_user(data.email, data.password)
    except AuthException as e:
        logger.error("Authentication failed: %s", str(e))
        return jsonify({"error": str(e), "code": e.code_error}), e.status_code

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
        user_id = payload.get("sub")
        
        user_service = get_user_service()
        user_service.logout_user(jti, exp)

        logger.info(f"User logged out: id={user_id}")
                   
    except Exception as e:
        # Lỗi trong quá trình xử lý logout (redis service)
        logger.error(f"Lỗi xư lý bên server khi logout: {str(e)}")

    finally:
        # Nếu có lỗi thì vẫn trả về 200 để client xóa token khỏi local storage
        return jsonify({"message": "Đăng xuất thành công"}), 200
         

