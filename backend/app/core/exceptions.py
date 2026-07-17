

# ---------------------------------------------------------------------------
# Base exceptions
# ---------------------------------------------------------------------------

class AppException(Exception):
    """
    Base exception cho toàn bộ ứng dụng.
    Mang status_code và code_error để handler Flask dùng thống nhất.
    """
    def __init__(self, message: str, status_code: int = 500, code_error: str = "APP_ERROR"):
        self.message = message
        self.status_code = status_code
        self.code_error = code_error
        super().__init__(message)


class AuthException(AppException):
    """
    Lỗi xác thực (Authentication) — 401.
    Dùng khi không xác định được danh tính người dùng
    (sai mật khẩu, email không tồn tại, token hết hạn...).
    """
    def __init__(self, message: str, status_code: int = 401, code_error: str = "AUTH_ERROR"):
        super().__init__(message, status_code=status_code, code_error=code_error)


class PermissionException(AppException):
    """
    Lỗi phân quyền (Authorization) — 403.
    Dùng khi đã xác định được danh tính nhưng không đủ quyền thực hiện hành động.
    """
    def __init__(self, message: str, status_code: int = 403, code_error: str = "PERMISSION_ERROR"):
        super().__init__(message, status_code=status_code, code_error=code_error)


class ValidationException(AppException):
    """
    Lỗi dữ liệu đầu vào — 400.
    Dùng khi request gửi lên có dữ liệu sai format hoặc vi phạm nghiệp vụ.
    """
    def __init__(self, message: str, status_code: int = 400, code_error: str = "VALIDATION_ERROR"):
        super().__init__(message, status_code=status_code, code_error=code_error)

class ConflictException(AppException):
    """
    Lỗi xung đột dữ liệu - 409.
    Dùng khi request hợp lệ nhưng xung đột với trạng thái hiện tại của resource.
    (name tồn tại, email tồn tại khi tạo tài khoản mới,...)
    """
    def __init__(self, message: str, status_code: int = 409, code_error: str = "CONFLICT_ERROR"):
        super().__init__(message, status_code=status_code, code_error=code_error)


# ---------------------------------------------------------------------------
# Concrete exceptions
# ---------------------------------------------------------------------------

class EmailNotFoundError(AuthException):
    """Ngoại lệ khi email không tồn tại"""
    def __init__(self, message: str = "Email không tồn tại"):
        super().__init__(message, status_code=404, code_error="EMAIL_NOT_FOUND")


class WrongPasswordError(AuthException):
    """Ngoại lệ khi mật khẩu không đúng"""
    def __init__(self, message: str = "Mật khẩu không đúng"):
        super().__init__(message, status_code=401, code_error="WRONG_PASSWORD")


class AccountLockedError(AuthException):
    """Ngoại lệ khi tài khoản bị khóa"""
    def __init__(self, message: str = "Tài khoản bị khóa"):
        super().__init__(message, status_code=403, code_error="ACCOUNT_LOCKED")


class AdminAccessRequiredError(PermissionException):
    """Ngoại lệ khi user không có quyền admin"""
    def __init__(self, message: str = "Yêu cầu quyền admin"):
        super().__init__(message, status_code=403, code_error="ADMIN_ACCESS_REQUIRED")


class InvalidInputError(ValidationException):
    """Ngoại lệ khi input không hợp lệ"""
    def __init__(self, message: str = "Input không hợp lệ", code_error: str = "INVALID_INPUT"):
        super().__init__(message, status_code=400, code_error=code_error)


class DuplicateNameError(ConflictException):
    """Ngoại lệ khi tạo tài khoản trùng tên đã tồn tại"""
    def __init__(self, message: str = "Tên đã tồn tại"):
        super().__init__(message, code_error="DUPLICATE_NAME")


class DuplicateEmailError(ConflictException):
    """Ngoại lệ khi tạo tài khoản trùng email đã tồn tại"""
    def __init__(self, message: str = "Email đã tồn tại"):
        super().__init__(message, code_error="DUPLICATE_EMAIL")