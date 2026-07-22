from contextvars import ContextVar
from typing import Any, Dict
from dataclasses import dataclass


@dataclass
class RequestContext:
    """
    Class lưu trữ context của mỗi request
    Chỉ là data — không biết gì về ContextVar
    """
    correlation_id: str | None = None
    user_id: int | None = None
    user_info: Dict[str, Any] | None = None


class ContextStore:
    """
    Class quản lý context của mỗi request
    Sử dụng ContextVar để lưu trữ context của mỗi request
    Có thể truy cập context từ bất kỳ đâu trong request lifecycle
    """

    # Khởi tạo ContextVar lưu RequestContext cho mỗi request
    _context_var: ContextVar[RequestContext | None] = ContextVar("request_context", default=None)

    @classmethod
    def get_context(cls) -> RequestContext:
        context = cls._context_var.get()
        if context is None:
            raise RuntimeError(
                "RequestContext chưa được khởi tạo"
            )
        return context

    @classmethod
    def set_context(cls, context: RequestContext) -> None:
        cls._context_var.set(context)

    @classmethod
    def get_correlation_id(cls) -> str | None:
        return cls.get_context().correlation_id

    @classmethod
    def get_user_id(cls) -> int | None:
        return cls.get_context().user_id

    @classmethod
    def get_user_info(cls) -> Dict[str, Any] | None:
        return cls.get_context().user_info

    @classmethod
    def set_correlation_id(cls, correlation_id: str | None) -> None:
        cls.get_context().correlation_id = correlation_id

    @classmethod
    def set_user_id(cls, user_id: int | None) -> None:
        cls.get_context().user_id = user_id

    @classmethod
    def set_user_info(cls, user_info: Dict[str, Any] | None) -> None:
        cls.get_context().user_info = user_info

