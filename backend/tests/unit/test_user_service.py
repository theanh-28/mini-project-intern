import pytest

from app.services.user_service import UserService
from app.repositories.user_repository import UserRepository

@pytest.fixture
def make_user_service(mocker, user_example):
    """
    Tạo đối tượng UserService
    """
    def _make(is_none=False):
        mock_user_repo = mocker.MagicMock()
        mock_user_repo.get_by_email.return_value = user_example if not is_none else None
        return UserService(user_repository=mock_user_repo)
    return _make

def test_auth_user_success(make_user_service, user_example):
    """
    Test trường hợp xác thực thành công khi truyền đúng email + password
    """
    user_service = make_user_service(is_none=False)
    user, error = user_service.auth_user(email=user_example.email, password="123456")

    assert error is None
    assert user == user_example

def test_auth_user_email_not_found(make_user_service):
    """
    Test trường hợp truyền vào email không tồn tại
    """
    user_service = make_user_service(is_none=True)
    user, error = user_service.auth_user(email="user_1@example.com", password="123456")

    assert user is None
    assert error == "Email không tồn tại"

def test_auth_user_wrong_password(make_user_service, user_example):
    """
    Test trường hợp nhập sai mật khẩu
    """
    user_service = make_user_service(is_none=False)
    user, error = user_service.auth_user(email=user_example.email, password="wrong_password")

    assert user is None
    assert error == "Sai mật khẩu"

def test_auth_user_inactive_account(make_user_service, user_example):
    """
    Test trường hợp tài khoản bị khóa (is_active = False)
    """
    user_example.is_active = False
    user_service = make_user_service(is_none=False)
    user, error = user_service.auth_user(email=user_example.email, password="123456")

    assert user is None
    assert error == "Tài khoản đang bị khóa"

def test_auth_user_calls_update_last_login_and_commit(make_user_service, user_example):
    """
    Test trường hợp xác thực thành công sẽ gọi update_last_login và commit
    """
    user_service = make_user_service(is_none=False)
    user, error = user_service.auth_user(email=user_example.email, password="123456")

    assert error is None
    assert user == user_example
    user_service.user_repository.update_last_login.assert_called_once_with(user_example)
    user_service.user_repository.commit.assert_called_once()

def test_auth_user_does_not_commit_on_failure(make_user_service, user_example):
    """
    Test trường hợp xác thực thất bại không gọi commit
    """
    # 1. Sai email
    user_service_1 = make_user_service(is_none=True)
    user_service_1.auth_user(email="nonexistent@example.com", password="123")
    user_service_1.user_repository.commit.assert_not_called()

    # 2. Sai mật khẩu
    user_service_2 = make_user_service(is_none=False)
    user_service_2.auth_user(email=user_example.email, password="wrong_password")
    user_service_2.user_repository.commit.assert_not_called()

    # 3. Tài khoản bị khóa
    user_example.is_active = False
    user_service_3 = make_user_service(is_none=False)
    user_service_3.auth_user(email=user_example.email, password="123456")
    user_service_3.user_repository.commit.assert_not_called()
    user_example.is_active = True


