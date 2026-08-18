import logging
from typing import Set, Dict, List
from sqlalchemy.orm import Session, selectinload

from app.models.role import Role
from app.models.permission import ResourceCode

logger = logging.getLogger(__name__)


class RBACRegistry:
    """
    In-Memory Role-Permission Cache / Registry cho Service hiện tại.
    Chỉ nạp và quản lý các quyền đối với các tài nguyên thuộc phạm vi của Service này
    """

    # Danh sách các tài nguyên (resource) thuộc phạm vi quản lý của User/IAM Service này
    SERVICE_RESOURCES: Set[str] = {
        ResourceCode.USERS,
        ResourceCode.ROLES,
        ResourceCode.PERMISSIONS,
        ResourceCode.AUDIT_LOGS,
    }

    def __init__(self):
        # Cấu trúc lưu trữ: { "role_code": {"users:read", "users:create", ...} }
        self._role_permissions: Dict[str, Set[str]] = {}
        self._is_loaded: bool = False

    def load_permissions(self, db: Session) -> None:
        """
        Nạp toàn bộ Role và Permission từ DB vào RAM khi hệ thống khởi động.
        Chỉ lưu các permission có resource thuộc SERVICE_RESOURCES.
        """
        try:
            roles = db.query(Role).options(selectinload(Role.permissions)).all()
            new_role_permissions: Dict[str, Set[str]] = {}

            for role in roles:
                perms_set: Set[str] = set()
                for perm in role.permissions:
                    # Chỉ lấy các quyền của tài nguyên thuộc service này
                    if perm.resource in self.SERVICE_RESOURCES:
                        perms_set.add(perm.code)
                new_role_permissions[role.code] = perms_set

            self._role_permissions = new_role_permissions
            self._is_loaded = True
            logger.info(
                "RBAC Registry đã nạp thành công %d vai trò trong RAM (Scope: %s)",
                len(self._role_permissions),
                list(self.SERVICE_RESOURCES),
            )
        except Exception as e:
            logger.error("Lỗi khi nạp RBAC Registry từ Database: %s", e)
            raise

    def get_permissions_for_roles(self, role_codes: List[str]) -> Set[str]:
        """
        Lấy hợp (union) toàn bộ mã quyền hạn của danh sách roles.
        """
        combined_permissions: Set[str] = set()
        for code in role_codes:
            if code in self._role_permissions:
                combined_permissions.update(self._role_permissions[code])
        return combined_permissions

    def has_permission(self, role_codes: List[str], required_permission: str) -> bool:
        """
        Kiểm tra xem các roles của User có chứa required_permission hay không.
        """
        if not role_codes:
            return False

        user_permissions = self.get_permissions_for_roles(role_codes)
        return required_permission in user_permissions

    def is_loaded(self) -> bool:
        return self._is_loaded

    def clear(self) -> None:
        """Xóa cache (dùng cho test)"""
        self._role_permissions.clear()
        self._is_loaded = False


rbac_registry = RBACRegistry()
