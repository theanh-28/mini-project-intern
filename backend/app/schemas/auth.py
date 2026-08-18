"""
Dùng pydantic để xác thực dữ liệu 
"""

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict, model_validator

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

    model_config = ConfigDict(extra="forbid")

class UserInfo(BaseModel):
    user_id: int
    name: str
    email: EmailStr
    must_change_password: bool = False
    roles: List[str] = []
    permissions: List[str] = []

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserInfo


class ForgotPasswordRequest(BaseModel):
    email: EmailStr

    model_config = ConfigDict(extra="forbid")

class ResetPasswordRequest(BaseModel):
    reset_token: str
    new_password: str
    confirm_password: str

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="after")
    def validate_password(self):
        if self.new_password != self.confirm_password:
            raise ValueError("Password không khớp")
        return self
