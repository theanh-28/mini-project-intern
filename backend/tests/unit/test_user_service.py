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
    user_service = make_user_service(get_page_with_count=(users, 1))

    result_users, result_total = user_service.get_list_user(is_admin=True, page=1, per_page=20)

    assert result_users == users
    assert result_total == 1


def test_get_list_user_calls_repository_with_correct_params(make_user_service):
    """
    Kiểm tra get_list_user truyền đúng page + per_page vào repository.get_page_with_count
    """
    user_service = make_user_service(get_page_with_count=([], 5))

    user_service.get_list_user(is_admin=True, page=2, per_page=10)

    user_service.user_repository.get_page_with_count.assert_called_once_with(2, 10, filters=None)


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


# ====== TEST HÀM UPDATE_USER   ======

def test_update_user_success(make_user_service, user_example):
    """
    Cập nhật thông tin user thành công
    """
    user_example.is_admin = False  # Đảm bảo không dính check admin khác
    user_service = make_user_service(
        get_by_id=user_example,
        get_by_email=None,
        get_by_name=None,
        update_profile=user_example
    )

    result = user_service.update_user(
        actor_id=999, # Admin khác sửa
        user_id=user_example.user_id,
        name="new_name",
        email="new_email@example.com",
        is_active=True
    )

    assert result == user_example
    user_service.user_repository.update_profile.assert_called_once_with(
        user=user_example,
        name="new_name",
        email="new_email@example.com",
        is_active=True
    )

def test_update_user_self_disable_raise_self_disable_error(make_user_service, user_example):
    """
    Admin tự khóa chính mình (user_id == actor_id và is_active=False) => SelfDisableError
    """
    from app.core.exceptions import SelfDisableError
    user_service = make_user_service()

    with pytest.raises(SelfDisableError) as excinfo:
        user_service.update_user(
            actor_id=user_example.user_id, # actor_id trùng user_id
            user_id=user_example.user_id,
            name="new_name",
            email="new_email@example.com",
            is_active=False  # Khóa tài khoản
        )

    user_service.user_repository.update_profile.assert_not_called()

def test_update_user_when_not_found_raise_user_not_found_error(make_user_service):
    """
    Không tìm thấy user theo user_id => UserNotFoundError
    """
    from app.core.exceptions import UserNotFoundError
    user_service = make_user_service(get_by_id=None)

    with pytest.raises(UserNotFoundError) as excinfo:
        user_service.update_user(
            actor_id=999,
            user_id=9999,
            name="new_name",
            email="new_email@example.com",
            is_active=True
        )

    user_service.user_repository.update_profile.assert_not_called()

def test_update_user_when_target_is_admin_raise_privilege_violation_error(make_user_service, user_example):
    """
    Cố gắng sửa đổi Admin khác (user.is_admin=True và user_id != actor_id) => PrivilegeViolationError
    """
    from app.core.exceptions import PrivilegeViolationError
    user_example.is_admin = True # Đối tượng bị sửa là admin
    user_service = make_user_service(get_by_id=user_example)

    with pytest.raises(PrivilegeViolationError) as excinfo:
        user_service.update_user(
            actor_id=999, # Admin khác thực hiện
            user_id=user_example.user_id,
            name="new_name",
            email="new_email@example.com",
            is_active=True
        )

    user_service.user_repository.update_profile.assert_not_called()

def test_update_user_when_email_exists_raise_duplicate_email_error(make_user_service, user_example):
    """
    Cập nhật sang email mới đã được sử dụng bởi user khác => DuplicateEmailError
    """
    from app.core.exceptions import DuplicateEmailError
    from app.models.user import User
    
    # Mock một user khác sở hữu email cần đổi
    another_user = User(user_id=99, email="taken@example.com", name="other")
    user_service = make_user_service(
        get_by_id=user_example,
        get_by_email=another_user
    )

    with pytest.raises(DuplicateEmailError) as excinfo:
        user_service.update_user(
            actor_id=999,
            user_id=user_example.user_id,
            name=user_example.name,
            email="taken@example.com", # Email bị trùng
            is_active=True
        )

    user_service.user_repository.update_profile.assert_not_called()

