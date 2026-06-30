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
        token = create_access_token(user_example.user_id, user_example.is_admin)
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
def test_decode_expired_token_raise(user_example):
    """
    Kiểm tra token hết hạn
    """
    with freeze_time("2026-01-01 00:00:00"):
        token = create_access_token(user_example.user_id, user_example.is_admin)

    # Giả lập sau 2h
    with freeze_time("2026-01-01 02:00:00"):
        try:
            decode_access_token(token)
            print("Lỗi: Token chứa mất khi hết hạn")
        except ExpiredSignatureError:
            pass

def test_decode_wrong_secret_raises(access_token):
    """
    Kiểm tra secret không hợp lệ
    """
    try:
        decode_access_token(access_token, secret_key="fake_secret_key")
        print("Lỗi: token vẫn giải mã được với secret_key khác")
    except JWTError:
        pass

def test_decode_tampered_token_raise(access_token):
    """
    Kiểm tra token bị sửa đổi
    """
    try:
        tampered = access_token[:-5] + "xxxxx"
        decode_access_token(tampered)

        print("Lỗi: Token vẫn giải được khi sửa token")
    except JWTError:
        pass


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

