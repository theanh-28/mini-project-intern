
from app.repositories.user_repository import UserRepository

def test_get_by_email_success(db_session, user_example):
    """
    Trường hợp tìm thấy user tồn tại bằng email
    """

    db_session.add(user_example)
    db_session.commit()
    db_session.refresh(user_example)

    user_repo = UserRepository(db=db_session)

    user = user_repo.get_by_email(user_example.email)

    assert user is not None
    assert user == user_example

def test_get_by_email_not_found(db_session):
    """
    Trường hợp không tìm thấy user tồn tại trong email
    """

    user_repo = UserRepository(db=db_session)

    user = user_repo.get_by_email("fake@example.com")

    assert user is None