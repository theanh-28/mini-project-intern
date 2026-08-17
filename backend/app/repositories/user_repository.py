from datetime import datetime, timezone
from sqlalchemy.orm import joinedload

from app.repositories.base_repository import BaseRepository
from app.models.user import User
from app.models.role import Role


class UserRepository(BaseRepository):
    def __init__(self, db):
        super().__init__(User, db)
    
    def create(self, name: str, email: str, password: str, must_change_password: bool = True) -> User:
        new_user = User(
            name=name,
            email=email,
            password=password,
            is_active=True,
            must_change_password=must_change_password,
            created_at=datetime.now(timezone.utc),
        )
        # Gán role mặc định 'user'
        default_role = self.db.query(Role).filter(Role.code == "user").first()
        new_user.roles.append(default_role)

        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)
        return new_user
    
    def get_by_id(self, user_id: int, with_roles: bool = False) -> User | None:
        query = self.db.query(User)
        if with_roles:
            query = query.options(joinedload(User.roles))
        return query.filter(User.user_id == user_id).first()

    def get_by_email(self, email: str, with_roles: bool = False) -> User | None:
        query = self.db.query(User)
        if with_roles:
            query = query.options(joinedload(User.roles))
        return query.filter(User.email == email).first()

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
        user.must_change_password = False
        self.db.commit()

    def soft_delete(self, user: User) -> None:
        user.is_active = False
        self.db.commit()

    def restore(self, user: User) -> None:
        user.is_active = True
        self.db.commit()

def get_user_repository() -> UserRepository:
    from app.db.session import get_db
    return UserRepository(get_db)   # Truyền hàm get_db không gọi