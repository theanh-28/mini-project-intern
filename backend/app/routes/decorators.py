from functools import wraps
import json
import logging
from flask import request, make_response, g

from app.core.exceptions import AdminAccessRequiredError

logger = logging.getLogger(__name__)


def cache_response(key_builder, ttl: int = 60):
    """
    Decorator để cache response của route trong Redis.
    key_builder: function để tạo key cache dựa trên request.
    ttl: thời gian sống của cache (giây).
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            from app.services.redis_service import redis_service

            cache_key = None
            try:
                # Tạo key cache dựa trên request
                cache_key = key_builder(request, **kwargs)
            except Exception as e:
                logger.error(f"Lỗi tạo cache key: {e}")

            if cache_key:
                try:
                    # Kiểm tra xem response đã có trong Redis chưa
                    cached_response = redis_service.get(cache_key)
                    if cached_response:
                        cache_data = json.loads(cached_response)
                        res = make_response(cache_data["data"])
                        res.status_code = cache_data["status_code"]
                        res.headers["Content-Type"] = cache_data.get("content_type", "application/json")
                        redis_service.expire(cache_key, ttl)  # Gia hạn thời gian sống của cache key trong Redis
                        return res
                except Exception as e:
                    logger.error(f"Lỗi đọc từ Redis cache: {e}")

            # Nếu chưa có hoặc lỗi Redis, gọi route function
            response_val = func(*args, **kwargs)

            # Tạo 1 flask Response object để dễ lấy dữ liệu
            try:
                response = make_response(response_val)
            except Exception as e:
                logger.error(f"Lỗi chuyển đổi giá trị trả về của route thành response: {e}")
                return response_val

            # Chỉ cache các response thành công 
            if cache_key and response.status_code in (200,):
                try:
                    cache_data = {
                        "data": response.get_data(as_text=True),
                        "status_code": response.status_code,
                        "content_type": response.headers.get("Content-Type", "application/json")
                    }
                    redis_service.set(cache_key, json.dumps(cache_data), ttl)
                except Exception as e:
                    logger.error(f"Lỗi ghi vào Redis cache: {e}")

            return response_val

        return wrapper
    return decorator


def require_admin(func):
    """
    Decorator để check quyền admin cho các request cần quyền admin
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        payload = g.get("current_user")
        is_admin = payload.get("is_admin")

        if not is_admin:
            raise AdminAccessRequiredError("Yêu cầu quyền Admin")
        
        return func(*args, **kwargs)
    
    return wrapper

