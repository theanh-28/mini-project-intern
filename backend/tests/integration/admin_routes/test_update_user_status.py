import pytest

# ====== Test Authorization ======

def test_when_no_token_return_401(client):
    """
    Không gửi token → 401
    """
    response = client.patch("/admin/users/3/status")
    assert response.status_code == 401


def test_when_invalid_token_return_401(client):
    """
    Token không hợp lệ → 401
    """
    response = client.patch(
        "/admin/users/3/status",
        headers={"Authorization": "Bearer invalid.token.here"}
    )
    assert response.status_code == 401


def test_when_token_is_blacklisted_return_401(client, admin_token, mock_redis):
    """
    Token hợp lệ nhưng đã bị blacklist → 401
    """
    mock_redis.is_token_blacklisted.return_value = True

    response = client.patch(
        "/admin/users/3/status",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 401


def test_when_non_admin_return_403(client, access_token):
    """
    Token hợp lệ nhưng user không có quyền users:update → 403
    """
    response = client.patch(
        "/admin/users/3/status",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 403
    data = response.get_json()
    assert data["code"] == "PERMISSION_DENIED"


# ====== Test PATCH Status Success ======

def test_success_update_status_return_200(client, admin_token, insert_users):
    """
    Cập nhật trạng thái user thành công -> 200 OK
    """
    response = client.patch(
        "/admin/users/3/status",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"is_active": False}
    )
    assert response.status_code == 200
    
    data = response.get_json()
    assert data["user_id"] == 3
    assert data["is_active"] is False


# ====== Test Payload Validation ======

@pytest.mark.parametrize("payload", [
    {},                           # Thiếu is_active
    {"is_active": "invalid_bool"},# Sai kiểu dữ liệu
    {"is_active": True, "extra": 1}, # Trường lạ
], ids=[
    "missing_is_active",
    "invalid_type",
    "extra_field"
])
def test_when_invalid_payload_return_400(client, admin_token, mock_redis, payload):
    """
    Gửi payload không hợp lệ => 400 Bad Request
    """
    response = client.patch(
        "/admin/users/3/status",
        headers={"Authorization": f"Bearer {admin_token}"},
        json=payload
    )
    assert response.status_code == 400
    data = response.get_json()
    assert data["code"] == "VALIDATION_ERROR"
    mock_redis.delete_pattern.assert_not_called()


# ====== Test Business Exceptions ======

def test_when_not_found_return_404(client, admin_token, mock_redis):
    """
    Cập nhật trạng thái user không tồn tại => 404 Not Found
    """
    response = client.patch(
        "/admin/users/9999/status",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"is_active": False}
    )
    assert response.status_code == 404
    data = response.get_json()
    assert data["code"] == "USER_NOT_FOUND"


def test_when_admin_tries_to_disable_self_return_403(client, admin_token, db_session, admin_example):
    """
    Admin tự khóa chính mình => 403 Forbidden
    """
    from app.models.role import Role
    admin_role = db_session.query(Role).filter(Role.code == "admin").first()
    admin_example.roles = [admin_role] if admin_role else []
    db_session.add(admin_example)
    db_session.commit()

    response = client.patch(
        "/admin/users/999/status",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"is_active": False}
    )
    assert response.status_code == 403
    data = response.get_json()
    assert data["code"] == "SELF_DISABLE_NOT_ALLOWED"


def test_when_admin_tries_to_update_another_admin_status_return_403(client, admin_token, insert_admins):
    """
    Admin đổi trạng thái của admin khác => 403 Forbidden
    """
    response = client.patch(
        "/admin/users/20/status",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"is_active": False}
    )
    assert response.status_code == 403
    data = response.get_json()
    assert data["code"] == "PRIVILEGE_VIOLATION"


def test_update_status_to_inactive_calls_redis_revocation(client, admin_token, insert_users, mock_redis):
    """
    Khi admin khóa tài khoản (is_active=False), hệ thống phải thu hồi token trên Redis
    """
    response = client.patch(
        "/admin/users/3/status",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"is_active": False}
    )
    assert response.status_code == 200
    mock_redis.revoke_user_sessions.assert_called_once_with(user_id=3, ttl=3600)


def test_when_success_then_cache_is_invalidated(client, admin_token, mock_redis, insert_users):
    """
    Đổi trạng thái thành công => Xóa cache danh sách user
    """
    response = client.patch(
        "/admin/users/3/status",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"is_active": False}
    )
    assert response.status_code == 200
    mock_redis.delete_pattern.assert_called_once_with("users:list:*")


def test_when_status_unchanged_return_200(client, admin_token, mock_redis, insert_users):
    """
    Khi gửi trạng thái không đổi (đang True gửi tiếp True), trả về 200 OK ngay mà không gọi thu hồi session
    """
    response = client.patch(
        "/admin/users/3/status",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"is_active": True}
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["user_id"] == 3
    assert data["is_active"] is True
    mock_redis.revoke_user_sessions.assert_not_called()