def test_update_user_when_name_exists_raise_duplicate_name_error(make_user_service, user_example):
    """
    Cập nhật sang tên mới đã được sử dụng bởi user khác => DuplicateNameError
    """
    from app.core.exceptions import DuplicateNameError
    from app.models.user import User
    
    # Mock một user khác sở hữu tên cần đổi
    another_user = User(user_id=99, email="other@example.com", name="taken_name")
    user_service = make_user_service(
        get_by_id=user_example,
        get_by_name=another_user
    )

    with pytest.raises(DuplicateNameError) as excinfo:
        user_service.update_user(
            actor_id=999,
            user_id=user_example.user_id,
            name="taken_name", # Tên bị trùng
            email=user_example.email,
            is_active=True
        )

    user_service.user_repository.update_profile.assert_not_called()


def test_update_user_same_user_different_case_email_success(make_user_service, user_example):
    """
    Cập nhật email chỉ thay đổi chữ hoa/thường (ví dụ từ user_1@example.com thành User_1@Example.com).
    Hành động này phải THÀNH CÔNG và không được báo lỗi trùng lặp (DuplicateEmailError).
    """
    
    # Mock khi get_by_email bằng email mới sẽ trả về chính user_example (giả lập hành vi case-insensitive của MySQL)
    user_service = make_user_service(
        get_by_id=user_example,
        get_by_email=user_example,  # Trả về chính nó
        update_profile=user_example
    )

    result = user_service.update_user(
        actor_id=999,
        user_id=user_example.user_id,
        name=user_example.name,
        email="User_1@Example.com",
        is_active=True
    )

    assert result == user_example
    user_service.user_repository.update_profile.assert_called_once_with(
        user=user_example,
        name=user_example.name,
        email="User_1@Example.com",
        is_active=True
    )


def test_update_user_same_user_different_case_name_success(make_user_service, user_example):
    """
    Cập nhật name chỉ thay đổi chữ hoa/thường (ví dụ từ user_1 thành User_1).
    Hành động này phải THÀNH CÔNG và không được báo lỗi trùng lặp (DuplicateNameError).
    """
    
    # Mock khi get_by_name bằng name mới sẽ trả về chính user_example (giả lập hành vi case-insensitive của MySQL)
    user_service = make_user_service(
        get_by_id=user_example,
        get_by_name=user_example,  # Trả về chính nó
        update_profile=user_example
    )

    result = user_service.update_user(
        actor_id=999,
        user_id=user_example.user_id,
        name="User_1",
        email=user_example.email,
        is_active=True
    )

    assert result == user_example
    user_service.user_repository.update_profile.assert_called_once_with(
        user=user_example,
        name="User_1",
        email=user_example.email,
        is_active=True
    )


def test_update_user_to_inactive_calls_redis_revoke(make_user_service, user_example):
    """
    Khi thay đổi trạng thái user từ active (True) sang inactive (False) -> gọi revoke_user_sessions
    """
    user_example.is_active = True
    user_example.is_admin = False
    user_service = make_user_service(
        get_by_id=user_example,
        get_by_email=None,
        get_by_name=None,
        update_profile=user_example
    )

    user_service.update_user(
        actor_id=999,
        user_id=user_example.user_id,
        name="User_1",
        email=user_example.email,
        is_active=False  # Chuyển sang inactive
    )

    # Kiểm tra gọi revoke_user_sessions với TTL 3600 (settings.access_token_expire_minutes * 60)
    user_service.redis_service.revoke_user_sessions.assert_called_once_with(
        user_id=user_example.user_id,
        ttl=3600
    )


# ====== TEST HÀM FORGOT_PASSWORD_USER ======

def test_forgot_password_user_success(make_user_service, user_example):
    """
    Tìm thấy email và user đang active -> sinh reset URL và lưu token vào Redis
    """
    user_example.is_active = True
    user_service = make_user_service(get_by_email=user_example)

    reset_url = user_service.forgot_password_user(email=user_example.email)

    assert reset_url is not None
    assert "/reset-password?token=" in reset_url
    
    # Kiểm tra Redis save_reset_token được gọi
    user_service.redis_service.save_reset_token.assert_called_once()
    call_kwargs = user_service.redis_service.save_reset_token.call_args[1]
    assert call_kwargs["user_id"] == user_example.user_id


def test_forgot_password_user_not_found(make_user_service):
    """
    Email không tồn tại -> Trả về None và không lưu gì vào Redis
    """
    user_service = make_user_service(get_by_email=None)

    reset_url = user_service.forgot_password_user(email="nonexistent@example.com")

    assert reset_url is None
    user_service.redis_service.save_reset_token.assert_not_called()


