from app.repositories.base_repository import BaseRepository
from app.models.user import User


class UserRepository(BaseRepository):
    def __init__(self, db):
        super().__init__(User, db)
    
    def get_by_email(self, email: str) -> User | None:
        return self.db.query(User).filter(User.email == email).first()