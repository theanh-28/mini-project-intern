from app.core.config import settings

def build_reset_password_url(reset_token: str):
    """
    Tạo url reset password
    """
    FRONTEND_PATH = "reset-password"
    return f"{settings.frontend_url}/{FRONTEND_PATH}?token={reset_token}"