from datetime import datetime, timezone

from app.repositories.base_repository import BaseRepository
from app.models.user import User


class UserRepository(BaseRepository):
    def __init__(self, db):
        super().__init__(User, db)
    
    def get_by_email(self, email: str) -> User | None:
        return self.db.query(User).filter(User.email == email).first()

    def update_last_login(self, user: User) -> None:
        user.last_login = datetime.now(timezone.utc)


def get_user_repository() -> UserRepository:
    from app.db.session import get_db
    return UserRepository(get_db)   # Truyền hàm get_db không gọi