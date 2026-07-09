import json
import math

import pytest


# ====== Test Authorization ======

def test_get_users_when_no_token_return_401(client):
    """
    Không gửi token → 401
    """
    response = client.get("/admin/users")
    assert response.status_code == 401


def test_get_users_when_invalid_token_return_401(client):
    """
    Token không hợp lệ → 401
    """
    response = client.get(
        "/admin/users",
        headers={"Authorization": "Bearer invalid.token.here"}
    )
    assert response.status_code == 401


def test_get_users_when_token_is_blacklisted_return_401(client, admin_token, mock_redis):
    """
    Token hợp lệ nhưng đã bị blacklist → 401
    """
    mock_redis.is_token_blacklisted.return_value = True

    response = client.get(
        "/admin/users",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 401


def test_get_users_when_non_admin_return_403(client, access_token, insert_users):
    """
    Token hợp lệ nhưng user không phải admin → 403
    """
    response = client.get(
        "/admin/users",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 403
    data = response.get_json()
    assert data["code"] == "ADMIN_ACCESS_REQUIRED"


def test_get_users_when_admin_return_200(client, admin_token, insert_users):
    """
    Admin token hợp lệ → 200
    """
    response = client.get(
        "/admin/users",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200


# ====== Test Query Params Validation ======

@pytest.mark.parametrize("params", [
    {"page": 0},          # page < 1
    {"per_page": 0},      # per_page < 1
    {"per_page": 101},    # per_page > 100
    {"page": "abc"},      # sai kiểu
    {"per_page": "xyz"},  # sai kiểu
])
def test_get_users_when_invalid_params_return_400(client, admin_token, params):
    """
    Query params không hợp lệ → 400
    """
    response = client.get(
        "/admin/users",
        query_string=params,
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 400


def test_get_users_when_no_params_use_defaults_return_200(client, admin_token):
    """
    Không truyền page/per_page → dùng default (page=1, per_page=20) → 200
    """
    response = client.get(
        "/admin/users",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["page"] == 1
    assert data["per_page"] == 20


# ====== Test Response Structure ======

def test_get_users_response_has_pagination_metadata(client, admin_token, insert_users):
    """
    Response phải có đầy đủ: users, total, page, per_page, total_pages
    """
    response = client.get(
        "/admin/users",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    data = response.get_json()

    assert "users" in data
    assert "total" in data
    assert "page" in data
    assert "per_page" in data
    assert "total_pages" in data


def test_get_users_total_pages_calculated_correctly(client, admin_token, insert_users):
    """
    Kiểm tra total_pages = ceil(total / per_page)
    15 users, per_page=10 → total_pages=2
    """
    response = client.get(
        "/admin/users",
        query_string={"page": 1, "per_page": 10},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    data = response.get_json()

    assert data["total"] == 15
    assert data["per_page"] == 10
    assert data["total_pages"] == math.ceil(15 / 10)  # 2


def test_get_users_pagination_limits_results(client, admin_token, insert_users):
    """
    per_page=5 → chỉ trả về 5 user mỗi trang
    """
    response = client.get(
        "/admin/users",
        query_string={"page": 1, "per_page": 5},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    data = response.get_json()

    assert len(data["users"]) == 5
    assert data["page"] == 1
    assert data["per_page"] == 5


def test_get_users_when_empty_db_return_zero_total_pages(client, admin_token):
    """
    Không có user nào trong DB → total=0, total_pages=0
    """
    response = client.get(
        "/admin/users",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    data = response.get_json()

    assert data["total"] == 0
    assert data["total_pages"] == 0
    assert data["users"] == []


def test_get_users_page_2_returns_remaining_users(client, admin_token, insert_users):
    """
    15 users, per_page=10:
    - page=1 → 10 users
    - page=2 → 5 users còn lại
    """
    response = client.get(
        "/admin/users",
        query_string={"page": 2, "per_page": 10},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    data = response.get_json()

    assert response.status_code == 200
    assert len(data["users"]) == 5
    assert data["page"] == 2


# ====== Test Caching ======

def test_get_users_when_subsequent_request_return_cached_response(client, admin_token, insert_users, mock_redis, mocker):
    """
    Lần đầu gọi → Cache Miss (truy cập DB) → Lần hai gọi → Cache Hit (lấy từ Redis, không truy cập DB)
    
    """
    from app.services.user_service import UserService

    spy_get_list = mocker.spy(UserService, "get_list_user")

    # Lần 1: Giả lập cache miss
    mock_redis.get.return_value = None

    response1 = client.get(
        "/admin/users",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response1.status_code == 200
    assert spy_get_list.call_count == 1

    # Lần 2: Giả lập cache hit
    cached_data = {
        "data": response1.get_data(as_text=True),
        "status_code": 200,
        "content_type": "application/json"
    }
    mock_redis.get.return_value = json.dumps(cached_data)

    response2 = client.get(
        "/admin/users",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response2.status_code == 200
    assert response2.get_json() == response1.get_json()
    assert spy_get_list.call_count == 1  # Vẫn là 1, không gọi lại DB/Service


def test_get_users_when_different_pages_return_different_cache_keys(client, admin_token, insert_users, mock_redis):
    """
    Gọi các trang khác nhau → Sử dụng các cache key khác nhau (không bị đè)
    """
    # Lần 1: page 1
    client.get(
        "/admin/users",
        query_string={"page": 1},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    called_args_page1 = mock_redis.set.call_args[0]
    assert "page=1" in called_args_page1[0]

    # Lần 2: page 2
    client.get(
        "/admin/users",
        query_string={"page": 2},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    called_args_page2 = mock_redis.set.call_args[0]
    assert "page=2" in called_args_page2[0]

    # 2 cache key phải khác nhau
    assert called_args_page1[0] != called_args_page2[0]


def test_get_users_when_response_is_error_does_not_cache(client, access_token, mock_redis):
    """
    Response lỗi (ví dụ: 403 Forbidden do token thường) → Không lưu vào Redis cache
    """
    response = client.get(
        "/admin/users",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 403

    mock_redis.set.assert_not_called()


def test_get_users_when_non_admin_and_cache_exists_return_403(client, access_token, mock_redis):
    """
    Trường hợp cache đang có sẵn dữ liệu (do admin gọi trước đó),
    nhưng user thường truy cập → vẫn phải trả về 403 và KHÔNG được lấy dữ liệu từ cache.
    """
    cached_data = {
        "data": json.dumps({"users": [], "total": 0}),
        "status_code": 200,
        "content_type": "application/json"
    }
    mock_redis.get.return_value = json.dumps(cached_data)

    response = client.get(
        "/admin/users",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    
    assert response.status_code == 403
    data = response.get_json()
    assert data["code"] == "ADMIN_ACCESS_REQUIRED"

    mock_redis.get.assert_not_called()

