import pytest

from app.models.user import User
from app.repositories.user_repository import UserRepository


@pytest.fixture
def inserted_user(db_session, user_example):
    """
    Fixture thêm user_example vào DB và trả về object đã được persist.
    Dùng khi test cần một user thực sự tồn tại trong DB trước khi gọi method.
    """
    db_session.add(user_example)
    db_session.commit()
    db_session.refresh(user_example)
    return user_example


# ======    TEST HÀM GET_BY_EMAIL   ======

def test_get_by_email_success(inserted_user, db_session):
    """
    Trường hợp tìm thấy user tồn tại bằng email
    """
    user_repo = UserRepository(db=db_session)

    user = user_repo.get_by_email(inserted_user.email)

    assert user is not None
    assert user == inserted_user

def test_get_by_email_not_found(db_session):
    """
    Trường hợp không tìm thấy user tồn tại trong email
    """

    user_repo = UserRepository(db=db_session)

    user = user_repo.get_by_email("fake@example.com")

    assert user is None


# ======    TEST HÀM UPDATE_LAST_LOGIN  ======

def test_update_last_login(inserted_user, db_session):
    """
    Test cập nhật last_login cho user
    """
    assert inserted_user.last_login is None

    user_repo = UserRepository(db=db_session)
    user_repo.update_last_login(inserted_user)

    db_session.refresh(inserted_user)
    assert inserted_user.last_login is not None


# ======    TEST HÀM GET_BY_ID  ======

def test_get_by_id_success(inserted_user, db_session):
    """
    Kiểm tra việc lấy user bằng ID thành công qua phương thức get_by_id của BaseRepository
    """
    user_repo = UserRepository(db=db_session)
    user = user_repo.get_by_id(inserted_user.user_id)

    assert user is not None
    assert user.user_id == inserted_user.user_id
    assert user.email == inserted_user.email

def test_get_by_id_not_found(db_session):
    """
    Kiểm tra khi get_by_id với ID không tồn tại sẽ trả về None
    """
    user_repo = UserRepository(db=db_session)
    user = user_repo.get_by_id(9999)

    assert user is None


# ======    TEST HÀM GET_BY_NAME    ======

def test_get_by_name_success(inserted_user, db_session):
    """
    Tìm user theo name đang tồn tại trong DB => trả về đúng user
    """
    user_repo = UserRepository(db=db_session)

    user = user_repo.get_by_name(inserted_user.name)

    assert user is not None
    assert user == inserted_user


def test_get_by_name_not_found(db_session):
    """
    Tìm user theo name không tồn tại trong DB => trả về None
    """
    user_repo = UserRepository(db=db_session)

    user = user_repo.get_by_name("nonexistent_name")

    assert user is None


# ======    TEST HÀM CREATE     ======

def test_create_stores_correct_fields(db_session):
    """
    Tạo user mới → các trường name, email, password được lưu đúng
    """
    user_repo = UserRepository(db=db_session)

    new_user = user_repo.create(
        name="new_user",
        email="new@example.com",
        password="hashed_password_value"
    )

    assert new_user.name == "new_user"
    assert new_user.email == "new@example.com"
    assert new_user.password == "hashed_password_value"


def test_create_sets_default_flags(db_session):
    """
    Tạo user mới => is_admin=False và is_active=True theo mặc định
    """
    user_repo = UserRepository(db=db_session)

    new_user = user_repo.create(
        name="new_user",
        email="new@example.com",
        password="hashed_password_value"
    )

    assert new_user.is_admin is False
    assert new_user.is_active is True


def test_create_sets_created_at(db_session):
    """
    Tạo user mới => created_at được gán tự động (không phải None)
    """
    user_repo = UserRepository(db=db_session)

    new_user = user_repo.create(
        name="new_user",
        email="new@example.com",
        password="hashed_password_value"
    )

    assert new_user.created_at is not None


def test_create_persists_to_database(db_session):
    """
    Tạo user mới => user tồn tại trong DB và có thể lấy lại bằng ID
    """
    user_repo = UserRepository(db=db_session)

    new_user = user_repo.create(
        name="new_user",
        email="new@example.com",
        password="hashed_password_value"
    )

    fetched = db_session.get(User, new_user.user_id)
    assert fetched is not None
    assert fetched.name == "new_user"
    assert fetched.email == "new@example.com"
