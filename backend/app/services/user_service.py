from app.core.security import verify_password


class UserService:
    def __init__(self, user_repository):
        self.user_repository = user_repository

    def auth_user(self, email: str, password: str):
        """
        Xác thực email + password. Trả về User nếu đúng, None nếu sai.
        Kiểm tra trạng thái tài khoản hoạt động và cập nhật thời gian đăng nhập cuối.
        """
        user = self.user_repository.get_by_email(email)
        if not user:
            return None, "Email không tồn tại"
        
        if not verify_password(password, user.password):
            return None, "Sai mật khẩu"
        
        if not user.is_active:
            return None, "Tài khoản đang bị khóa"
            
        self.user_repository.update_last_login(user)
        self.user_repository.commit()
        return user, None
    
def get_user_service() -> UserService:
    from app.repositories.user_repository import get_user_repository
    return UserService(get_user_repository())

