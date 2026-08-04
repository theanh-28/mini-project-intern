import pytest

# ====== Test Authorization & Authentication ======

def test_restore_user_when_no_token_return_401(client):
    """
    Không gửi token → 401
    """
    response = client.post("/admin/users/3/restore")
    assert response.status_code == 401


def test_restore_user_when_invalid_token_return_401(client):
    """
    Token không hợp lệ → 401
    """
    response = client.post(
        "/admin/users/3/restore",
        headers={"Authorization": "Bearer invalid.token.here"}
    )
    assert response.status_code == 401


def test_restore_user_when_token_is_blacklisted_return_401(client, admin_token, mock_redis):
    """
    Token hợp lệ nhưng đã bị blacklist → 401
    """
    mock_redis.is_token_blacklisted.return_value = True

    response = client.post(
        "/admin/users/3/restore",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 401


def test_restore_user_when_non_admin_return_403(client, access_token):
    """
    Token hợp lệ nhưng user không phải admin → 403
    """
    response = client.post(
        "/admin/users/3/restore",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 403
    data = response.get_json()
    assert data["code"] == "ADMIN_ACCESS_REQUIRED"


# ====== Test Restore User API Success & Business Rules ======

def test_restore_user_success_return_204(client, admin_token, insert_users):
    """
    Admin khôi phục user thường bị xóa mềm thành công → 204 No Content
    """
    user_target = insert_users[2] # user_3
    response = client.post(
        f"/admin/users/{user_target.user_id}/restore",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 204


def test_restore_user_self_restore_return_403(client, admin_token):
    """
    Admin tự khôi phục tài khoản của chính mình → 403 (SELF_RESTORE_NOT_ALLOWED)
    """
    # admin_token thuộc về user_id=999
    response = client.post(
        "/admin/users/999/restore",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 403
    data = response.get_json()
    assert data["code"] == "SELF_RESTORE_NOT_ALLOWED"


def test_restore_user_other_admin_return_403(client, admin_token, insert_admins):
    """
    Admin khôi phục tài khoản của một Admin khác → 403 (PRIVILEGE_VIOLATION)
    """
    admin_target = insert_admins[0] # user_id=16, is_admin=True
    response = client.post(
        f"/admin/users/{admin_target.user_id}/restore",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 403
    data = response.get_json()
    assert data["code"] == "PRIVILEGE_VIOLATION"


def test_restore_user_not_found_return_404(client, admin_token):
    """
    Khôi phục user_id không tồn tại → 404 (USER_NOT_FOUND)
    """
    response = client.post(
        "/admin/users/99999/restore",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 404
    data = response.get_json()
    assert data["code"] == "USER_NOT_FOUND"
