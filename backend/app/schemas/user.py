from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, ConfigDict, Field, field_validator, model_validator


class UserResponse(BaseModel):
    user_id: int
    name: str
    email: EmailStr
    is_active: bool
    created_at: datetime
    last_login: datetime | None = None
    roles: List[str] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)

    @field_validator("roles", mode="before")
    @classmethod
    def extract_role_codes(cls, v): 
        if isinstance(v, (list, set)):
            return [r.code if hasattr(r, "code") else str(r) for r in v]
        return []


class UserListRequest(BaseModel):
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=20, ge=1, le=100)
    is_active: bool | None = None
    role: List[str] | None = None
    search: str | None = None
    created_at_from: datetime | None = None
    created_at_to: datetime | None = None
    
    model_config = ConfigDict(extra="forbid")


class UserListResponse(BaseModel):
    users: list[UserResponse]
    total: int           # Tổng số user
    page: int            # Trang hiện tại
    per_page: int        # Số user mỗi trang
    total_pages: int     # Tổng số trang


class UserCreateRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    confirm_password: Optional[str] = Field(default=None, alias="confirmPassword")

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @model_validator(mode="after")
    def validate_password(self):
        if self.confirm_password is not None and self.password != self.confirm_password:
            raise ValueError("Mật khẩu xác nhận không khớp")
        return self


class UserUpdateRequest(BaseModel):
    name: str
    email: EmailStr

    model_config = ConfigDict(extra="forbid")


class UserStatusUpdateRequest(BaseModel):
    is_active: bool

    model_config = ConfigDict(extra="forbid")