def test_forgot_password_user_inactive(make_user_service, user_example):
    """
    Email tồn tại nhưng tài khoản bị inactive (khóa) -> Trả về None và không lưu gì vào Redis
    """
    user_example.is_active = False
    user_service = make_user_service(get_by_email=user_example)

    reset_url = user_service.forgot_password_user(email=user_example.email)

    assert reset_url is None
    user_service.redis_service.save_reset_token.assert_not_called()


# ====== TEST HÀM GET_USER_BY_RESET_TOKEN ======

def test_get_user_by_reset_token_success(make_user_service, user_example):
    """
    Token hợp lệ và user đang active -> Trả về đối tượng User
    """
    user_example.is_active = True
    user_service = make_user_service(get_by_id=user_example)
    user_service.redis_service.get_user_id_by_reset_token.return_value = str(user_example.user_id)

    user = user_service.get_user_by_reset_token(reset_token="valid_token")

    assert user == user_example
    user_service.redis_service.get_user_id_by_reset_token.assert_called_once_with(reset_token="valid_token")
    user_service.user_repository.get_by_id.assert_called_once_with(id=str(user_example.user_id))


def test_get_user_by_reset_token_invalid_token(make_user_service):
    """
    Token không tồn tại hoặc hết hạn -> Ném lỗi InvalidTokenError
    """
    from app.core.exceptions import InvalidTokenError
    user_service = make_user_service()
    user_service.redis_service.get_user_id_by_reset_token.return_value = None

    with pytest.raises(InvalidTokenError) as excinfo:
        user_service.get_user_by_reset_token(reset_token="expired_token")

    user_service.user_repository.get_by_id.assert_not_called()


def test_get_user_by_reset_token_user_not_found(make_user_service):
    """
    Token hợp lệ nhưng không tìm thấy User tương ứng trong DB -> Ném lỗi UserNotFoundError
    """
    from app.core.exceptions import UserNotFoundError
    user_service = make_user_service(get_by_id=None)
    user_service.redis_service.get_user_id_by_reset_token.return_value = "999"

    with pytest.raises(UserNotFoundError) as excinfo:
        user_service.get_user_by_reset_token(reset_token="valid_token")


def test_get_user_by_reset_token_user_inactive(make_user_service, user_example):
    """
    Token hợp lệ nhưng tài khoản User bị khóa (inactive) -> Ném lỗi UserNotFoundError
    """
    from app.core.exceptions import UserNotFoundError
    user_example.is_active = False
    user_service = make_user_service(get_by_id=user_example)
    user_service.redis_service.get_user_id_by_reset_token.return_value = str(user_example.user_id)

    with pytest.raises(UserNotFoundError) as excinfo:
        user_service.get_user_by_reset_token(reset_token="valid_token")


# ====== TEST HÀM RESET_PASSWORD_USER ======

def test_reset_password_user_success(make_user_service, user_example):
    """
    Thực hiện reset mật khẩu thành công: lưu mật khẩu đã băm, thu hồi session và hủy reset token
    """
    user_service = make_user_service()

    result = user_service.reset_password_user(
        user=user_example,
        new_password="new_password_123",
        reset_token="token_to_invalidate"
    )

    assert result is None

    # Kiểm tra gọi repository lưu mật khẩu băm (mật khẩu không lưu plain-text)
    user_service.user_repository.update_password.assert_called_once()
    call_args = user_service.user_repository.update_password.call_args[1]
    assert call_args["user"] == user_example
    assert call_args["password"] != "new_password_123"
    assert call_args["password"].startswith("$2b$")  # bcrypt hash format

    # Kiểm tra gọi thu hồi session trên Redis
    user_service.redis_service.revoke_user_sessions.assert_called_once_with(
        user_id=user_example.user_id,
        ttl=3600
    )

    # Kiểm tra hủy reset token trên Redis
    user_service.redis_service.invalidate_reset_token.assert_called_once_with(
        reset_token="token_to_invalidate"
    )
# ======    TEST HÀM DELETE_USER    ======

def test_delete_user_success(make_user_service, user_example):
    """
    Xóa mềm tài khoản hợp lệ (actor_id khác user_id, user tồn tại và không phải admin)
    => Đã gọi soft_delete và lock_account trong Redis
    """
    user_example.is_admin = False
    user_service = make_user_service(get_by_id=user_example)

    user_service.delete_user(actor_id=999, user_id=user_example.user_id)

    user_service.user_repository.soft_delete.assert_called_once_with(user=user_example)
    user_service.redis_service.lock_account.assert_called_once()


