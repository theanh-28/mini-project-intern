import math
from flask import Blueprint, request, jsonify, g
from pydantic import ValidationError
import logging

from app.services.user_service import get_user_service
from app.schemas.user import UserListResponse, UserResponse, UserListRequest
from app.core.exceptions import AuthException
from app.routes.decorators import cache_response


admin_bp = Blueprint('admin', __name__)
logger = logging.getLogger(__name__)

@admin_bp.route('/admin/users', methods=['GET'])
@cache_response(key_builder=lambda req, **kwargs: f"users:list:page={req.args.get('page', 1)}:per_page={req.args.get('per_page', 20)}", ttl=60)
def get_users():
    """
    Endpoint để lấy danh sách user với phân trang.
    """
    try:
        data = UserListRequest(**(request.args or {}))
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400

    # Lấy thông tin payload từ g object
    payload = g.get("current_user")
    is_admin = payload.get("is_admin")

    user_service = get_user_service()

    try:
        users, total = user_service.get_list_user(is_admin, data.page, data.per_page)
    except AuthException as e:
        return jsonify({"error": str(e.message), "code": e.code_error}), e.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    user_list_response = UserListResponse(
        users=[UserResponse.model_validate(user) for user in users],
        total=total,
        page=data.page,
        per_page=data.per_page,
        total_pages=math.ceil(total / data.per_page) if total > 0 else 0,
    )
    return jsonify(user_list_response.model_dump(mode='json')), 200
