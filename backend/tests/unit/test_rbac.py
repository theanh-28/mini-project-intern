import pytest
from flask import g

from app.core.rbac import RBACRegistry, rbac_registry
from app.core.exceptions import PermissionDeniedError, InvalidTokenError
from app.routes.decorators import require_permission
from app.models.role import Role
from app.models.permission import Permission, ActionEnum


def test_rbac_registry_resource_filtering(db_session):
    """
    Kiểm tra RBAC Registry chỉ nạp các permission thuộc scope của service (users, roles, permissions, audit_logs)
    và bỏ qua các resource của microservice khác.
    """
    registry = RBACRegistry()
    registry.SERVICE_RESOURCES = {"users", "roles"}

    # Lấy permission 'users:read' đã có sẵn trong db_session
    perm_valid = db_session.query(Permission).filter(
        Permission.resource == "users",
        Permission.action == ActionEnum.READ
    ).first()

    # Tạo role và permission thuộc service khác (ví dụ: orders)
    role = Role(name="Test Role", code="test_role", is_system=False)
    perm_other_service = Permission(name="Read Orders", resource="orders", action=ActionEnum.READ)

    role.permissions.extend([perm_valid, perm_other_service])
    db_session.add_all([role, perm_other_service])
    db_session.commit()

    registry.load_permissions(db_session)

    # Chỉ có 'users:read' được nạp, 'orders:read' bị loại bỏ
    perms = registry.get_permissions_for_roles(["test_role"])
    assert "users:read" in perms
    assert "orders:read" not in perms


def test_require_permission_decorator_allowed(app):
    """
    Kiểm tra decorator @require_permission cho phép truy cập khi có quyền.
    """
    @require_permission("users:read")
    def sample_endpoint():
        return "success"

    with app.test_request_context():
        g.current_user = {"sub": "999", "roles": ["admin"]}
        result = sample_endpoint()
        assert result == "success"


def test_require_permission_decorator_denied(app):
    """
    Kiểm tra decorator @require_permission chặn và ném PermissionDeniedError khi thiếu quyền.
    """
    @require_permission("users:read")
    def sample_endpoint():
        return "success"

    with app.test_request_context():
        g.current_user = {"sub": "1", "roles": ["user"]}
        with pytest.raises(PermissionDeniedError):
            sample_endpoint()

