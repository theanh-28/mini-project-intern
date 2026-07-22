import redis.asyncio as redis
from app.core.config import settings

# Khởi tạo đối tượng Redis bất đồng bộ kết nối qua Connection Pool
redis_client = redis.Redis(
    host=settings.redis_host,
    port=settings.redis_port,
    db=settings.redis_db,
    decode_responses=True  # Tự động chuyển data từ bytes thành string cho dễ đọc
)
