from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError, ExpiredSignatureError
import uuid
import bcrypt   # Thuật toán băm mật khẩu bcrypt

from app.core.config import settings

def create_access_token(user_id: int, 
                        roles: list[str] | None = None,
                        secret_key: str = settings.secret_key,
                        algorithm: str = settings.algorithm,
                        access_token_expire_minutes: int = settings.access_token_expire_minutes,
                        iss: str = settings.iss) -> str:
    """
    Tạo access token cho người dùng dựa trên user_id và danh sách roles.
    Token sẽ hết hạn sau một khoảng thời gian được định nghĩa trong settings.
    claims trong token bao gồm:
    - jti: token id
    - sub: user_id
    - roles: danh sách mã vai trò (vd: ['admin', 'user'])
    - exp: thời gian hết hạn của token
    """

    if roles is None:
        roles = ["user"]

    expire = datetime.now(timezone.utc) + timedelta(minutes=access_token_expire_minutes)
    payload = {
        "jti": str(uuid.uuid4()),
        "sub": str(user_id),
        "roles": roles,
        "exp": int(expire.timestamp()),
        "iat": int(datetime.now(timezone.utc).timestamp()),
        "iss": iss
    }

    return jwt.encode(payload, secret_key, algorithm=algorithm)

def decode_access_token(token: str,
                        secret_key: str = settings.secret_key,
                        algorithm: str = settings.algorithm) -> dict:
    """
    Giải mã access token và trả về payload chứa các claims.
    Raise ExpiredSignatureError nếu token hết hạn.
    Raise JWTError nếu token không hợp lệ hoặc thiếu claim bắt buộc.
    """
    payload = jwt.decode(token, secret_key, algorithms=[algorithm])

    if not payload.get("sub"):
        raise JWTError("Token thiếu claim 'sub'")

    if not payload.get("jti"):
        raise JWTError("Token thiếu claim 'jti'")

    roles = payload.get("roles")
    if not roles or not isinstance(roles, list):
        raise JWTError("Token thiếu hoặc sai định dạng claim 'roles'")

    return payload

def hash_password(password: str) -> str:
    """
    Băm mật khẩu người dùng.
    """
    salt = bcrypt.gensalt() # Sinh ngẫu nhiên salt
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')

def verify_password(raw_password: str, hashed_password: str) -> bool:
    """
    Kiểm tra mật khẩu người dùng.
    """
    return bcrypt.checkpw(raw_password.encode('utf-8'), hashed_password.encode('utf-8'))
