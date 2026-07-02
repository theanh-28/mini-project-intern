from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError, ExpiredSignatureError
import uuid
import bcrypt   # Thuật toán băm mật khẩu bcrypt

from app.core.config import settings

def create_access_token(user_id: int, 
                        is_admin: bool,
                        secret_key: str = settings.secret_key,
                        algorithm: str = settings.algorithm,
                        access_token_expire_minutes: int = settings.access_token_expire_minutes) -> str:
    """
    Tao access token cho người dùng dựa trên user_id và quyền admin.
    Token sẽ hết hạn sau một khoảng thời gian được định nghĩa trong settings.
    claims trong token bao gồm:
    - jti: token id
    - sub: user_id
    - is_admin: quyền admin của người dùng
    - exp: thời gian hết hạn của token
    """

    expire = datetime.now(timezone.utc) + timedelta(minutes=access_token_expire_minutes)
    payload = {
        "jti": str(uuid.uuid4()),
        "sub": str(user_id),
        "is_admin": is_admin,
        "exp": int(expire.timestamp())
    }

    return jwt.encode(payload, secret_key, algorithm=algorithm)

def decode_access_token(token: str, 
                        secret_key: str = settings.secret_key, 
                        algorithm: str = settings.algorithm) -> dict:
    """
    Giải mã access token và trả về payload chứa các claims.
    """
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        user_id:str | None = payload.get("sub")
        if user_id is None:
            return None
        return payload
    except (ExpiredSignatureError, JWTError, ValueError):
        raise

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