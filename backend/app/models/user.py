from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.models.role import user_roles


# Khai báo model User
class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True)
    email = Column(String(100), nullable=False, unique=True)
    password = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False, server_default="1")
    is_admin = Column(Boolean, default=False, nullable=False, server_default="0")
    must_change_password = Column(Boolean, default=False, nullable=False, server_default="0")
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Định nghĩa các trường loại trừ hoàn toàn khỏi audit log
    __audit_exclude__ = {"last_login", "updated_at"}

    # Định nghĩa các trường cần dùng mặt nạ bảo vệ
    __audit_mask__ = {"password"}

    audit_logs = relationship("AuditLog", back_populates="actor")
    
    roles = relationship("Role", secondary=user_roles, back_populates="users")