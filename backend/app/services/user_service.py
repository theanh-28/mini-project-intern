from datetime import datetime, timezone
import secrets

from app.core.security import verify_password, hash_password, create_access_token
from app.core.rbac import rbac_registry
from app.core.exceptions import InvalidCredentialsError, AccountLockedError, InvalidTokenError
from app.core.exceptions import AdminAccessRequiredError, SelfDisableError, SelfRestoreError, PrivilegeViolationError
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
        Xác thực email + password. Trả về User nếu đúng, ném ngoại lệ nếu sai.
        Kiểm tra trạng thái tài khoản hoạt động và không bị xóa mềm.
        - Nếu must_change_password is True: Tự động sinh reset_token (lưu Redis TTL 15p) và trả về thông báo yêu cầu đổi mật khẩu qua email, KHÔNG cấp access_token.
        - Nếu must_change_password is False: Cập nhật last_login, tạo access_token, trích xuất roles & permissions và trả về kết quả đăng nhập.
        Áp dụng chuẩn OWASP chống User Enumeration (dùng chung InvalidCredentialsError).
        """
        user = self.user_repository.get_by_email(email, with_roles=True)
        if not user or user.deleted_at is not None:
            raise InvalidCredentialsError()
        
        if not verify_password(password, user.password):
            raise InvalidCredentialsError()
        
        if not user.is_active:
            raise AccountLockedError("Tài khoản đang bị khóa")
            
        if user.must_change_password:
            reset_token = secrets.token_urlsafe(32)
            self.redis_service.save_reset_token(
                reset_token=reset_token,
                user_id=user.user_id,
                ttl=settings.reset_token_expire_second,
            )
            reset_url = build_reset_password_url(reset_token=reset_token)
            return {
                "require_password_change": True,
                "message": "Tài khoản yêu cầu đổi mật khẩu. Vui lòng kiểm tra email để đặt lại mật khẩu.",
                "reset_url": reset_url,
                "user": user,
            }

        self.user_repository.update_last_login(user)

        user_roles = [r.code for r in user.roles] or ["user"]
        user_permissions = list(rbac_registry.get_permissions_for_roles(user_roles))
        access_token = create_access_token(user_id=user.user_id, roles=user_roles)

        return {
            "require_password_change": False,
            "user": user,
            "roles": user_roles,
            "permissions": user_permissions,
            "access_token": access_token,
        }
    
    def forgot_password_user(self, email: str):
        """
        Kiểm tra email có tồn tại không
        Trả về reset_url nếu tồn tại, None nếu không (kể cả trường hợp is_active đang là False hoặc đã bị xóa mềm)
        """
        user = self.user_repository.get_by_email(email=email)

        if not user or not user.is_active or user.deleted_at is not None:
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

        user = self.user_repository.get_by_id(int(user_id))
        if not user or user.deleted_at is not None:
            raise UserNotFoundError("Tài khoản không tồn tại")

        if not user.is_active:
            raise AccountLockedError("Tài khoản đang bị khóa, không thể đặt lại mật khẩu")

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
        page: int,
        per_page: int,
        filters: dict = None
    ):
        """
        Lấy danh sách user.
        Trả về tuple (users, total).
        """
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
    
    def update_user(self, actor_id: int, user_id: int, name: str, email: str):
        """
        Cập nhật thông tin profile của user (name, email).
        Trả về user sau khi đã cập nhật.
        """
        # Kiểm tra user có tồn tại không và chưa bị xóa mềm
        user = self.user_repository.get_by_id(user_id, with_roles=True)
        if not user or user.deleted_at is not None:
            raise UserNotFoundError("User không tồn tại")
        
        # Kiểm tra tài khoản cập nhật có phải admin khác không
        if any(r.code == "admin" for r in (user.roles or [])) and user_id != actor_id:
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

        # Cập nhật thông tin user vào database
        updated_user = self.user_repository.update_profile(user=user, name=name, email=email)
        return updated_user

    def update_user_status(self, actor_id: int, user_id: int, is_active: bool):
        """
        Cập nhật trạng thái hoạt động của tài khoản (is_active: True/False).
        Thu hồi token trong Redis nếu chuyển sang False.
        """
        # Kiểm tra có hành động tự khóa tài khoản của mình không
        if user_id == actor_id and is_active is False:
            raise SelfDisableError("Admin không thể tự khóa tài khoản của chính mình")

        # Kiểm tra user có tồn tại không và chưa bị xóa mềm
        user = self.user_repository.get_by_id(user_id, with_roles=True)
        if not user or user.deleted_at is not None:
            raise UserNotFoundError("User không tồn tại")

        # Kiểm tra tài khoản cập nhật có phải admin khác không
        if any(r.code == "admin" for r in (user.roles or [])) and user_id != actor_id:
            raise PrivilegeViolationError("Admin không thể thay đổi trạng thái của admin khác")

        # Nếu trạng thái không thay đổi, không cần gọi DB update hay Redis
        if user.is_active == is_active:
            return user

        # Cập nhật trạng thái vào database
        updated_user = self.user_repository.update_status(user=user, is_active=is_active)

        # Nếu khóa tài khoản, thu hồi ngay phiên đăng nhập JWT
        if not is_active:
            jwt_ttl_seconds = settings.access_token_expire_minutes * 60
            self.redis_service.revoke_user_sessions(user_id=user_id, ttl=jwt_ttl_seconds)

        return updated_user

    def delete_user(self, actor_id: int, user_id: int):
        """
        Kiểm tra và xóa mềm tài khoản (gán deleted_at)
        """
        if actor_id == user_id:
            # Không thể tự xóa tài khoản của mình
            raise SelfDisableError()

        user = self.user_repository.get_by_id(user_id, with_roles=True)
        if not user:
            # Kiểm tra user có tồn tại không
            raise UserNotFoundError("User không tồn tại")

        if any(r.code == "admin" for r in (user.roles or [])): 
            # Không có quyền xóa tài khoản admin khác
            raise PrivilegeViolationError()

        # Nếu user đã bị xóa mềm từ trước thì không làm gì cả
        if user.deleted_at is not None:
            return

        # Xóa mềm (gán deleted_at)
        self.user_repository.soft_delete(user=user)

        # Khóa session/tài khoản trong Redis
        jwt_ttl_seconds = settings.access_token_expire_minutes * 60
        self.redis_service.revoke_user_sessions(user_id=user_id, ttl=jwt_ttl_seconds)

    def restore_user(self, actor_id: int, user_id: int):
        """
        Kiểm tra và khôi phục tài khoản đã bị xóa mềm (gán deleted_at = None)
        """
        if actor_id == user_id:
            # Không thể tự khôi phục tài khoản của mình
            raise SelfRestoreError()

        user = self.user_repository.get_by_id(user_id, with_roles=True)
        if not user:
            # Kiểm tra user có tồn tại không
            raise UserNotFoundError("User không tồn tại")

        if any(r.code == "admin" for r in (user.roles or [])): 
            # Không có quyền khôi phục tài khoản admin khác
            raise PrivilegeViolationError()

        # Nếu user chưa từng bị xóa thì không làm gì cả
        if user.deleted_at is None:
            return

        # Khôi phục tài khoản
        self.user_repository.restore(user=user)

    def get_user_by_id(self, user_id: int):
        """
        Lấy thông tin chi tiết một user theo ID (chỉ lấy tài khoản chưa bị xóa mềm).
        """
        user = self.user_repository.get_by_id(user_id, with_roles=True)
        if not user or user.deleted_at is not None:
            raise UserNotFoundError("User không tồn tại")
        return user

    def admin_reset_password(self, actor_id: int, user_id: int):
        """
        Admin yêu cầu đặt lại mật khẩu cho một user:
        - Kiểm tra user tồn tại, chưa bị xóa mềm, không phải admin khác, và đang active
        - Sinh reset_token lưu Redis TTL 15p
        - Thu hồi token JWT hiện tại của user trên Redis
        - Tạo reset_url gửi về cho caller (để gửi email)
        """
        user = self.user_repository.get_by_id(user_id, with_roles=True)
        if not user or user.deleted_at is not None:
            raise UserNotFoundError("User không tồn tại")

        if any(r.code == "admin" for r in (user.roles or [])):
            raise PrivilegeViolationError("Không thể yêu cầu đặt lại mật khẩu cho tài khoản Admin khác")

        if not user.is_active:
            raise AccountLockedError("Tài khoản đang bị khóa, không thể đặt lại mật khẩu")

        # Đặt trạng thái yêu cầu đổi mật khẩu (chặn đăng nhập bằng mật khẩu cũ)
        self.user_repository.set_must_change_password(user=user, must_change=True)

        reset_token = secrets.token_urlsafe(32)
        self.redis_service.save_reset_token(
            reset_token=reset_token,
            user_id=user.user_id,
            ttl=settings.admin_reset_token_expire_second
        )
        jwt_ttl_seconds = settings.access_token_expire_minutes * 60
        self.redis_service.revoke_user_sessions(user_id=user.user_id, ttl=jwt_ttl_seconds)

        reset_url = build_reset_password_url(reset_token=reset_token)
        return {
            "reset_url": reset_url,
            "email": user.email,
            "user": user,
            "reset_token": reset_token
        }

def get_user_service() -> UserService:
    from app.repositories.user_repository import get_user_repository
    from app.services.redis_service import redis_service
    return UserService(get_user_repository(), redis_service=redis_service)

