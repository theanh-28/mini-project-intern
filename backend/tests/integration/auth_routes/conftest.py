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
