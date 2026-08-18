import pytest

from app.models import User
from app.core.security import hash_password
from app.models.role import Role

# Tính toán băm mật khẩu 1 lần duy nhất thay vì băm 15-20 lần ở mỗi test case
DEFAULT_TEST_PASSWORD_HASH = hash_password("123456")


@pytest.fixture
def insert_users(db_session):
    """
    Thêm 15 user vào db để test pagination
    """
    user_role = db_session.query(Role).filter(Role.code == "user").first()
    users = []
    for i in range(1, 16):
        u = User(
            user_id=i,
            name=f"user_{i}",
            email=f"user_{i}@example.com",
            password=DEFAULT_TEST_PASSWORD_HASH,
            is_active=True,
        )
        if user_role:
            u.roles.append(user_role)
        users.append(u)

    db_session.add_all(users)
    db_session.commit()
    return users

@pytest.fixture
def insert_admins(db_session):
    """
    Thêm 5 admin vào db
    """
    admin_role = db_session.query(Role).filter(Role.code == "admin").first()
    admins = []
    for i in range(16, 21):
        a = User(
            user_id=i,
            name=f"admin_{i}",
            email=f"admin_{i}@example.com",
            password=DEFAULT_TEST_PASSWORD_HASH,
            is_active=True,
        )
        if admin_role:
            a.roles.append(admin_role)
        admins.append(a)

    db_session.add_all(admins)
    db_session.commit()
    return admins