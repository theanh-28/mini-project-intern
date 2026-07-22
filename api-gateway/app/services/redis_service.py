import redis.asyncio as redis
from datetime import datetime, timezone

from app.core.config import settings
from app.clients.redis_client import redis_client

class RedisService():
    BLACKLIST_PREFIX = "blacklist:"
    REVOCATION_PREFIX = "user:revoke_at:"

    def __init__(self, client : redis.Redis | None = None):
        self.client = client

    def set(self, key: str, value: str, expire: int = None):
        self.client.set(name=key, value=value, ex=expire)

    def get(self, key: str):
        return self.client.get(name=key)
    
    def delete(self, key: str):
        self.client.delete(key)

    def is_token_blacklisted(self, jti: str):
        return self.client.exists(f"{self.BLACKLIST_PREFIX}{jti}") == 1
    
    def is_session_revoked(self, user_id: int, token_iat: int):
        revoked_at = self.client.get(name=f"{self.REVOCATION_PREFIX}{user_id}")
        return bool(revoked_at) and token_iat < int(revoked_at)

 

redis_service = RedisService(redis_client)