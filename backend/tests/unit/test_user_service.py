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
        return UserService(user=mock_user_repo)
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
