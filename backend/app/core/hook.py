from flask import request, jsonify, g

from app.core.security import decode_access_token
from app.services.redis_service import redis_service

# Danh sách các endpoint công khai (không yêu cầu đăng nhập)
PUBLIC_ENDPOINTS = [
    "auth.login",
]

def login_required():
    """
    before_request dùng để kiểm tra xem user đã đăng nhập chưa
    """
    if request.endpoint in PUBLIC_ENDPOINTS:
        return  # Không cần kiểm tra đăng nhập cho các endpoint công khai

    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Thiếu token hoặc token sai định dạng (Bearer <token>)"}), 401
        
    try:
        token = auth_header.split(" ")[1]
        
        payload = decode_access_token(token)
        jti = payload.get("jti")
        
        # Kiểm tra jti có trong payload không
        if not jti:
            return jsonify({"error": "Token không hợp lệ"}), 400
        
        # Kiểm tra xem token này đã bị thu hồi (đăng xuất) chưa
        if redis_service.is_token_blacklisted(jti):
            return jsonify({"error": "Token đã bị vô hiệu hóa (Đã đăng xuất)"}), 401
            
        # Lưu thông tin user vào Flask global g, các route sau có thể dùng
        g.current_user = payload
        
    except Exception:
        return jsonify({"error": "Token không hợp lệ hoặc đã hết hạn"}), 401
