import pytest

from app.models import User
from app.core.security import hash_password

@pytest.fixture
def insert_user(db_session, user_example):
    """
    Thêm user_example vào db
    """
    db_session.add(user_example)
    db_session.commit()

    return user_example

@pytest.fixture
def insert_admin(db_session, admin_example):
    """
    Thêm admin_example vào db
    """
    db_session.add(admin_example)
    db_session.commit()
    return admin_example

def test_login_when_credentials_is_valid_return_200_and_token(client, insert_user):
    """
    Trường hợp xác thực thành công
    Trả về status code 200 và jwt đúng
    """
    response = client.post(
        '/auth/login',
        json = {
            'email': insert_user.email,
            'password': '123456'
        }
    )

    data = response.get_json()

    assert response.status_code == 200
    assert 'access_token' in data
    assert data['is_admin'] is False

def test_login_when_user_is_admin_return_200_and_is_admin_true(client, insert_admin):
    """
    Trường hợp admin login thành công, kiểm tra is_admin=True trong response
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
    assert data['is_admin'] is True


def test_login_when_email_is_incorrect_return_404(client):
    """
    Trường hợp xác thực thất bại vì email sai
    Trả về status code 404
    """
    response = client.post(
        '/auth/login',
        json = {
            'email': 'abc@example.com',
            'password': '123'
        }
    )

    assert response.status_code == 404

def test_login_when_password_is_incorrect_return_401(client, insert_user):
    """
    Trường hợp đúng email nhưng sai password
    Trả về status code 401
    """
    response = client.post(
        '/auth/login',
        json = {
            'email': insert_user.email,
            'password': '123'
        }
    )

    assert response.status_code == 401

@pytest.mark.parametrize('payload',
                         [
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
        json = payload,
    )

    assert response.status_code == 400 

def test_login_when_user_is_inactive_return_403(client, db_session):
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
        json = {
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


def test_logout_when_token_is_valid_return_200_and_blacklists_token(client, access_token, mock_redis):
    """
    Trường hợp token hợp lệ, đăng xuất thành công và đưa token vào blacklist
    """
    response = client.post(
        '/auth/logout',
        headers={"Authorization": f"Bearer {access_token}"}
    )
    
    assert response.status_code == 200
    data = response.get_json()
    assert data["message"] == "Đăng xuất thành công"
    mock_redis.blacklist_token.assert_called_once()


def test_logout_when_no_token_return_401(client):
    """
    Trường hợp không gửi token kèm theo khi gọi logout
    """
    response = client.post(
        '/auth/logout'
    )
    
    assert response.status_code == 401


def test_logout_when_token_is_blacklisted_return_401(client, access_token, mock_redis):
    """
    Trường hợp gửi token đã bị blacklist từ trước khi logout
    """
    mock_redis.is_token_blacklisted.return_value = True
    
    response = client.post(
        '/auth/logout',
        headers={"Authorization": f"Bearer {access_token}"}
    )
    
    assert response.status_code == 401




