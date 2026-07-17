import redis
from datetime import datetime, timezone

from app.core.config import settings

class RedisService():
    BLACKLIST_PREFIX = "blacklist:"
    ACCOUNT_LOCK_PREFIX = "user:lock_at:"

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
    
    # --- Khóa tài khoản ---
    def lock_account(self, user_id: int, ttl: int):
        self.client.set(
            name=f"{self.ACCOUNT_LOCK_PREFIX}{user_id}", 
            value=str(int(datetime.now(timezone.utc).timestamp())), 
            ex=ttl
        )

    def unlock_account(self, user_id: int):
        self.client.delete(name=f"{self.ACCOUNT_LOCK_PREFIX}{user_id}")

    def is_account_locked(self, user_id: int, token_iat: int):
        """
        True nếu token được cấp trước thời điểm khóa -> cần revoke
        """
        locked_at = self.client.get(name=f"{self.ACCOUNT_LOCK_PREFIX}{user_id}")
        return bool(locked_at) and token_iat < int(locked_at)


redis_service = RedisService()