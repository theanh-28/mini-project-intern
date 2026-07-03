import logging

from flask import request, jsonify, g
from jose import ExpiredSignatureError, JWTError

from app.core.security import decode_access_token

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
        return jsonify({"error": "Thiếu token hoặc sai định dạng (Bearer <token>)"}), 401

    token = auth_header.split(" ")[1]

    try:
        payload = decode_access_token(token)
    except ExpiredSignatureError:
        return jsonify({"error": "Token đã hết hạn, vui lòng đăng nhập lại"}), 401
    except (JWTError, ValueError):
        return jsonify({"error": "Token không hợp lệ"}), 401
    except Exception:
        logger.exception("Lỗi không xác định khi giải mã token")
        return jsonify({"error": "Lỗi xác thực token"}), 500

    jti = payload.get("jti")

    # Kiểm tra token đã bị thu hồi (đăng xuất) chưa
    try:
        if redis_service.is_token_blacklisted(jti):
            return jsonify({"error": "Token đã bị thu hồi, vui lòng đăng nhập lại"}), 401
    except Exception as e:
        # Nếu có lỗi khi kiểm tra token trong Redis, log lỗi và trả về 500
        logger.error(f"Lỗi kiểm tra token trong Redis: {e}")
        return jsonify({"error": "Lỗi dịch vụ Redis"}), 500

    # Lưu payload vào Flask g để các route sử dụng
    g.current_user = payload
