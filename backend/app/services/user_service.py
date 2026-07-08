from datetime import datetime, timezone

from app.core.security import verify_password, hash_password
from app.core.exceptions import EmailNotFoundError, WrongPasswordError, AccountLockedError
from app.core.exceptions import AdminAccessRequiredError
from app.core.exceptions import DuplicateEmailError, DuplicateNameError

class UserService:
    def __init__(self, user_repository, redis_service):
        self.user_repository = user_repository
        self.redis_service = redis_service

    def auth_user(self, email: str, password: str):
        """
        Xác thực email + password. Trả về User nếu đúng, None nếu sai.
        Kiểm tra trạng thái tài khoản hoạt động và cập nhật thời gian đăng nhập cuối.
        """
        user = self.user_repository.get_by_email(email)
        if not user:
            raise EmailNotFoundError("Email không tồn tại")
        
        if not verify_password(password, user.password):
            raise WrongPasswordError("Mật khẩu không đúng")
        
        if not user.is_active:
            raise AccountLockedError("Tài khoản đang bị khóa")
            
        self.user_repository.update_last_login(user)
        return user
    
    def logout_user(self, jti: str, exp: int):
        """
        Thêm token vào blacklist trong Redis nếu chưa hết hạn.
        """
        # Tính TTL còn lại bằng giây
        now = datetime.now(timezone.utc).timestamp()
        ttl = int(exp - now)
        
        # Nếu token vẫn chưa hết hạn thì cho vào blacklist
        if ttl > 0:
            self.redis_service.blacklist_token(jti, ttl)

    def get_list_user(self, is_admin: bool, page: int, per_page: int):
        """
        Lấy danh sách user.
        Trả về tuple (users, total).
        """
        if not is_admin:
            raise AdminAccessRequiredError("Yêu cầu quyền admin để truy cập danh sách user")

        total = self.user_repository.count()
        users = self.user_repository.get_page(page, per_page)
        return users, total
    
    def create_user(self, name: str, email: str, password: str):
        """
        Tạo user mới.
        """
        # Kiểm tra name đã tồn tại chưa
        existing_name = self.user_repository.get_by_name(name)
        if existing_name:
            raise DuplicateNameError("Tên đã tồn tại")
        
        # Kiểm tra email đã tồn tại chưa
        existing_user = self.user_repository.get_by_email(email)
        if existing_user:
            raise DuplicateEmailError("Email đã tồn tại")
        
        # Băm mật khẩu trước khi lưu
        hashed_password = hash_password(password)

        # Tạo user mới trong cơ sở dữ liệu
        new_user = self.user_repository.create(name=name, email=email, password=hashed_password)
        return new_user
    
def get_user_service() -> UserService:
    from app.repositories.user_repository import get_user_repository
    from app.services.redis_service import redis_service
    return UserService(get_user_repository(), redis_service=redis_service)

