import pytest

from app.services.user_service import UserService
from app.repositories.user_repository import UserRepository


@pytest.fixture
def make_user_service(mocker):
    """
    Factory fixture tạo UserService với mock linh hoạt.
    Nhận **repo_overrides để cấu hình return_value cho từng method của user_repository.
    """
    def _make(**repo_overrides):
        mock_user_repo = mocker.MagicMock()
        for method, return_value in repo_overrides.items():
            getattr(mock_user_repo, method).return_value = return_value
        mock_redis = mocker.MagicMock()
        return UserService(user_repository=mock_user_repo, redis_service=mock_redis)
    return _make


# ======    TEST HÀM AUTH_USER  ======

def test_auth_user_success(make_user_service, user_example):
    """
    Test trường hợp xác thực thành công khi truyền đúng email + password
    """
    user_service = make_user_service(get_by_email=user_example)
    user = user_service.auth_user(email=user_example.email, password="123456")

    assert user == user_example

def test_auth_user_email_not_found(make_user_service):
    """
    Test trường hợp truyền vào email không tồn tại
    """
    from app.core.exceptions import EmailNotFoundError
    user_service = make_user_service(get_by_email=None)
    with pytest.raises(EmailNotFoundError) as excinfo:
        user_service.auth_user(email="user_1@example.com", password="123456")
    assert str(excinfo.value) == "Email không tồn tại"

def test_auth_user_wrong_password(make_user_service, user_example):
    """
    Test trường hợp nhập sai mật khẩu
    """
    from app.core.exceptions import WrongPasswordError
    user_service = make_user_service(get_by_email=user_example)
    with pytest.raises(WrongPasswordError) as excinfo:
        user_service.auth_user(email=user_example.email, password="wrong_password")
    assert str(excinfo.value) == "Mật khẩu không đúng"

def test_auth_user_inactive_account(make_user_service, user_example):
    """
    Test trường hợp tài khoản bị khóa (is_active = False)
    """
    from app.core.exceptions import AccountLockedError
    user_example.is_active = False
    user_service = make_user_service(get_by_email=user_example)
    with pytest.raises(AccountLockedError) as excinfo:
        user_service.auth_user(email=user_example.email, password="123456")
    assert str(excinfo.value) == "Tài khoản đang bị khóa"

def test_auth_user_calls_update_last_login(make_user_service, user_example):
    """
    Test trường hợp xác thực thành công sẽ gọi update_last_login
    """
    user_service = make_user_service(get_by_email=user_example)
    user = user_service.auth_user(email=user_example.email, password="123456")

    assert user == user_example
    user_service.user_repository.update_last_login.assert_called_once_with(user_example)

def test_auth_user_does_not_commit_on_failure(make_user_service, user_example):
    """
    Test trường hợp xác thực thất bại không gọi ghi đè thông tin đăng nhập
    """
    from app.core.exceptions import EmailNotFoundError, WrongPasswordError, AccountLockedError

    # 1. Sai email
    user_service_1 = make_user_service(get_by_email=None)
    with pytest.raises(EmailNotFoundError):
        user_service_1.auth_user(email="nonexistent@example.com", password="123")
    user_service_1.user_repository.update_last_login.assert_not_called()

    # 2. Sai mật khẩu
    user_service_2 = make_user_service(get_by_email=user_example)
    with pytest.raises(WrongPasswordError):
        user_service_2.auth_user(email=user_example.email, password="wrong_password")
    user_service_2.user_repository.update_last_login.assert_not_called()

    # 3. Tài khoản bị khóa
    user_example.is_active = False
    user_service_3 = make_user_service(get_by_email=user_example)
    with pytest.raises(AccountLockedError):
        user_service_3.auth_user(email=user_example.email, password="123456")
    user_service_3.user_repository.update_last_login.assert_not_called()
    user_example.is_active = True


# ======    TEST HÀM LOGOUT_USER    ======

