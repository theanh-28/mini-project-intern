
from datetime import datetime

from pydantic import BaseModel, EmailStr, ConfigDict, Field


class UserResponse(BaseModel):
    user_id: int
    name: str
    email: EmailStr
    is_active: bool
    created_at: datetime
    last_login: datetime | None

    model_config = ConfigDict(from_attributes=True)

class UserListRequest(BaseModel):
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=20, ge=1, le=100)

class UserListResponse(BaseModel):
    users: list[UserResponse]
    total: int           # Tổng số user
    page: int            # Trang hiện tại
    per_page: int        # Số user mỗi trang
    total_pages: int     # Tổng số trang
