import logging
from typing import Tuple, List, Optional

from app.models.audit_log import AuditLog
from app.repositories.audit_log_repository import AuditLogRepository
from app.core.exceptions import AuditLogNotFoundError

logger = logging.getLogger(__name__)


class AuditLogService:
    def __init__(self, audit_log_repository: AuditLogRepository):
        self.audit_log_repo = audit_log_repository

    def get_list_audit_logs(
        self,
        limit: int = 20,
        cursor: Optional[str] = None,
        filters: Optional[dict] = None,
    ) -> Tuple[List[AuditLog], Optional[str], bool]:
        """
        Lấy danh sách Audit Logs phân trang theo con trỏ (Cursor-based) và áp dụng bộ lọc.
        """
        return self.audit_log_repo.get_by_cursor(
            limit=limit,
            cursor=cursor,
            filters=filters,
        )

    def get_audit_log_by_id(self, log_id: str) -> AuditLog:
        """
        Lấy chi tiết một bản ghi Audit Log theo ID (UUIDv7).
        """
        log = self.audit_log_repo.get_by_id(log_id)
        if not log:
            raise AuditLogNotFoundError("Audit Log không tồn tại")
        return log

    def get_user_audit_timeline(
        self,
        user_id: int,
        limit: int = 20,
        cursor: Optional[str] = None,
    ) -> Tuple[List[AuditLog], Optional[str], bool]:
        """
        Lấy dòng thời gian ghi vết thay đổi (Timeline) của một tài khoản user cụ thể.
        """
        filters = {
            "table_name": "users",
            "target_id": str(user_id),
        }
        return self.audit_log_repo.get_by_cursor(
            limit=limit,
            cursor=cursor,
            filters=filters,
        )


def get_audit_log_service() -> AuditLogService:
    """
    Factory function để tạo AuditLogService gắn với session DB hiện tại.
    """
    from app.repositories.audit_log_repository import get_audit_log_repository
    return AuditLogService(audit_log_repository=get_audit_log_repository())
