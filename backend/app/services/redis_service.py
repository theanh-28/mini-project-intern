import redis
from datetime import datetime, timezone

from app.core.config import settings

class RedisService():
    BLACKLIST_PREFIX = "blacklist:"
    REVOCATION_PREFIX = "user:revoke_at:"
    RESET_TOKEN_FREFIX = "reset_token:"

    def __init__(self, client : redis.Redis | None = None):
        self.client = client or redis.Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            db=settings.redis_db,
            decode_responses=True    # tự động giải mã bytes sang string
        )

    def set(self, key: str, value: str, expire: int = None):
        self.client.set(name=key, value=value, ex=expire)

    def get(self, key: str):
        return self.client.get(name=key)
    
    def delete(self, key: str):
        self.client.delete(key)
    
    def delete_pattern(self, pattern: str):
        """
        Xóa tất cả các key trong Redis có tên khớp với pattern.
        """
        keys = list(self.client.scan_iter(match=pattern))
        if keys:
            self.client.delete(*keys)

    def expire(self, key: str, ttl: int):
        self.client.expire(name=key, time=ttl)  # Gia hạn thoi gian sống của key trong Redis

    def blacklist_token(self, jti: str, ttl: int):
        self.client.set(name=f"{self.BLACKLIST_PREFIX}{jti}", value="1", ex=ttl)

    def is_token_blacklisted(self, jti: str):
        return self.client.exists(f"{self.BLACKLIST_PREFIX}{jti}") == 1
    
    # --- Quản lý phiên đăng nhập (Session Revocation) ---
    def revoke_user_sessions(self, user_id: int, ttl: int):
        """
        Ghi nhận thời điểm thu hồi phiên đăng nhập để vô hiệu hóa tất cả các JWT đã cấp trước đó.
        """
        self.client.set(
            name=f"{self.REVOCATION_PREFIX}{user_id}", 
            value=str(int(datetime.now(timezone.utc).timestamp())), 
            ex=ttl
        )

    def restore_user_sessions(self, user_id: int):
        """
        Xóa mốc thời gian thu hồi, cho phép tài khoản hoạt động bình thường.
        """
        self.client.delete(name=f"{self.REVOCATION_PREFIX}{user_id}")

    def is_session_revoked(self, user_id: int, token_iat: int):
        """
        True nếu token được cấp trước thời điểm thu hồi phiên đăng nhập -> cần hủy
        """
        revoked_at = self.client.get(name=f"{self.REVOCATION_PREFIX}{user_id}")
        return bool(revoked_at) and token_iat < int(revoked_at)
    
    # --- Lưu reset password token ---
    def save_reset_token(self, reset_token: str, user_id: int, ttl: int):
        self.set(
            key=f"{self.RESET_TOKEN_FREFIX}{reset_token}",
            value=str(user_id),
            expire=ttl
        )

    def get_user_id_by_reset_token(self, reset_token: str):
        return self.get(key=f"{self.RESET_TOKEN_FREFIX}{reset_token}")
    
    def invalidate_reset_token(self, reset_token: str):
        self.delete(key=f"{self.RESET_TOKEN_FREFIX}{reset_token}")


redis_service = RedisService()