from datetime import datetime, timezone

from app.repositories.base_repository import BaseRepository
from app.models.user import User


class UserRepository(BaseRepository):
    def __init__(self, db):
        super().__init__(User, db)
    
    def create(self, name: str, email: str, password: str) -> User:
        new_user = User(
            name=name,
            email=email,
            password=password,
            is_admin=False,
            is_active=True,
            created_at=datetime.now(timezone.utc),
        )
        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)
        return new_user
    
    def get_by_email(self, email: str) -> User | None:
        return self.db.query(User).filter(User.email == email).first()

    def get_by_name(self, name: str) -> User | None:
        return self.db.query(User).filter(User.name == name).first()
    
    def update_last_login(self, user: User) -> None:
        user.last_login = datetime.now(timezone.utc)
        self.db.commit()
    
    def update_profile(self, user: User, name: str, email: str, is_active: bool) -> User:
        user.name = name
        user.email = email 
        user.is_active = is_active
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def update_password(self, user: User, password: str) -> None:
        user.password = password
        self.db.commit()


def get_user_repository() -> UserRepository:
    from app.db.session import get_db
    return UserRepository(get_db)   # Truyền hàm get_db không gọi