import pytest

from app.models import User
from app.core.security import hash_password


from app.models.role import Role


@pytest.fixture
def insert_user(db_session, user_example):
    """
    Thêm user_example vào db
    """
    db_role = db_session.query(Role).filter(Role.code == "user").first()
    user_example.roles = [db_role] if db_role else []
    db_session.add(user_example)
    db_session.commit()
    return user_example


@pytest.fixture
def insert_admin(db_session, admin_example):
    """
    Thêm admin_example vào db
    """
    db_role = db_session.query(Role).filter(Role.code == "admin").first()
    admin_example.roles = [db_role] if db_role else []
    db_session.add(admin_example)
    db_session.commit()
    return admin_example
