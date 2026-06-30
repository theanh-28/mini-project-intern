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

def test_login_when_credentials_is_valid_return_200_and_token(client, insert_user):
    """
    Trường hợp xác thực thông công
    Trả và status code 200 và jwt đúng
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

def test_login_when_email_is_incorrect_return_401(client):
    """
    Trường hợp xác thực thất bại vì email sai
    Trả về status code 401
    """
    response = client.post(
        '/auth/login',
        json = {
            'email': 'abc@example.com',
            'password': '123'
        }
    )

    assert response.status_code == 401

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