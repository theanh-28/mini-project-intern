import math
from flask import Blueprint, request, jsonify, g
import logging

from app.services.user_service import get_user_service
from app.schemas.user import UserListResponse, UserResponse, UserListRequest, UserCreateRequest
from app.core.exceptions import AppException
from app.routes.decorators import cache_response, invalidate_cache, require_admin


admin_bp = Blueprint('admin', __name__)
logger = logging.getLogger(__name__)

@admin_bp.route('/admin/users', methods=['GET'])
@require_admin
@cache_response(key_builder=lambda req, **kwargs: f"users:list:page={req.args.get('page', 1)}:per_page={req.args.get('per_page', 20)}", ttl=60)
def get_users():
    """
    Endpoint để lấy danh sách user với phân trang.
    """
    data = UserListRequest(**(request.args or {}))

    # Lấy thông tin payload từ g object
    payload = g.get("current_user")
    is_admin = payload.get("is_admin")

    user_service = get_user_service()

    try:
        users, total = user_service.get_list_user(is_admin, data.page, data.per_page)
    except AppException as e:
        return jsonify({"error": e.message, "code": e.code_error}), e.status_code

    user_list_response = UserListResponse(
        users=[UserResponse.model_validate(user) for user in users],
        total=total,
        page=data.page,
        per_page=data.per_page,
        total_pages=math.ceil(total / data.per_page) if total > 0 else 0,
    )
    return jsonify(user_list_response.model_dump(mode='json')), 200


@admin_bp.route("/admin/users", methods=["POST"])
@require_admin
@invalidate_cache(key="users:list:page=*:per_page=*")
def create_user():
    """
    Endpoint để tạo user mới.
    Chỉ admin mới có quyền tạo user mới.
    """

    data = UserCreateRequest(**(request.json or {}))

    user_service = get_user_service()

    try:
        new_user = user_service.create_user(
            name=data.name,
            email=data.email,
            password=data.password,
        )
    except AppException as e:
        return jsonify({"error": e.message, "code": e.code_error}), e.status_code
    
    user_response = UserResponse.model_validate(new_user)
    logger.info(f"User created: id={new_user.user_id}, name={new_user.name}, email={new_user.email}, is_admin={new_user.is_admin}")
    return jsonify(user_response.model_dump(mode='json')), 201