import json
import logging

from flask import request, g
from jose import ExpiredSignatureError, JWTError

from app.core.security import decode_access_token
from app.core.exceptions import (
    InvalidTokenError,
    TokenExpiredError,
    TokenRevokedError,
    AccountLockedError,
    AuthException,
    AppException,
)

logger = logging.getLogger(__name__)

# Danh sách các endpoint công khai (không yêu cầu đăng nhập)
PUBLIC_ENDPOINTS = [
    "index",
    "auth.login",
    "auth.forgot_password",
    "auth.reset_password"
]


def login_required():
    """
    before_request hook để xác thực người dùng trước mỗi request:
    1. Bỏ qua các endpoint công khai trong PUBLIC_ENDPOINTS và request preflight OPTIONS.
    2. Ưu tiên: Khi chạy qua Kong API Gateway, đọc trực tiếp định danh đã xác thực từ Headers (x-user-id, x-user-roles).
    3. Dự phòng: Khi chạy độc lập (Standalone/Pytest), tự giải mã JWT và kiểm tra Redis.
    """
    if request.method == "OPTIONS":
        return

    if request.endpoint in PUBLIC_ENDPOINTS:
        return

    # --- 1. Nhận diện người dùng từ Kong API Gateway (Đã qua xác thực ở Gateway) ---
    user_id = request.headers.get("x-user-id")
    if user_id:
        roles_header = request.headers.get("x-user-roles")
        token_jti = request.headers.get("x-token-jti")
        token_exp = request.headers.get("x-token-exp")

        roles = []
        if roles_header:
            try:
                roles = json.loads(roles_header) if roles_header.startswith("[") else [r.strip() for r in roles_header.split(",")]
            except Exception:
                roles = [roles_header]

        g.current_user = {
            "sub": str(user_id),
            "roles": roles if isinstance(roles, list) else [roles],
            "jti": token_jti,
            "exp": int(token_exp) if token_exp else None,
        }
        return

    
    # --- 2. Xác thực JWT trực tiếp tại Backend (Khi chạy test hoặc không qua Gateway) ---
    from app.services.redis_service import redis_service

    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise InvalidTokenError("Thiếu token hoặc sai định dạng (Bearer <token>)")

    token = auth_header.split(" ")[1]

    try:
        payload = decode_access_token(token)
    except ExpiredSignatureError:
        raise TokenExpiredError()
    except (JWTError, ValueError):
        raise InvalidTokenError()
    except Exception:
        logger.exception("Lỗi không xác định khi giải mã token")
        raise AuthException("Lỗi xác thực token")

    jti = payload.get("jti")
    user_id = payload.get("sub")
    token_iat = payload.get("iat", 0)

    try:
        # Kiểm tra token đã bị thu hồi (đăng xuất) chưa
        if redis_service.is_token_blacklisted(jti):
            raise TokenRevokedError()
        
        # Kiểm tra xem phiên đăng nhập có bị thu hồi (đổi mật khẩu hoặc bị khóa) không
        if redis_service.is_session_revoked(user_id, token_iat):
            raise TokenRevokedError("Phiên đăng nhập đã bị thu hồi hoặc hết hạn")
    except AppException:
        raise
    except Exception as e:
        # Khi Redis gặp sự cố, log cảnh báo và tạm thời cho qua (chữ ký JWT đã được xác thực hợp lệ)
        logger.warning(f"Lỗi kiểm tra token trong Redis, cho phép tiếp tục phiên: {e}")

    # Lưu payload vào Flask g để các route sử dụng
    g.current_user = payload
    
