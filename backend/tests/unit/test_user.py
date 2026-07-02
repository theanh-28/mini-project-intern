import pytest

from app.models import User

@pytest.mark.parametrize(
    "name, email, password",
    [
        ("John Doe", "john.doe@example.com", "password123"),
        ("Jane Smith", "jane.smith@example.com", "password456"),
        ("Bob Johnson", "bob.johnson@example.com", "password789"),
    ]
)
def test_user_when_create_is_correct_return_true(db_session, name, email, password):
    user = User( 
        name=name,
        email=email,
        password=password,
    )
    db_session.add(user)
    db_session.flush() #

    assert user.user_id is not None
    assert user.name == name
    assert user.email == email
    assert user.is_active is True
    assert user.is_admin is False
