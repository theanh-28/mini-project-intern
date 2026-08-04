import math
from flask import Blueprint, request, jsonify, g
import logging

from app.services.user_service import get_user_service
from app.schemas.user import UserListResponse, UserResponse, UserListRequest, UserCreateRequest, UserUpdateRequest
from app.core.exceptions import AppException
from app.routes.decorators import cache_response, invalidate_cache, require_admin


admin_bp = Blueprint('admin', __name__)
logger = logging.getLogger(__name__)

def make_cache_key(req, **kwargs):
    # Dựng cache key từ tất cả tham số query để tránh đè cache khi đổi filter
    params = [f"{k}={v}" for k, v in sorted(req.args.items())]
    return f"users:list:{':'.join(params)}" if params else "users:list:default"


@admin_bp.route('/admin/users', methods=['GET'])
@require_admin
@cache_response(key_builder=make_cache_key, ttl=60)
def get_users():
    """
    Endpoint để lấy danh sách user với phân trang và lọc dữ liệu.
    """
    data = UserListRequest(**(request.args or {}))

    # Lấy thông tin payload từ g object
    payload = g.get("current_user")
    is_admin = payload.get("is_admin")

    user_service = get_user_service()

    filters = {
        "is_active": data.is_active,
        "is_admin": data.is_admin,
        "created_at_from": data.created_at_from,
        "created_at_to": data.created_at_to,
    }

    try:
        users, total = user_service.get_list_user(
            is_admin=is_admin,
            page=data.page,
            per_page=data.per_page,
            filters=filters
        )
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
@invalidate_cache(key="users:list:*")
def create_user():
    """
    Endpoint để tạo user mới.
    Chỉ admin mới có quyền tạo user mới.
    """

    data = UserCreateRequest.model_validate(request.json or {})

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


@admin_bp.route("/admin/users/<int:user_id>", methods=["PUT"])
@require_admin
@invalidate_cache(key="users:list:*")
def update_user(user_id: int):
    """
    Endpoint để cập nhật thông tin của user.
    """

    data = UserUpdateRequest.model_validate(request.json or {})

    payload = g.get("current_user")
    
    user_service = get_user_service()

    try:
        updated_user = user_service.update_user(
            actor_id=int(payload.get("sub")),
            user_id=user_id,
            name=data.name,
            email=data.email,
            is_active=data.is_active,
        )

    except AppException as e:
        return jsonify({"error": e.message, "code": e.code_error}), e.status_code

    user_response = UserResponse.model_validate(updated_user)
    logger.info(f"User updated: id={updated_user.user_id}, name={updated_user.name}, email={updated_user.email}, is_active={updated_user.is_active}")
    return jsonify(user_response.model_dump(mode='json')), 200    

@admin_bp.route('/admin/users/<int:user_id>', methods=['DELETE'])
@require_admin
@invalidate_cache(key='users:list:*')
def delete_user(user_id: int):
    """
    Endpoint để xóa mềm tài khoản
    """
    payload = g.get("current_user")
    actor_id = int(payload.get("sub"))

    user_service = get_user_service()

    user_service.delete_user(actor_id=actor_id, user_id=user_id)

    logger.info(f"User delete: user_id={user_id}, actor_id={actor_id}")

    return "", 204

@admin_bp.route('/admin/users/<int:user_id>/restore', methods=['POST'])
@require_admin
@invalidate_cache(key='users:list:*')
def restore_user(user_id: int):
    """
    Endpoint để khôi phục tài khoản
    """
    payload = g.get("current_user")
    actor_id = int(payload.get("sub"))

    user_service = get_user_service()

    user_service.restore_user(actor_id=actor_id, user_id=user_id)

    logger.info(f"User restore: user_id={user_id}, actor_id={actor_id}")

    return "", 204

