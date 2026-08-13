import enum
from sqlalchemy import Column, Integer, String, DateTime, Text, Enum as SQLEnum, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.models.role import role_permissions


class ResourceCode:
    USERS = "users"
    ROLES = "roles"
    PERMISSIONS = "permissions"
    AUDIT_LOGS = "audit_logs"


class ActionEnum(str, enum.Enum):
    READ = "read"
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    MANAGE = "manage"


class Permission(Base):
    __tablename__ = "permissions"

    permission_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    resource = Column(String(50), nullable=False)
    action = Column(
        SQLEnum(ActionEnum, native_enum=False, values_callable=lambda x: [e.value for e in x]),
        nullable=False
    )
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    __audit_exclude__ = {"updated_at"}

    __table_args__ = (
        UniqueConstraint('resource', 'action', name='uq_permission_resource_action'),
    )

    @property
    def code(self):
        action_val = self.action.value if hasattr(self.action, "value") else self.action
        return f"{self.resource}:{action_val}"

    roles = relationship("Role", secondary=role_permissions, back_populates="permissions")
