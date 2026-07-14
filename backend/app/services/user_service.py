from datetime import datetime, timezone

from app.core.security import verify_password, hash_password
from app.core.exceptions import EmailNotFoundError, WrongPasswordError, AccountLockedError
from app.core.exceptions import AdminAccessRequiredError, SelfDisableError, PrivilegeViolationError
from app.core.exceptions import DuplicateEmailError, DuplicateNameError
from app.core.exceptions import UserNotFoundError

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

    def get_list_user(
        self,
        is_admin: bool,
        page: int,
        per_page: int,
        filters: dict = None
    ):
        """
        Lấy danh sách user.
        Trả về tuple (users, total).
        """
        if not is_admin:
            raise AdminAccessRequiredError("Yêu cầu quyền admin để truy cập danh sách user")

        return self.user_repository.get_page_with_count(page, per_page, filters=filters)
    
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
    
    def update_user(self, actor_id: int, user_id: int, name: str, email: str, is_active: bool):
        """
        Cập nhật thông tin của user
        Trả về user sau khi đã cập nhật
        """

        # Kiểm tra có hành động tự khóa tài khoản của mình không
        if user_id == actor_id and is_active is False:
            raise SelfDisableError("Admin không thể tự khóa tài khoản của chính mình")

        # Kiểm tra user có tồn tại không
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundError("User không tồn tại")
        
        # Kiểm tra tài khoản cập nhật có phải admin khác không
        if user.is_admin and user_id != actor_id:
            raise PrivilegeViolationError("Admin không thể thay đổi thông tin của admin khác")
        
        # Kiểm tra email muốn cập nhật đã tồn tại chưa
        if user.email != email:
            existing_user_email = self.user_repository.get_by_email(email)
            if existing_user_email and existing_user_email.user_id != user.user_id: # Tránh trường hợp DB không phân biệt hoa/thường
                raise DuplicateEmailError("Email đã tồn tại")
        
        # Kiểm tra name muốn cập nhật đã tồn tại chưa
        if user.name != name:
            existing_user_name = self.user_repository.get_by_name(name)
            if existing_user_name and existing_user_name.user_id != user.user_id: # Tránh trường hợp DB không phân biệt hoa/thường
                raise DuplicateNameError("Tên đã tồn tại")
        
        # So sánh trạng thái mói so với trạng thái hiện tại của tài khoản
        status_changed = user.is_active != is_active

        # Cập nhật thông tin user vào database
        updated_user = self.user_repository.update(user=user, name=name, email=email, is_active=is_active)

        # Xử lí Redis nếu trạng thái của tài khoản thay đổi sau cập nhật
        if status_changed:
            if not is_active:
                from app.core.config import settings
                jwt_ttl_seconds = settings.access_token_expire_minutes * 60
                
                self.redis_service.lock_account(user_id=user_id, ttl=jwt_ttl_seconds)
            else:
                self.redis_service.unlock_account(user_id=user_id)

        return updated_user
    
def get_user_service() -> UserService:
    from app.repositories.user_repository import get_user_repository
    from app.services.redis_service import redis_service
    return UserService(get_user_repository(), redis_service=redis_service)

