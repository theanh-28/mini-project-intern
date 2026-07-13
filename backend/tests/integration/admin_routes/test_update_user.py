import pytest

# ====== Test Authorization ======

def test_when_no_token_return_401(client):
    """
    Không gửi token → 401
    """
    response = client.put("/admin/users/3")
    assert response.status_code == 401


def test_when_invalid_token_return_401(client):
    """
    Token không hợp lệ → 401
    """
    response = client.put(
        "/admin/users/3",
        headers={"Authorization": "Bearer invalid.token.here"}
    )
    assert response.status_code == 401


def test_when_token_is_blacklisted_return_401(client, admin_token, mock_redis):
    """
    Token hợp lệ nhưng đã bị blacklist → 401
    """
    mock_redis.is_token_blacklisted.return_value = True

    response = client.put(
        "/admin/users/3",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 401


def test_when_non_admin_return_403(client, access_token):
    """
    Token hợp lệ nhưng user không phải admin → 403
    """
    response = client.put(
        "/admin/users/3",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 403
    data = response.get_json()
    assert data["code"] == "ADMIN_ACCESS_REQUIRED"


# ====== Test PUT Success ======

def test_success_return_200(client, admin_token, insert_users):
    """
    Cập nhật thông tin user thành công -> 200 OK và trả về thông tin user mới
    """
    response = client.put(
        "/admin/users/3",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "name": "updated_user_3",
            "email": "updated_user_3@example.com",
            "is_active": False
        }
    )
    assert response.status_code == 200
    
    data = response.get_json()
    assert data["name"] == "updated_user_3"
    assert data["email"] == "updated_user_3@example.com"
    assert data["is_active"] is False


# ====== Test Payload Validation ======

@pytest.mark.parametrize("payload", [
    {"email": "updated@example.com", "is_active": True},                    # Thiếu name
    {"name": "updated_name", "is_active": True},                            # Thiếu email
    {"name": "updated_name", "email": "updated@example.com"},               # Thiếu is_active
    {"name": "updated_name", "email": "invalid-email", "is_active": True},  # Email sai định dạng
    {},                                                                     # Payload trống
], ids=[
    "missing_name",
    "missing_email",
    "missing_is_active",
    "invalid_email_format",
    "empty_payload"
])
def test_when_invalid_payload_return_400(client, admin_token, mock_redis, payload):
    """
    Gửi payload không hợp lệ => 400 Bad Request, lỗi VALIDATION_ERROR và KHÔNG xóa cache
    """
    response = client.put(
        "/admin/users/3",
        headers={"Authorization": f"Bearer {admin_token}"},
        json=payload
    )
    assert response.status_code == 400
    data = response.get_json()
    assert data["code"] == "VALIDATION_ERROR"
    assert isinstance(data["error"], list)
    
    # Đảm bảo cache không bị xóa khi validation thất bại
    mock_redis.delete_pattern.assert_not_called()


# ====== Test Business Exceptions ======

def test_when_not_found_return_404(client, admin_token, mock_redis):
    """
    Cập nhật user không tồn tại trong hệ thống => 404 Not Found và KHÔNG xóa cache
    """
    response = client.put(
        "/admin/users/9999",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "name": "updated_name",
            "email": "updated@example.com",
            "is_active": True
        }
    )
    assert response.status_code == 404
    data = response.get_json()
    assert data["code"] == "USER_NOT_FOUND"  # Hoặc mã lỗi tương ứng
    mock_redis.delete_pattern.assert_not_called()


def test_when_name_exists_return_409(client, admin_token, mock_redis, insert_users):
    """
    Cập nhật tên trùng với một user khác đã tồn tại => 409 Conflict và KHÔNG xóa cache
    """
    response = client.put(
        "/admin/users/3",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "name": "user_1",  # Trùng tên với user_1
            "email": "updated_user_3@example.com",
            "is_active": True
        }
    )
    assert response.status_code == 409
    data = response.get_json()
    assert data["code"] == "DUPLICATE_NAME"
    mock_redis.delete_pattern.assert_not_called()


def test_when_email_exists_return_409(client, admin_token, mock_redis, insert_users):
    """
    Cập nhật email trùng với một user khác đã tồn tại => 409 Conflict và KHÔNG xóa cache
    """
    response = client.put(
        "/admin/users/3",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "name": "updated_user_3",
            "email": "user_1@example.com",  # Trùng email với user_1
            "is_active": True
        }
    )
    assert response.status_code == 409
    data = response.get_json()
    assert data["code"] == "DUPLICATE_EMAIL"
    mock_redis.delete_pattern.assert_not_called()


# ====== Test Cache Invalidation ======

def test_when_success_then_cache_is_invalidated(client, admin_token, mock_redis, insert_users):
    """
    Cập nhật user thành công => Xóa cache danh sách user
    """
    response = client.put(
        "/admin/users/3",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "name": "updated_user_3",
            "email": "updated_user_3@example.com",
            "is_active": True
        }
    )
    assert response.status_code == 200
    mock_redis.delete_pattern.assert_called_once_with("users:list:page=*:per_page=*")


# ====== Test Admin Self Disable / Lockout ======

def test_when_admin_tries_to_disable_self_return_403(client, admin_token, insert_users):
    """
    Admin tự khóa tài khoản của chính mình => 403 Forbidden và báo lỗi SELF_DISABLE_NOT_ALLOWED
    """
    response = client.put(
        "/admin/users/2",  # ID của admin_example là 2 (khớp với sub trong token)
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "name": "admin_1_updated",
            "email": "admin_1_updated@example.com",
            "is_active": False  # Tự khóa chính mình
        }
    )
    assert response.status_code == 403
    data = response.get_json()
    assert data["code"] == "SELF_DISABLE_NOT_ALLOWED"


def test_when_admin_updates_self_with_active_true_success(client, admin_token, insert_users):
    """
    Admin tự cập nhật thông tin của mình nhưng vẫn giữ is_active=True => Thành công 200 OK
    """
    response = client.put(
        "/admin/users/2",  # ID của admin_example là 2
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "name": "admin_updated_name",
            "email": "admin_updated_email@example.com",
            "is_active": True  # Vẫn hoạt động
        }
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["name"] == "admin_updated_name"
    assert data["email"] == "admin_updated_email@example.com"
    assert data["is_active"] is True


# ====== Test Admin Privilege Hierarchy ======

def test_when_admin_tries_to_update_another_admin_return_403(client, admin_token, insert_admins):
    """
    Admin cập nhật thông tin của admin khác => 403 Forbidden và báo lỗi PRIVILEGE_VIOLATION
    """
    response = client.put(
        "/admin/users/20",   # ID của admin
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "name": "admin_updated_name",
            "email": "admin_updated_email@example.com",
            "is_active": True  
        }
    )

    assert response.status_code == 403
    data = response.get_json()
    assert data["code"] == "PRIVILEGE_VIOLATION"