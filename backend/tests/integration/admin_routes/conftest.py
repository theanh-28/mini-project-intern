import pytest

from app.models import User
from app.core.security import hash_password


@pytest.fixture
def insert_users(db_session):
    """
    Thêm 15 user vào db để test pagination
    """
    users = [
        User(
            user_id=i,
            name=f"user_{i}",
            email=f"user_{i}@example.com",
            password=hash_password("123456"),
            is_active=True,
        )
        for i in range(1, 16)  # 15 users
    ]
    db_session.add_all(users)
    db_session.commit()
    return users
