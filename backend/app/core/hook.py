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
]


def login_required():
    """
    before_request hook để xác thực JWT trước mỗi request.
    Bỏ qua các endpoint công khai trong PUBLIC_ENDPOINTS.
    """
    from app.services.redis_service import redis_service
    
    if request.endpoint in PUBLIC_ENDPOINTS:
        return

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

    try:
        # Kiểm tra token đã bị thu hồi (đăng xuất) chưa
        if redis_service.is_token_blacklisted(jti):
            raise TokenRevokedError()
        
        # Kiểm tra tài khoản đã bị khóa (disabled) chưa
        if redis_service.is_account_locked(user_id):
            raise AccountLockedError()
    except AppException:
        raise
    except Exception as e:
        # Nếu có lỗi khi kiểm tra token trong Redis, log lỗi và trả về AuthException
        logger.error(f"Lỗi kiểm tra token trong Redis: {e}")
        raise AuthException("Lỗi dịch vụ Redis", code_error="REDIS_ERROR")

    # Lưu payload vào Flask g để các route sử dụng
    g.current_user = payload

