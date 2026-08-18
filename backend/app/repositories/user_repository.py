from datetime import datetime, timezone
from sqlalchemy import or_
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
        if default_role:
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
    
    def update_profile(self, user: User, name: str, email: str) -> User:
        user.name = name
        user.email = email
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def update_status(self, user: User, is_active: bool) -> User:
        user.is_active = is_active
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def update_password(self, user: User, password: str) -> None:
        user.password = password
        user.must_change_password = False
        self.db.commit()

    def set_must_change_password(self, user: User, must_change: bool = True) -> None:
        user.must_change_password = must_change
        self.db.commit()

    def soft_delete(self, user: User) -> None:
        user.deleted_at = datetime.now(timezone.utc)
        self.db.commit()

    def restore(self, user: User) -> None:
        user.deleted_at = None
        self.db.commit()

    def _apply_filters(self, query, filters: dict):
        filters = dict(filters) if filters else {}
        role_filter = filters.pop("role", None)
        search_filter = filters.pop("search", None)

        if role_filter:
            roles = [role_filter] if isinstance(role_filter, str) else role_filter
            query = query.join(User.roles).filter(Role.code.in_(roles)).distinct()

        if search_filter:
            search_term = str(search_filter).strip()
            if search_term:
                query = query.filter(or_(User.name.ilike(f"%{search_term}%"), User.email.ilike(f"%{search_term}%")))

        return super()._apply_filters(query, filters)

    def get_page_with_count(
        self,
        page: int = 1,
        limit: int = 100,
        filters: dict = None
    ) -> tuple[list, int]:
        # Mặc định chỉ lấy tài khoản chưa bị xóa mềm (deleted_at IS NULL)
        query = self.db.query(User).options(joinedload(User.roles)).filter(User.deleted_at.is_(None))
        query = self._apply_filters(query, filters)
        total = query.count()
        skip = (page - 1) * limit
        items = query.offset(skip).limit(limit).all()
        return items, total

def get_user_repository() -> UserRepository:
    from app.db.session import get_db
    return UserRepository(get_db)   # Truyền hàm get_db không gọi