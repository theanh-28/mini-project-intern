import pytest

# ====== Test Authorization ======

def test_when_no_token_return_401(client):
    """
    Không gửi token → 401 Unauthorized
    """
    response = client.get("/admin/users/1")
    assert response.status_code == 401


def test_when_invalid_token_return_401(client):
    """
    Gửi token không hợp lệ → 401 Unauthorized
    """
    response = client.get(
        "/admin/users/1",
        headers={"Authorization": "Bearer invalid.token.value"}
    )
    assert response.status_code == 401


def test_when_token_is_blacklisted_return_401(client, admin_token, mock_redis):
    """
    Token hợp lệ nhưng đã bị blacklist trên Redis → 401 Unauthorized
    """
    mock_redis.is_token_blacklisted.return_value = True

    response = client.get(
        "/admin/users/1",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 401


def test_when_non_admin_return_403(client, access_token):
    """
    User thường (role user, không có quyền users:read) → 403 Forbidden
    """
    response = client.get(
        "/admin/users/1",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 403
    data = response.get_json()
    assert data["code"] == "PERMISSION_DENIED"


# ====== Test Success & Business Exceptions ======

def test_get_user_detail_success_return_200(client, admin_token, insert_users):
    """
    Lấy thông tin chi tiết user thành công → 200 OK kèm dữ liệu UserResponse
    """
    target_user = insert_users[0] # user_1

    response = client.get(
        f"/admin/users/{target_user.user_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.get_json()

    assert data["user_id"] == target_user.user_id
    assert data["name"] == target_user.name
    assert data["email"] == target_user.email
    assert data["is_active"] is True
    assert "roles" in data
    assert "user" in data["roles"]
    assert "created_at" in data


def test_when_user_not_found_return_404(client, admin_token):
    """
    User ID không tồn tại trong hệ thống → 404 Not Found
    """
    response = client.get(
        "/admin/users/9999",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 404
    data = response.get_json()
    assert data["code"] == "USER_NOT_FOUND"


def test_when_user_is_soft_deleted_return_404(client, admin_token, insert_users, db_session):
    """
    User đã bị xóa mềm (deleted_at IS NOT NULL) → coi như không tồn tại → 404 Not Found
    """
    from datetime import datetime, timezone
    target_user = insert_users[1]
    target_user.deleted_at = datetime.now(timezone.utc)
    db_session.commit()

    response = client.get(
        f"/admin/users/{target_user.user_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 404
    data = response.get_json()
    assert data["code"] == "USER_NOT_FOUND"
