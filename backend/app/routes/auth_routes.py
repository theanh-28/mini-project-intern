import logging

from flask import Blueprint, request, jsonify, g, render_template
from flask_mail import Message

from app.schemas.auth import LoginRequest, LoginResponse, ForgotPasswordRequest, ResetPasswordRequest, UserInfo
from app.services.user_service import get_user_service
from app.core.exceptions import AuthException
from app.core.config import settings
from app.core.extensions import mail

auth_bp = Blueprint('auth', __name__)
logger = logging.getLogger(__name__)

@auth_bp.route('/auth/login', methods=['POST'])
def login():
    data = LoginRequest.model_validate(request.json or {})
    
    user_service = get_user_service()
    
    try:
        auth_result = user_service.auth_user(data.email, data.password)
    except AuthException as e:
        logger.error("Authentication failed: %s", e.message)
        return jsonify({"error": e.message, "code": e.code_error}), e.status_code

    # Nếu bắt buộc đổi mật khẩu lần đầu: không cấp JWT, gửi email chứa link đổi mật khẩu và trả về thông báo
    if auth_result.get("require_password_change"):
        reset_url = auth_result.get("reset_url")
        if reset_url:
            msg = Message(
                subject="Yêu cầu đổi mật khẩu",
                recipients=[data.email],
                body=render_template("emails/reset_password.txt", reset_url=reset_url),
                html=render_template("emails/reset_password.html", reset_url=reset_url),
            )
            mail.send(msg)

        return jsonify({
            "message": auth_result["message"],
            "require_password_change": True,
        }), 200

    user = auth_result["user"]
    logger.info("User logged in: id=%s, roles=%s", user.user_id, auth_result["roles"])

    response_data = LoginResponse(
        access_token=auth_result["access_token"],
        user=UserInfo(
            user_id=user.user_id,
            name=user.name,
            email=user.email,
            must_change_password=False,
            roles=auth_result["roles"],
            permissions=auth_result["permissions"],
        )
    )
    return jsonify(response_data.model_dump(mode="json")), 200


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
         

@auth_bp.route('/auth/forgot-password', methods=['POST'])
def forgot_password():
    """
    Endpoint tiếp nhận yêu cầu quên mật khẩu của user, gửi link đặt lại mật khẩu khi xác nhận thành công
    """
    data = ForgotPasswordRequest.model_validate(request.json or {})

    user_service = get_user_service()

    reset_url = user_service.forgot_password_user(data.email)

    response = {"message": "Nếu địa chỉ email tồn tại, một liên kết đặt lại mật khẩu đã được gửi"}

    if reset_url:
        msg = Message(
            subject="Reset pasword",
            recipients=[data.email],
            body=render_template("emails/reset_password.txt", reset_url=reset_url),
            html=render_template("emails/reset_password.html", reset_url=reset_url),
        )

        mail.send(msg)

    return jsonify(response), 200


@auth_bp.route('/auth/reset-password', methods=['POST'])
def reset_password():
    """
    Endpoint để thực hiện yêu cầu reset mật khẩu của user
    """
    data = ResetPasswordRequest.model_validate(request.json or {})
    reset_token = data.reset_token
    new_password = data.new_password

    user_service = get_user_service()
    
    # Xác thực token và lấy thông tin user
    user = user_service.get_user_by_reset_token(reset_token=reset_token)

    # Thiết lập g.current_user để Audit Log ghi nhận actor_id
    g.current_user = {"sub": str(user.user_id)}

    # Thực hiện đổi mật khẩu
    user_service.reset_password_user(user=user, new_password=new_password, reset_token=reset_token)
    
    logger.info(f"User reset password: user_id = {user.user_id}")
    return jsonify({"message": "Đã đổi mật khẩu thành công"}), 200