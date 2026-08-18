import pytest

# ====== Test Authorization ======

def test_when_no_token_return_401(client):
    """
    Không gửi token → 401 Unauthorized
    """
    response = client.post("/admin/users/1/reset-password")
    assert response.status_code == 401


def test_when_invalid_token_return_401(client):
    """
    Token không hợp lệ → 401 Unauthorized
    """
    response = client.post(
        "/admin/users/1/reset-password",
        headers={"Authorization": "Bearer invalid.token.string"}
    )
    assert response.status_code == 401


def test_when_token_is_blacklisted_return_401(client, admin_token, mock_redis):
    """
    Token hợp lệ nhưng bị blacklist → 401 Unauthorized
    """
    mock_redis.is_token_blacklisted.return_value = True

    response = client.post(
        "/admin/users/1/reset-password",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 401


def test_when_non_admin_return_403(client, access_token):
    """
    User thường không có quyền users:update → 403 Forbidden
    """
    response = client.post(
        "/admin/users/1/reset-password",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 403
    data = response.get_json()
    assert data["code"] == "PERMISSION_DENIED"


# ====== Test Success & Business Exceptions ======

def test_admin_reset_password_success_return_200(client, admin_token, insert_users, mock_redis):
    """
    Admin yêu cầu đặt lại mật khẩu cho User thành công:
    - Trả về 200 OK
    - Lưu reset token vào Redis
    - Thu hồi các session JWT cũ của user
    """
    target_user = insert_users[0] # user_1

    response = client.post(
        f"/admin/users/{target_user.user_id}/reset-password",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.get_json()
    assert "message" in data

    assert target_user.must_change_password is True
    mock_redis.save_reset_token.assert_called_once()
    mock_redis.revoke_user_sessions.assert_called_once()


def test_admin_reset_password_when_user_not_found_return_404(client, admin_token):
    """
    User không tồn tại → 404 Not Found
    """
    response = client.post(
        "/admin/users/9999/reset-password",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 404
    data = response.get_json()
    assert data["code"] == "USER_NOT_FOUND"


def test_admin_reset_password_when_target_is_admin_return_403(client, admin_token, insert_admins):
    """
    Admin cố gắng reset mật khẩu của một Admin khác → 403 Forbidden (PRIVILEGE_VIOLATION)
    """
    admin_target = insert_admins[0]

    response = client.post(
        f"/admin/users/{admin_target.user_id}/reset-password",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 403
    data = response.get_json()
    assert data["code"] == "PRIVILEGE_VIOLATION"


def test_admin_reset_password_when_user_locked_return_403(client, admin_token, insert_users, db_session):
    """
    User đang bị khóa (is_active=False) → 403 Forbidden (ACCOUNT_LOCKED)
    """
    target_user = insert_users[2]
    target_user.is_active = False
    db_session.commit()

    response = client.post(
        f"/admin/users/{target_user.user_id}/reset-password",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 403
    data = response.get_json()
    assert data["code"] == "ACCOUNT_LOCKED"
