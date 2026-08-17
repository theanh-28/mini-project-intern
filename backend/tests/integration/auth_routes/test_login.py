import pytest

from app.models import User
from app.core.security import hash_password


def test_login_when_credentials_is_valid_return_200_and_token(client, insert_user):
    """
    Trường hợp xác thực thành công
    Trả về status code 200 và jwt đúng
    """
    response = client.post(
        '/auth/login',
        json={
            'email': insert_user.email,
            'password': '123456'
        }
    )

    data = response.get_json()

    assert response.status_code == 200
    assert 'access_token' in data
    assert data['user']['user_id'] == insert_user.user_id
    assert data['user']['name'] == insert_user.name
    assert data['user']['email'] == insert_user.email
    assert 'user' in data['user']['roles']
    assert data['user']['permissions'] == []


def test_login_when_user_is_admin_return_200_and_admin_role(client, insert_admin):
    """
    Trường hợp admin login thành công, kiểm tra role admin và full permissions trong response
    """
    response = client.post(
        '/auth/login',
        json={
            'email': insert_admin.email,
            'password': '123456'
        }
    )

    data = response.get_json()

    assert response.status_code == 200
    assert 'access_token' in data
    assert data['user']['user_id'] == insert_admin.user_id
    assert data['user']['name'] == insert_admin.name
    assert data['user']['email'] == insert_admin.email
    assert 'admin' in data['user']['roles']
    assert 'users:read' in data['user']['permissions']
    assert 'users:delete' in data['user']['permissions']


def test_login_when_email_is_incorrect_return_401(client):
    """
    Trường hợp xác thực thất bại vì email sai (chống user enumeration)
    Trả về status code 401 và mã lỗi INVALID_CREDENTIALS
    """
    response = client.post(
        '/auth/login',
        json={
            'email': 'abc@example.com',
            'password': '123'
        }
    )

    data = response.get_json()
    assert response.status_code == 401
    assert data['code'] == "INVALID_CREDENTIALS"


def test_login_when_password_is_incorrect_return_401(client, insert_user):
    """
    Trường hợp đúng email nhưng sai password
    Trả về status code 401 và mã lỗi INVALID_CREDENTIALS
    """
    response = client.post(
        '/auth/login',
        json={
            'email': insert_user.email,
            'password': '123'
        }
    )

    data = response.get_json()
    assert response.status_code == 401
    assert data['code'] == "INVALID_CREDENTIALS"


@pytest.mark.parametrize('payload', [
    {"email": "abc@example.com"},
    {"password": "123"},
    {"email": "abc", "password": "123"},
    {},
])
def test_login_when_request_is_invalid_return_400(client, payload):
    """
    Trường hợp nhập sai định dạng
    Trả về status code 400
    """
    response = client.post(
        '/auth/login',
        json=payload,
    )

    assert response.status_code == 400


def test_login_when_user_is_inactive_return_403(client, db_session):
    """
    Trường hợp tài khoản bị khóa (is_active=False)
    Trả về status code 403
    """
    user_inactive = User(
        user_id=1,
        name="user_1",
        email="user_1@example.com",
        password=hash_password("123456"),
        is_active=False
    )

    db_session.add(user_inactive)
    db_session.commit()
    db_session.refresh(user_inactive)

    response = client.post(
        '/auth/login',
        json={
            "email": user_inactive.email,
            "password": "123456"
        }
    )

    assert response.status_code == 403


def test_login_when_no_body_return_400(client):
    """
    Trường hợp gửi request login không có body (JSON payload)
    """
    response = client.post(
        '/auth/login',
        headers={"Content-Type": "application/json"}
    )
    assert response.status_code == 400


def test_login_when_credentials_is_valid_updates_last_login_in_db(client, db_session, insert_user):
    """
    Trường hợp login thành công, verify last_login trong database được cập nhật
    """
    assert insert_user.last_login is None

    response = client.post(
        '/auth/login',
        json={
            'email': insert_user.email,
            'password': '123456'
        }
    )
    assert response.status_code == 200

    db_session.refresh(insert_user)
    assert insert_user.last_login is not None


def test_login_when_user_is_soft_deleted_return_401(client, db_session):
    """
    Trường hợp tài khoản đã bị xóa mềm (deleted_at IS NOT NULL)
    Trả về status code 401 (coi như không tồn tại thông tin đăng nhập hợp lệ)
    """
    from datetime import datetime, timezone
    deleted_user = User(
        name="deleted_user",
        email="deleted@example.com",
        password=hash_password("123456"),
        is_active=True,
        deleted_at=datetime.now(timezone.utc)
    )
    db_session.add(deleted_user)
    db_session.commit()

    response = client.post(
        '/auth/login',
        json={
            'email': deleted_user.email,
            'password': '123456'
        }
    )
    data = response.get_json()
    assert response.status_code == 401
    assert data['code'] == "INVALID_CREDENTIALS"


def test_login_when_must_change_password_is_true_returns_notice_and_no_jwt(client, db_session, mock_redis):
    """
    Trường hợp user có must_change_password=True:
    Trả về HTTP 200, require_password_change=True, KHÔNG cấp access_token và gửi link qua Email.
    """
    from app.core.extensions import mail

    new_user = User(
        name="must_change_user",
        email="force_change@example.com",
        password=hash_password("123456"),
        is_active=True,
        must_change_password=True,
    )
    db_session.add(new_user)
    db_session.commit()

    with mail.record_messages() as out:
        response = client.post(
            '/auth/login',
            json={
                'email': new_user.email,
                'password': '123456'
            }
        )

        data = response.get_json()
        assert response.status_code == 200
        assert data.get("require_password_change") is True
        assert "access_token" not in data
        assert "reset_url" not in data  # Không để lộ reset_url trong HTTP body
        assert "đặt lại mật khẩu" in data.get("message", "")

        # Kiểm tra email thực sự được gửi tới hòm thư cá nhân của user
        assert len(out) == 1
        assert out[0].recipients == [new_user.email]
        assert "/reset-password?token=" in out[0].body