def test_logout_user_success(make_user_service):
    """
    Test trường hợp gọi logout_user thành công đưa token vào blacklist
    """
    from datetime import datetime, timezone

    user_service = make_user_service()

    # 1. Trường hợp token chưa hết hạn (exp > now)
    future_exp = datetime.now(timezone.utc).timestamp() + 100
    user_service.logout_user(jti="test_jti", exp=future_exp)
    user_service.redis_service.blacklist_token.assert_called_once()

    # 2. Trường hợp token đã hết hạn (exp <= now)
    user_service.redis_service.reset_mock()
    past_exp = datetime.now(timezone.utc).timestamp() - 100
    user_service.logout_user(jti="test_jti_expired", exp=past_exp)
    user_service.redis_service.blacklist_token.assert_not_called()


# ======    TEST HÀM GET_LIST_USER  ======

def test_get_list_user_when_non_admin_raise_admin_access_required_error(make_user_service):
    """
    User thường (is_admin=False) => AdminAccessRequiredError
    """
    from app.core.exceptions import AdminAccessRequiredError
    user_service = make_user_service()
    with pytest.raises(AdminAccessRequiredError):
        user_service.get_list_user(is_admin=False, page=1, per_page=20)


def test_get_list_user_when_admin_return_users_and_total(make_user_service, user_example):
    """
    Admin (is_admin=True) => trả về tuple (users, total) từ repository
    """
    users = [user_example]
    user_service = make_user_service(count=1, get_page=users)

    result_users, result_total = user_service.get_list_user(is_admin=True, page=1, per_page=20)

    assert result_users == users
    assert result_total == 1


def test_get_list_user_calls_repository_with_correct_params(make_user_service):
    """
    Kiểm tra get_list_user truyền đúng page + per_page vào repository.get_page
    """
    user_service = make_user_service(count=5, get_page=[])

    user_service.get_list_user(is_admin=True, page=2, per_page=10)

    user_service.user_repository.count.assert_called_once()
    user_service.user_repository.get_page.assert_called_once_with(2, 10)


# ======    TEST HÀM CREATE_USER    ======

def test_create_user_success(make_user_service, user_example):
    """
    Tạo user thành công khi name và email chưa tồn tại
    """
    user_service = make_user_service(get_by_name=None, get_by_email=None, create=user_example)

    result = user_service.create_user(
        name="new_user",
        email="new@example.com",
        password="123456"
    )

    assert result == user_example
    user_service.user_repository.create.assert_called_once()


def test_create_user_when_name_exists_raise_duplicate_name_error(make_user_service, user_example):
    """
    Name đã tồn tại → DuplicateNameError, không tiếp tục kiểm tra email hay tạo user
    """
    from app.core.exceptions import DuplicateNameError
    user_service = make_user_service(get_by_name=user_example, get_by_email=None)

    with pytest.raises(DuplicateNameError) as excinfo:
        user_service.create_user(name=user_example.name, email="new@example.com", password="123456")

    assert str(excinfo.value) == "Tên đã tồn tại"
    user_service.user_repository.create.assert_not_called()


def test_create_user_when_email_exists_raise_duplicate_email_error(make_user_service, user_example):
    """
    Email đã tồn tại → DuplicateEmailError, không tạo user
    """
    from app.core.exceptions import DuplicateEmailError
    user_service = make_user_service(get_by_name=None, get_by_email=user_example)

    with pytest.raises(DuplicateEmailError) as excinfo:
        user_service.create_user(name="new_user", email=user_example.email, password="123456")

    assert str(excinfo.value) == "Email đã tồn tại"
    user_service.user_repository.create.assert_not_called()


def test_create_user_does_not_store_raw_password(make_user_service, user_example):
    """
    Mật khẩu được hash trước khi lưu — repository.create không nhận raw password
    """
    raw_password = "123456"
    user_service = make_user_service(get_by_name=None, get_by_email=None, create=user_example)

    user_service.create_user(name="new_user", email="new@example.com", password=raw_password)

    call_kwargs = user_service.user_repository.create.call_args.kwargs
    stored_password = call_kwargs["password"]

    assert stored_password != raw_password          # không lưu raw
    assert stored_password.startswith("$2b$")       # bcrypt format