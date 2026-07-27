from datetime import datetime, timezone
import secrets

from app.core.security import verify_password, hash_password
from app.core.exceptions import EmailNotFoundError, WrongPasswordError, AccountLockedError, InvalidTokenError
from app.core.exceptions import AdminAccessRequiredError, SelfDisableError, PrivilegeViolationError
from app.core.exceptions import DuplicateEmailError, DuplicateNameError
from app.core.exceptions import UserNotFoundError
from app.core.config import settings
from app.utils.link_builder import build_reset_password_url

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
    
    def forgot_password_user(self, email: str):
        """
        Kiểm tra email có tồn tại không
        Trả về reset_url nếu tồn tại, None nếu không (có trường hợp is_active đang là False)
        """
        user =  self.user_repository.get_by_email(email=email)

        if not user or not user.is_active:
            return None

        # Tạo reset token 
        reset_token = secrets.token_urlsafe(32)

        self.redis_service.save_reset_token(
            reset_token=reset_token, 
            user_id=user.user_id, 
            ttl=settings.reset_token_expire_second
        )

        reset_url = build_reset_password_url(reset_token=reset_token)
        return reset_url

    def get_user_by_reset_token(self, reset_token: str):
        """
        Kiểm tra reset_token có tồn tại trong cache không và trả về User
        """
        user_id = self.redis_service.get_user_id_by_reset_token(reset_token=reset_token)

        if not user_id:
            raise InvalidTokenError("Token đã hết hiệu lực hoặc không tồn tại token này")

        user = self.user_repository.get_by_id(id=user_id)
        if not user or not user.is_active:
            raise UserNotFoundError("Tài khoản không tồn tại")

        return user

    def reset_password_user(self, user, new_password: str, reset_token: str):
        """
        Thực hiện reset password cho user, hủy các JWT cũ và vô hiệu hóa reset token
        """
        hashed_password = hash_password(new_password)
        self.user_repository.update_password(user=user, password=hashed_password)

        # Thu hồi toàn bộ JWT access token cũ đang hoạt động
        jwt_ttl_seconds = settings.access_token_expire_minutes * 60
        self.redis_service.revoke_user_sessions(user_id=user.user_id, ttl=jwt_ttl_seconds)

        # Vô hiệu hóa reset token
        self.redis_service.invalidate_reset_token(reset_token=reset_token)

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
        updated_user = self.user_repository.update_profile(user=user, name=name, email=email, is_active=is_active)

        # Xử lí Redis nếu trạng thái của tài khoản thay đổi sau cập nhật
        if status_changed:
            if not is_active:
                jwt_ttl_seconds = settings.access_token_expire_minutes * 60
                
                self.redis_service.revoke_user_sessions(user_id=user_id, ttl=jwt_ttl_seconds)

        return updated_user
    
def get_user_service() -> UserService:
    from app.repositories.user_repository import get_user_repository
    from app.services.redis_service import redis_service
    return UserService(get_user_repository(), redis_service=redis_service)

