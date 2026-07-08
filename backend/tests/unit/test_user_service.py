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
        mock_redis = mocker.MagicMock()
        return UserService(user_repository=mock_user_repo, redis_service=mock_redis)
    return _make

def test_auth_user_success(make_user_service, user_example):
    """
    Test trường hợp xác thực thành công khi truyền đúng email + password
    """
    user_service = make_user_service(is_none=False)
    user = user_service.auth_user(email=user_example.email, password="123456")

    assert user == user_example

def test_auth_user_email_not_found(make_user_service):
    """
    Test trường hợp truyền vào email không tồn tại
    """
    from app.core.exceptions import EmailNotFoundError
    user_service = make_user_service(is_none=True)
    with pytest.raises(EmailNotFoundError) as excinfo:
        user_service.auth_user(email="user_1@example.com", password="123456")
    assert str(excinfo.value) == "Email không tồn tại"

def test_auth_user_wrong_password(make_user_service, user_example):
    """
    Test trường hợp nhập sai mật khẩu
    """
    from app.core.exceptions import WrongPasswordError
    user_service = make_user_service(is_none=False)
    with pytest.raises(WrongPasswordError) as excinfo:
        user_service.auth_user(email=user_example.email, password="wrong_password")
    assert str(excinfo.value) == "Mật khẩu không đúng"

def test_auth_user_inactive_account(make_user_service, user_example):
    """
    Test trường hợp tài khoản bị khóa (is_active = False)
    """
    from app.core.exceptions import AccountLockedError
    user_example.is_active = False
    user_service = make_user_service(is_none=False)
    with pytest.raises(AccountLockedError) as excinfo:
        user_service.auth_user(email=user_example.email, password="123456")
    assert str(excinfo.value) == "Tài khoản đang bị khóa"

def test_auth_user_calls_update_last_login(make_user_service, user_example):
    """
    Test trường hợp xác thực thành công sẽ gọi update_last_login
    """
    user_service = make_user_service(is_none=False)
    user = user_service.auth_user(email=user_example.email, password="123456")

    assert user == user_example
    user_service.user_repository.update_last_login.assert_called_once_with(user_example)

def test_auth_user_does_not_commit_on_failure(make_user_service, user_example):
    """
    Test trường hợp xác thực thất bại không gọi ghi đè thông tin đăng nhập
    """
    from app.core.exceptions import EmailNotFoundError, WrongPasswordError, AccountLockedError

    # 1. Sai email
    user_service_1 = make_user_service(is_none=True)
    with pytest.raises(EmailNotFoundError):
        user_service_1.auth_user(email="nonexistent@example.com", password="123")
    user_service_1.user_repository.update_last_login.assert_not_called()

    # 2. Sai mật khẩu
    user_service_2 = make_user_service(is_none=False)
    with pytest.raises(WrongPasswordError):
        user_service_2.auth_user(email=user_example.email, password="wrong_password")
    user_service_2.user_repository.update_last_login.assert_not_called()

    # 3. Tài khoản bị khóa
    user_example.is_active = False
    user_service_3 = make_user_service(is_none=False)
    with pytest.raises(AccountLockedError):
        user_service_3.auth_user(email=user_example.email, password="123456")
    user_service_3.user_repository.update_last_login.assert_not_called()
    user_example.is_active = True


def test_logout_user_success(mocker):
    """
    Test trường hợp gọi logout_user thành công đưa token vào blacklist
    """
    from datetime import datetime, timezone
    mock_user_repo = mocker.MagicMock()
    mock_redis_service = mocker.MagicMock()
    
    user_service = UserService(user_repository=mock_user_repo, redis_service=mock_redis_service)
    
    # 1. Trường hợp token chưa hết hạn (exp > now)
    future_exp = datetime.now(timezone.utc).timestamp() + 100
    user_service.logout_user(jti="test_jti", exp=future_exp)
    mock_redis_service.blacklist_token.assert_called_once()
    
    # 2. Trường hợp token đã hết hạn (exp <= now)
    mock_redis_service.reset_mock()
    past_exp = datetime.now(timezone.utc).timestamp() - 100
    user_service.logout_user(jti="test_jti_expired", exp=past_exp)
    mock_redis_service.blacklist_token.assert_not_called()