"""
Dùng pydantic để xác thực dữ liệu 
"""

from pydantic import BaseModel, EmailStr, ConfigDict

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

    model_config = ConfigDict(extra="forbid")

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    is_admin: bool