def test_delete_user_self_delete_raises_self_disable_error(make_user_service):
    """
    Tự xóa tài khoản của chính mình (actor_id == user_id) => SelfDisableError
    """
    from app.core.exceptions import SelfDisableError

    user_service = make_user_service()

    with pytest.raises(SelfDisableError):
        user_service.delete_user(actor_id=1, user_id=1)

    user_service.user_repository.soft_delete.assert_not_called()


def test_delete_user_not_found_raises_user_not_found_error(make_user_service):
    """
    Xóa tài khoản không tồn tại => UserNotFoundError
    """
    from app.core.exceptions import UserNotFoundError

    user_service = make_user_service(get_by_id=None)

    with pytest.raises(UserNotFoundError):
        user_service.delete_user(actor_id=999, user_id=9999)

    user_service.user_repository.soft_delete.assert_not_called()


def test_delete_user_admin_target_raises_privilege_violation_error(make_user_service, user_example):
    """
    Xóa tài khoản Admin khác => PrivilegeViolationError
    """
    from app.core.exceptions import PrivilegeViolationError

    user_example.is_admin = True
    user_service = make_user_service(get_by_id=user_example)

    with pytest.raises(PrivilegeViolationError):
        user_service.delete_user(actor_id=999, user_id=user_example.user_id)

    user_service.user_repository.soft_delete.assert_not_called()


def test_delete_user_already_inactive_skips_soft_delete(make_user_service, user_example):
    """
    Tài khoản đã ở trạng thái xóa mềm (is_active = False) từ trước
    => Bỏ qua không gọi soft_delete và redis lock
    """
    user_example.is_admin = False
    user_example.is_active = False
    user_service = make_user_service(get_by_id=user_example)

    user_service.delete_user(actor_id=999, user_id=user_example.user_id)

    user_service.user_repository.soft_delete.assert_not_called()
    user_service.redis_service.lock_account.assert_not_called()
    user_example.is_active = True


# ======    TEST HÀM RESTORE_USER   ======

def test_restore_user_success(make_user_service, user_example):
    """
    Khôi phục tài khoản hợp lệ (actor_id khác user_id, user tồn tại và không phải admin)
    => Đã gọi repository.restore
    """
    user_example.is_admin = False
    user_example.is_active = False
    user_service = make_user_service(get_by_id=user_example)

    user_service.restore_user(actor_id=999, user_id=user_example.user_id)

    user_service.user_repository.restore.assert_called_once_with(user=user_example)
    user_example.is_active = True


def test_restore_user_already_active_skips_restore(make_user_service, user_example):
    """
    Tài khoản đã ở trạng thái hoạt động (is_active = True) từ trước
    => Bỏ qua không gọi repository.restore
    """
    user_example.is_admin = False
    user_example.is_active = True
    user_service = make_user_service(get_by_id=user_example)

    user_service.restore_user(actor_id=999, user_id=user_example.user_id)

    user_service.user_repository.restore.assert_not_called()


def test_restore_user_self_restore_raises_self_restore_error(make_user_service):
    """
    Tự khôi phục tài khoản của chính mình (actor_id == user_id) => SelfRestoreError
    """
    from app.core.exceptions import SelfRestoreError

    user_service = make_user_service()

    with pytest.raises(SelfRestoreError):
        user_service.restore_user(actor_id=1, user_id=1)

    user_service.user_repository.restore.assert_not_called()


def test_restore_user_not_found_raises_user_not_found_error(make_user_service):
    """
    Khôi phục tài khoản không tồn tại => UserNotFoundError
    """
    from app.core.exceptions import UserNotFoundError

    user_service = make_user_service(get_by_id=None)

    with pytest.raises(UserNotFoundError):
        user_service.restore_user(actor_id=999, user_id=9999)

    user_service.user_repository.restore.assert_not_called()


def test_restore_user_admin_target_raises_privilege_violation_error(make_user_service, user_example):
    """
    Khôi phục tài khoản Admin khác => PrivilegeViolationError
    """
    from app.core.exceptions import PrivilegeViolationError

    user_example.is_admin = True
    user_service = make_user_service(get_by_id=user_example)

    with pytest.raises(PrivilegeViolationError):
        user_service.restore_user(actor_id=999, user_id=user_example.user_id)

    user_service.user_repository.restore.assert_not_called()
