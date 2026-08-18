from typing import Optional, Tuple, List
from sqlalchemy import or_
from sqlalchemy.orm import joinedload

from app.models.audit_log import AuditLog
from app.models.user import User
from app.repositories.base_repository import BaseRepository


class AuditLogRepository(BaseRepository):
    def __init__(self, db):
        super().__init__(AuditLog, db)

    def get_by_id(self, log_id: str) -> Optional[AuditLog]:
        return (
            self.db.query(AuditLog)
            .options(joinedload(AuditLog.actor))
            .filter(AuditLog.id == log_id)
            .first()
        )

    def _apply_filters(self, query, filters: dict):
        filters = dict(filters) if filters else {}

        action_filter = filters.pop("action", None)
        table_name_filter = filters.pop("table_name", None)
        target_id_filter = filters.pop("target_id", None)
        actor_id_filter = filters.pop("actor_id", None)
        search_filter = filters.pop("search", None)

        if action_filter:
            query = query.filter(AuditLog.action.ilike(f"{action_filter.strip()}"))

        if table_name_filter:
            query = query.filter(AuditLog.table_name == table_name_filter.strip())

        if target_id_filter:
            query = query.filter(AuditLog.target_id == str(target_id_filter).strip())

        if actor_id_filter is not None:
            query = query.filter(AuditLog.actor_id == actor_id_filter)

        if search_filter:
            search_term = str(search_filter).strip()
            if search_term:
                query = query.outerjoin(AuditLog.actor).filter(
                    or_(
                        AuditLog.target_id.ilike(f"%{search_term}%"),
                        AuditLog.action.ilike(f"%{search_term}%"),
                        AuditLog.table_name.ilike(f"%{search_term}%"),
                        AuditLog.ip_address.ilike(f"%{search_term}%"),
                        User.name.ilike(f"%{search_term}%"),
                        User.email.ilike(f"%{search_term}%"),
                    )
                )

        return super()._apply_filters(query, filters)

    def get_by_cursor(
        self,
        limit: int = 20,
        cursor: Optional[str] = None,
        filters: Optional[dict] = None,
    ) -> Tuple[List[AuditLog], Optional[str], bool]:
        """
        Phân trang theo con trỏ UUIDv7 (Cursor-based Pagination) đạt hiệu năng O(1)
        loại bỏ hoàn toàn câu lệnh COUNT(*) và OFFSET trên bảng lớn.
        """
        query = self.db.query(AuditLog).options(joinedload(AuditLog.actor))
        query = self._apply_filters(query, filters)

        if cursor:
            cursor_clean = str(cursor).strip()
            if cursor_clean:
                query = query.filter(AuditLog.id < cursor_clean)

        # Sắp xếp mới nhất lên đầu theo UUIDv7 (đã bao hàm timestamp tự nhiên)
        query = query.order_by(AuditLog.id.desc())

        # Lấy thêm 1 bản ghi (limit + 1) để xác định trang tiếp theo có dữ liệu hay không
        items = query.limit(limit + 1).all()

        has_more = len(items) > limit
        if has_more:
            items = items[:limit]
            next_cursor = items[-1].id
        else:
            next_cursor = None

        return items, next_cursor, has_more


def get_audit_log_repository() -> AuditLogRepository:
    from app.db.session import get_db
    return AuditLogRepository(get_db)
