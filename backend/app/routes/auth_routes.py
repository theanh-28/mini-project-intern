import logging

from flask import Blueprint, request, jsonify, g

from app.schemas.auth import LoginRequest, LoginResponse
from app.core.security import create_access_token
from app.services.user_service import get_user_service
from app.core.exceptions import AuthException

auth_bp = Blueprint('auth', __name__)
logger = logging.getLogger(__name__)

@auth_bp.route('/auth/login', methods=['POST'])
def login():
    data = LoginRequest.model_validate(request.json or {})
    
    user_service = get_user_service()
    
    try:
        user = user_service.auth_user(data.email, data.password)
    except AuthException as e:
        logger.error("Authentication failed: %s", e.message)
        return jsonify({"error": e.message, "code": e.code_error}), e.status_code

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
        # Sau có thể thêm 1 bảng database lưu các jti của jwt đã logout
        # để kiểm tra như 1 blacklist dự phòng
        logger.error(f"Lỗi xử lý bên server khi logout: {e}")

    # Luôn trả về 200 dù có lỗi, để client xóa token khỏi local storage
    # Chấp nhận rủi ro để tối ưu UX
    return jsonify({"message": "Đăng xuất thành công"}), 200
         

