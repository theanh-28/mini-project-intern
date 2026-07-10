import pytest

# ====== Test Authorization ======

def test_when_no_token_return_401(client):
    """
    Không gửi token → 401
    """
    response = client.post("/admin/users")
    assert response.status_code == 401


def test_when_invalid_token_return_401(client):
    """
    Token không hợp lệ → 401
    """
    response = client.post(
        "/admin/users",
        headers={"Authorization": "Bearer invalid.token.here"}
    )
    assert response.status_code == 401


def test_when_token_is_blacklisted_return_401(client, admin_token, mock_redis):
    """
    Token hợp lệ nhưng đã bị blacklist → 401
    """
    mock_redis.is_token_blacklisted.return_value = True

    response = client.post(
        "/admin/users",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 401


def test_when_non_admin_return_403(client, access_token):
    """
    Token hợp lệ nhưng user không phải admin → 403
    """
    response = client.post(
        "/admin/users",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 403
    data = response.get_json()
    assert data["code"] == "ADMIN_ACCESS_REQUIRED"


# ====== Test Create User Success  ======

def test_when_admin_return_201(client, admin_token):
    """
    Admin token hợp lệ → 201
    """
    response = client.post(
        "/admin/users",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "name": "new_user",
            "email": "new_user@example.com",
            "password": "123456"
        }
    )
    assert response.status_code == 201

    data = response.get_json()
    assert data["name"] == "new_user"
    assert data["email"] == "new_user@example.com"


# ====== Test Payload Validation ======

@pytest.mark.parametrize("payload", [
    {"name": "new_user", "password": "123"},                             # Thiếu email
    {"email": "new_user@example.com", "password": "123"},                  # Thiếu name
    {"name": "new_user", "email": "new_user@example.com"},                  # Thiếu password
    {"name": "new_user", "email": "invalid-email", "password": "123"},     # Email sai định dạng
    {},                                                                    # Payload trống
], ids=[
    "missing_email",
    "missing_name",
    "missing_password",
    "invalid_email_format",
    "empty_payload"
])
def test_create_user_when_invalid_payload_return_400(client, admin_token, mock_redis, payload):
    """
    Gửi payload không hợp lệ => 400 Bad Request, trả về lỗi chuẩn VALIDATION_ERROR và KHÔNG xóa cache
    """
    response = client.post(
        "/admin/users",
        headers={"Authorization": f"Bearer {admin_token}"},
        json=payload
    )
    assert response.status_code == 400
    data = response.get_json()
    assert data["code"] == "VALIDATION_ERROR"
    assert isinstance(data["error"], list)
    assert len(data["error"]) > 0

    # Đảm bảo cache không bị xóa khi validation thất bại
    mock_redis.delete_pattern.assert_not_called()



# ====== Test Business Exceptions ======

def test_when_name_exists_return_409(client, admin_token, mock_redis, insert_users):
    """
    Tên tài khoản muốn tạo đã tồn tại => status_code = 409 và KHÔNG xóa cache
    """

    response = client.post(
        "/admin/users",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "name": "user_1",
            "email": "user_new@example.com",
            "password": "123456"
        }
    )

    assert response.status_code == 409
    mock_redis.delete_pattern.assert_not_called()


def test_when_email_exists_return_409(client, admin_token, mock_redis, insert_users):
    """
    Email tài khoản muốn tạo đã tồn tại => status_code = 409 và KHÔNG xóa cache
    """

    response = client.post(
        "/admin/users",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "name": "user_new",
            "email": "user_1@example.com",
            "password": "123456"
        }
    )

    assert response.status_code == 409
    mock_redis.delete_pattern.assert_not_called()



# ====== Test Cache Invalidation ======

def test_when_create_user_success_then_cache_is_invalidated(client, admin_token, mock_redis):
    """
    Tạo user thành công => Xóa cache danh sách user trong Redis (gọi delete_pattern)
    """
    response = client.post(
        "/admin/users",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "name": "cache_invalid_user",
            "email": "cache_invalid_user@example.com",
            "password": "password123"
        }
    )
    assert response.status_code == 201

    # Kiểm tra delete_pattern được gọi với đúng key pattern
    mock_redis.delete_pattern.assert_called_once_with("users:list:page=*:per_page=*")

