from app.repositories.user_repository import UserRepository
from app.core.security import verify_password


class UserService:
    def __init__(self, user: UserRepository):
        self.user = user

    def auth_user(self, email: str, password: str):
        """
        Xác thực email + password. Trả về User nếu đúng, None nếu sai.
        """
        user = self.user.get_by_email(email)
        if not user:
            return None, "Email không tồn tại"
        
        if not verify_password(password, user.password):
            return None, "Sai mật khẩu"
        
        return user, None
    
        

