import math
from flask import Blueprint, request, jsonify, g, render_template
from flask_mail import Message
import logging

from app.services.user_service import get_user_service
from app.schemas.user import (
    UserListResponse,
    UserResponse,
    UserListRequest,
    UserCreateRequest,
    UserUpdateRequest,
    UserStatusUpdateRequest,
)
from app.core.extensions import mail
from app.routes.decorators import cache_response, invalidate_cache, require_permission


admin_bp = Blueprint('admin', __name__)
logger = logging.getLogger(__name__)

def make_cache_key(req, **kwargs):
    # Dựng cache key từ tất cả tham số query (hỗ trợ cả dạng ?role=admin&role=editor)
    params = [f"{k}={v}" for k, v in sorted(req.args.items(multi=True))]
    return f"users:list:{':'.join(params)}" if params else "users:list:default"


@admin_bp.route('/admin/users', methods=['GET'])
@require_permission("users:read")
@cache_response(key_builder=make_cache_key, ttl=60)
def get_users():
    """
    Endpoint để lấy danh sách user với phân trang và lọc dữ liệu.
    """
    args_dict = dict(request.args) if request.args else {}
    roles = request.args.getlist("role")
    if roles:
        args_dict["role"] = roles

    data = UserListRequest(**args_dict)

    user_service = get_user_service()

    filters = {
        "is_active": data.is_active,
        "role": data.role,
        "search": data.search,
        "created_at_from": data.created_at_from,
        "created_at_to": data.created_at_to,
    }

    users, total = user_service.get_list_user(
        page=data.page,
        per_page=data.per_page,
        filters=filters
    )

    user_list_response = UserListResponse(
        users=[UserResponse.model_validate(user) for user in users],
        total=total,
        page=data.page,
        per_page=data.per_page,
        total_pages=math.ceil(total / data.per_page) if total > 0 else 0,
    )
    return jsonify(user_list_response.model_dump(mode='json')), 200


@admin_bp.route("/admin/users", methods=["POST"])
@require_permission("users:create")
@invalidate_cache(key="users:list:*")
def create_user():
    """
    Endpoint để tạo user mới.
    Chỉ admin mới có quyền tạo user mới.
    """
    data = UserCreateRequest.model_validate(request.json or {})

    user_service = get_user_service()

    new_user = user_service.create_user(
        name=data.name,
        email=data.email,
        password=data.password,
    )
    
    user_response = UserResponse.model_validate(new_user)
    logger.info(f"User created: id={new_user.user_id}, name={new_user.name}, email={new_user.email}")
    return jsonify(user_response.model_dump(mode='json')), 201


@admin_bp.route("/admin/users/<int:user_id>", methods=["PUT"])
@require_permission("users:update")
@invalidate_cache(key="users:list:*")
def update_user(user_id: int):
    """
    Endpoint để cập nhật thông tin hồ sơ của user (name, email).
    """
    data = UserUpdateRequest.model_validate(request.json or {})

    payload = g.get("current_user")
    
    user_service = get_user_service()

    updated_user = user_service.update_user(
        actor_id=int(payload.get("sub")),
        user_id=user_id,
        name=data.name,
        email=data.email,
    )

    user_response = UserResponse.model_validate(updated_user)
    logger.info(f"User profile updated: id={updated_user.user_id}, name={updated_user.name}, email={updated_user.email}")
    return jsonify(user_response.model_dump(mode='json')), 200


@admin_bp.route("/admin/users/<int:user_id>/status", methods=["PATCH"])
@require_permission("users:update")
@invalidate_cache(key="users:list:*")
def update_user_status(user_id: int):
    """
    Endpoint để cập nhật trạng thái hoạt động của user (is_active: True/False).
    """
    data = UserStatusUpdateRequest.model_validate(request.json or {})

    payload = g.get("current_user")

    user_service = get_user_service()

    updated_user = user_service.update_user_status(
        actor_id=int(payload.get("sub")),
        user_id=user_id,
        is_active=data.is_active,
    )

    user_response = UserResponse.model_validate(updated_user)
    logger.info(f"User status updated: id={updated_user.user_id}, is_active={updated_user.is_active}")
    return jsonify(user_response.model_dump(mode='json')), 200


@admin_bp.route('/admin/users/<int:user_id>', methods=['DELETE'])
@require_permission("users:delete")
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
@require_permission("users:delete")
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


@admin_bp.route('/admin/users/<int:user_id>', methods=['GET'])
@require_permission("users:read")
def get_user_detail(user_id: int):
    """
    Endpoint để lấy thông tin chi tiết một user
    """
    user_service = get_user_service()
    user = user_service.get_user_by_id(user_id=user_id)

    user_response = UserResponse.model_validate(user)
    return jsonify(user_response.model_dump(mode='json')), 200


@admin_bp.route('/admin/users/<int:user_id>/reset-password', methods=['POST'])
@require_permission("users:update")
def admin_reset_password(user_id: int):
    """
    Endpoint để Admin gửi yêu cầu đặt lại mật khẩu cho một user
    """
    payload = g.get("current_user")
    actor_id = int(payload.get("sub"))

    user_service = get_user_service()
    result = user_service.admin_reset_password(actor_id=actor_id, user_id=user_id)

    reset_url = result.get("reset_url")
    if reset_url:
        msg = Message(
            subject="Yêu cầu đặt lại mật khẩu từ Quản trị viên",
            recipients=[result["email"]],
            body=render_template("emails/reset_password.txt", reset_url=reset_url),
            html=render_template("emails/reset_password.html", reset_url=reset_url),
        )
        mail.send(msg)

    logger.info(f"Admin reset password triggered: target_user_id={user_id}, actor_id={actor_id}")
    return jsonify({"message": "Đã gửi email hướng dẫn đặt lại mật khẩu tới người dùng"}), 200

