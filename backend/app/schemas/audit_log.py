from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, ConfigDict, Field, EmailStr


class ActorInfo(BaseModel):
    user_id: int
    name: str
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)


class AuditLogListItemResponse(BaseModel):
    """
    Schema rút gọn cho danh sách Audit Log (Không chứa old_value / new_value để tối ưu băng thông)
    """
    id: str
    actor_id: Optional[int] = None
    actor: Optional[ActorInfo] = None
    action: str
    table_name: str
    target_id: str
    ip_address: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class AuditLogDetailResponse(BaseModel):
    """
    Schema chi tiết đầy đủ khi người dùng bấm xem một bản ghi log cụ thể
    """
    id: str
    actor_id: Optional[int] = None
    actor: Optional[ActorInfo] = None
    action: str
    table_name: str
    target_id: str
    old_value: Optional[Dict[str, Any]] = None
    new_value: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class AuditLogListRequest(BaseModel):
    """
    Request parameters phân trang theo con trỏ (Cursor-based Pagination)
    """
    limit: int = Field(default=20, ge=1, le=100)
    cursor: Optional[str] = None  # UUIDv7 của bản ghi cuối cùng ở trang trước
    actor_id: Optional[int] = None
    action: Optional[str] = None
    table_name: Optional[str] = None
    target_id: Optional[str] = None
    search: Optional[str] = None
    created_at_from: Optional[datetime] = None
    created_at_to: Optional[datetime] = None

    model_config = ConfigDict(extra="forbid")


class AuditLogListResponse(BaseModel):
    """
    Response phân trang theo con trỏ (Cursor-based Pagination)
    """
    audit_logs: List[AuditLogListItemResponse]
    limit: int
    next_cursor: Optional[str] = None
    has_more: bool
