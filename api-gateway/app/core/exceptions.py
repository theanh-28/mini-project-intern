# ---------------------------------------------------------------------------
# Base exceptions
# ---------------------------------------------------------------------------
class GatewayException(Exception):
    """
    Base exception cho toàn bộ ứng dụng API Gateway.
    Mang status_code và code_error để middleware dùng thống nhất.
    """
    def __init__(self, message: str, status_code: int = 500, code_error: str = "GATEWAY_ERROR"):
        self.message = message
        self.status_code = status_code
        self.code_error = code_error
        super().__init__(message)


# ---------------------------------------------------------------------------
# Client & Request exceptions
# ---------------------------------------------------------------------------
class ValidationException(GatewayException):
    """
    Lỗi dữ liệu đầu vào — 400.
    Dùng khi request gửi lên có dữ liệu sai định dạng hoặc vi phạm quy tắc.
    """
    def __init__(self, message: str = "Dữ liệu yêu cầu không hợp lệ"):
        super().__init__(message, status_code=400, code_error="VALIDATION_ERROR")


class AuthException(GatewayException):
    """
    Lỗi xác thực (Authentication) — 401.
    Dùng khi không xác định được danh tính người dùng hoặc không được phép truy cập.
    """
    def __init__(self, message: str = "Xác thực không thành công", code_error: str = "AUTH_ERROR"):
        super().__init__(message, status_code=401, code_error=code_error)


# ---------------------------------------------------------------------------
# Concrete Auth exceptions
# ---------------------------------------------------------------------------
class TokenExpiredError(AuthException):
    """Ngoại lệ khi token đã hết hạn"""
    def __init__(self, message: str = "Token đã hết hạn, vui lòng đăng nhập lại"):
        super().__init__(message, code_error="TOKEN_EXPIRED")


class InvalidTokenError(AuthException):
    """Ngoại lệ khi token không hợp lệ hoặc thiếu hoặc sai cấu trúc"""
    def __init__(self, message: str = "Token không hợp lệ"):
        super().__init__(message, code_error="INVALID_TOKEN")


class TokenRevokedError(AuthException):
    """Ngoại lệ khi token đã bị thu hồi (đăng xuất)"""
    def __init__(self, message: str = "Token đã bị thu hồi, vui lòng đăng nhập lại"):
        super().__init__(message, code_error="TOKEN_REVOKED")


# ---------------------------------------------------------------------------
# Upstream exceptions (Lỗi giao tiếp với Backend/Upstream)
# ---------------------------------------------------------------------------
class UpstreamException(GatewayException):
    """
    Base exception cho tất cả các lỗi xảy ra khi giao tiếp với service upstream.
    """
    def __init__(self, message: str, status_code: int = 502, code_error: str = "UPSTREAM_ERROR"):
        super().__init__(message, status_code=status_code, code_error=code_error)


class BadGateway(UpstreamException):
    """Lỗi cổng kết nối (Bad Gateway)"""
    def __init__(self, message: str = "Lỗi cổng kết nối (Bad Gateway)"):
        super().__init__(message, status_code=502, code_error="BAD_GATEWAY")


class UpstreamTimeout(UpstreamException):
    """Yêu cầu gửi đến dịch vụ upstream bị quá hạn (Timeout)"""
    def __init__(self, message: str = "Dịch vụ upstream phản hồi quá lâu (Timeout)"):
        super().__init__(message, status_code=504, code_error="UPSTREAM_TIMEOUT")


class UpstreamUnavailable(UpstreamException):
    """Dịch vụ upstream hiện tại không khả dụng"""
    def __init__(self, message: str = "Dịch vụ upstream hiện tại không khả dụng (Unavailable)"):
        super().__init__(message, status_code=502, code_error="UPSTREAM_UNAVAILABLE")


class InvalidUpstreamResponse(UpstreamException):
    """Phản hồi từ upstream trả về không đúng cấu trúc hoặc không hợp lệ"""
    def __init__(self, message: str = "Phản hồi từ dịch vụ upstream không hợp lệ"):
        super().__init__(message, status_code=502, code_error="INVALID_UPSTREAM_RESPONSE")


# ---------------------------------------------------------------------------
# Rate Limiting & Gateway Internal exceptions
# ---------------------------------------------------------------------------
class RateLimitException(GatewayException):
    """Lỗi vượt quá giới hạn tần suất yêu cầu (Rate limit)"""
    def __init__(self, message: str = "Vượt quá giới hạn tần suất yêu cầu (Rate limit)"):
        super().__init__(message, status_code=429, code_error="TOO_MANY_REQUESTS")


class ConfigurationException(GatewayException):
    """Lỗi cấu hình hệ thống của API Gateway"""
    def __init__(self, message: str = "Lỗi cấu hình hệ thống Gateway"):
        super().__init__(message, status_code=500, code_error="CONFIGURATION_ERROR")


class InternalGatewayException(GatewayException):
    """Lỗi nội bộ phát sinh từ Gateway"""
    def __init__(self, message: str = "Lỗi nội bộ hệ thống Gateway"):
        super().__init__(message, status_code=500, code_error="INTERNAL_GATEWAY_ERROR")


class RouteNotFoundError(GatewayException):
    """Ngoại lệ khi không tìm thấy đường dẫn tương ứng trong API Gateway"""
    def __init__(self, message: str = "Không tìm thấy đường dẫn"):
        super().__init__(message, status_code=404, code_error="ROUTE_NOT_FOUND")

