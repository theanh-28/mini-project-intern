"""
Dùng pydantic để xác thực dữ liệu 
"""

from pydantic import BaseModel, EmailStr, ConfigDict, model_validator

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

    model_config = ConfigDict(extra="forbid")

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    is_admin: bool


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
