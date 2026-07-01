import redis
from app.core.config import settings

class RedisService():
    def __init__(self):
        self.client = redis.Redis(
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

    def blacklist_token(self, jti: str, ttl: int):
        self.client.set(name=f"blacklist:{jti}", value="1", ex=ttl)

    def is_token_blacklisted(self, jti: str):
        return self.client.exists(f"blacklist:{jti}") == 1

redis_service = RedisService()