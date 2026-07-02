

class AuthException(Exception):
    """
    Lớp ngoại lệ cho các lỗi liên quan đến xác thực
    """
    def __init__(self, message: str, status_code: int = 401, code_error: str = "AUTH_ERROR"):
        self.message = message
        self.status_code = status_code
        self.code_error = code_error
        super().__init__(message)

class EmailNotFoundError(AuthException):
    """
    Ngoại lệ khi email không tồn tại
    """
    def __init__(self, message: str = "Email không tồn tại"):
        super().__init__(message, status_code=404, code_error="EMAIL_NOT_FOUND")

class WrongPasswordError(AuthException):
    """
    Ngoại lệ khi mật khẩu không đúng
    """
    def __init__(self, message: str = "Mật khẩu không đúng"):
        super().__init__(message, status_code=401, code_error="WRONG_PASSWORD")

class AccountLockedError(AuthException):
    """
    Ngoại lệ khi tài khoản bị khóa
    """
    def __init__(self, message: str = "Tài khoản bị khóa"):
        super().__init__(message, status_code=403, code_error="ACCOUNT_LOCKED")

class InvalidInputError(AuthException):
    """
    Ngoại lệ khi input không hợp lệ
    """
    def __init__(self, message: str = "Input không hợp lệ", code_error: str = "INVALID_INPUT"):
        super().__init__(message, status_code=400, code_error=code_error)
        