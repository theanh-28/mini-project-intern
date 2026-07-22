from jose import jwt, JWTError, ExpiredSignatureError

from app.core.config import settings
from app.services.redis_service import redis_service
from app.core.exceptions import (
    TokenExpiredError, 
    InvalidTokenError, 
    TokenRevokedError,
    AuthException
)

class AuthService:
    @classmethod
    def verify_token(cls, token: str) -> dict:
        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=settings.algorithm)
            if not payload.get("sub") or not payload.get("jti"):
                raise JWTError
        except ExpiredSignatureError:
            raise TokenExpiredError()
        except (ValueError, JWTError):
            raise InvalidTokenError()
        except Exception:
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
        except AuthException:
            raise
        except Exception as e:
            # Nếu có lỗi khi kiểm tra token trong Redis trả về AuthException
            raise AuthException("Lỗi dịch vụ Redis", code_error="REDIS_ERROR")

        return payload
    