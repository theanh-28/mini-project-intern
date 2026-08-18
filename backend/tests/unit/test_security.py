import pytest
from datetime import datetime, timezone, timedelta

from freezegun import freeze_time
from jose import jwt, ExpiredSignatureError, JWTError

from app.core.security import create_access_token, decode_access_token, hash_password, verify_password


# ====== Test tạo access token =======

def test_create_access_token_contains_jti(access_token):
    """
    Kiểm tra jti có trong token và khác None không
    """
    payload = decode_access_token(access_token)
    assert 'jti' in payload, "Payload không chứa jti"
    assert payload['jti'] is not None, "jti nhận None"

def test_create_access_token_expires_1h(user_example):
    """
    Kiểm tra expiry 1h
    """
    with freeze_time("2026-01-01 00:00:00"):
        token = create_access_token(user_example.user_id, roles=["user"])
        payload = decode_access_token(token)
    
    exp = datetime.fromtimestamp(payload['exp'], tz=timezone.utc)
    expected = datetime(2026, 1, 1, 1, 0, 0, tzinfo=timezone.utc)

    assert exp == expected

def test_create_access_token_algorithm_HS256(access_token):
    """
    Kiểm tra thuật toán sử dụng (HS256)
    """
    header = jwt.get_unverified_header(access_token)
    print(header)
    assert header['alg'] == "HS256", "Sai thuật toán sử dụng (HS256)"

def test_create_access_token_contains_user_id(user_example, access_token):
    """
    Kiểm tra thông tin user_id
    """
    payload = decode_access_token(access_token)

    assert 'sub' in payload, "Payload không chứa sub"
    assert int(payload['sub']) == user_example.user_id, "Sai thông tin user_id"


# ====== Test decode token ======
def test_decode_expired_token_raises(user_example):
    """
    Kiểm tra token hết hạn raise ExpiredSignatureError
    """
    with freeze_time("2026-01-01 00:00:00"):
        token = create_access_token(user_example.user_id, roles=["user"])

    with freeze_time("2026-01-01 02:00:00"):
        with pytest.raises(ExpiredSignatureError):
            decode_access_token(token)

def test_decode_wrong_secret_raises(access_token):
    """
    Kiểm tra sai secret key raise JWTError
    """
    with pytest.raises(JWTError):
        decode_access_token(access_token, secret_key="fake_secret_key")

def test_decode_tampered_token_raises(access_token):
    """
    Kiểm tra token bị giả mạo raise JWTError
    """
    tampered = access_token[:-5] + "xxxxx"
    with pytest.raises(JWTError):
        decode_access_token(tampered)

def test_decode_token_missing_sub_raises():
    """
    Kiểm tra token thiếu claim 'sub' raise JWTError
    """
    from app.core.config import settings
    payload_no_sub = {
        "jti": "some-jti",
        "roles": ["user"],
        "exp": 9999999999
    }
    token = jwt.encode(payload_no_sub, settings.secret_key, algorithm=settings.algorithm)
    with pytest.raises(JWTError):
        decode_access_token(token)

def test_decode_token_missing_roles_raises():
    """
    Kiểm tra token thiếu claim 'roles' raise JWTError
    """
    from app.core.config import settings
    payload_no_roles = {
        "jti": "some-jti",
        "sub": "1",
        "exp": 9999999999
    }
    token = jwt.encode(payload_no_roles, settings.secret_key, algorithm=settings.algorithm)
    with pytest.raises(JWTError):
        decode_access_token(token)


# ====== Test password ======
def test_hash_password_not_equal_raw():
    """
    Kiểm trả password đã được hash chưa
    """
    hashed = hash_password("password123")
    assert hashed != "password123", "Lỗi: hash password giống password"

def test_hash_same_password_different_hash():
    """
    Kiểm tra 2 password giống nhau hash giống nhau không
    """
    hash1 = hash_password("password123")
    hash2 = hash_password("password123")

    assert hash1 != hash2, "Lỗi: hash password giống nhau"

def test_verify_password():
    """
    Kiểm tra hàm verify_password() với trường hợp đúng và sai password
    """
    hashed = hash_password("password123")

    assert verify_password("", hashed) == False, "Lỗi: Nhận password rỗng"
    assert verify_password("password123", hashed) == True, "Lỗi: password hợp lệ nhưng thất bại"
    assert verify_password("password", hashed) == False, "Lỗi: password không hợp lệ nhưng thành công"

