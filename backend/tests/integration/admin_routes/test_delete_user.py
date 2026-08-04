import pytest

# ====== Test Authorization & Authentication ======

def test_delete_user_when_no_token_return_401(client):
    """
    Không gửi token → 401
    """
    response = client.delete("/admin/users/3")
    assert response.status_code == 401


def test_delete_user_when_invalid_token_return_401(client):
    """
    Token không hợp lệ → 401
    """
    response = client.delete(
        "/admin/users/3",
        headers={"Authorization": "Bearer invalid.token.here"}
    )
    assert response.status_code == 401


def test_delete_user_when_token_is_blacklisted_return_401(client, admin_token, mock_redis):
    """
    Token hợp lệ nhưng đã bị blacklist → 401
    """
    mock_redis.is_token_blacklisted.return_value = True

    response = client.delete(
        "/admin/users/3",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 401


def test_delete_user_when_non_admin_return_403(client, access_token):
    """
    Token hợp lệ nhưng user không phải admin → 403
    """
    response = client.delete(
        "/admin/users/3",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 403
    data = response.get_json()
    assert data["code"] == "ADMIN_ACCESS_REQUIRED"


# ====== Test Delete User API Success & Business Rules ======

def test_delete_user_success_return_204(client, admin_token, insert_users):
    """
    Admin xóa mềm user thường thành công → 204 No Content
    """
    user_target = insert_users[2] # user_3 (is_admin=False)
    response = client.delete(
        f"/admin/users/{user_target.user_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 204


def test_delete_user_self_delete_return_403(client, admin_token):
    """
    Admin tự xóa tài khoản của chính mình → 403 (SELF_DISABLE_NOT_ALLOWED)
    """
    # admin_token thuộc về user_id=999
    response = client.delete(
        "/admin/users/999",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 403
    data = response.get_json()
    assert data["code"] == "SELF_DISABLE_NOT_ALLOWED"


def test_delete_user_other_admin_return_403(client, admin_token, insert_admins):
    """
    Admin xóa tài khoản của một Admin khác → 403 (PRIVILEGE_VIOLATION)
    """
    admin_target = insert_admins[0] # user_id=16, is_admin=True
    response = client.delete(
        f"/admin/users/{admin_target.user_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 403
    data = response.get_json()
    assert data["code"] == "PRIVILEGE_VIOLATION"


def test_delete_user_not_found_return_404(client, admin_token):
    """
    Xóa user_id không tồn tại → 404 (USER_NOT_FOUND)
    """
    response = client.delete(
        "/admin/users/99999",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 404
    data = response.get_json()
    assert data["code"] == "USER_NOT_FOUND"
