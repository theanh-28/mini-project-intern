import logging
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse

from app.core.exceptions import GatewayException

logger = logging.getLogger("gateway.exception")

class ExceptionMiddleware(BaseHTTPMiddleware):
    """
    Middle bắt tất cả exception của hệ thống
    """
    async def dispatch(self, request: Request, call_next) -> Response:
        try:
            return await call_next(request)
        except GatewayException as exc:
            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "error": exc.code_error,
                    "message": exc.message
                }
            )
        except HTTPException as exc:
            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "error": f"HTTP_{exc.status_code}",
                    "message": exc.detail
                }
            )
        except Exception as exc:
            # Bắt lỗi hệ thống không lường trước
            logger.error(f"Lỗi không xác định: {exc}", exc_info=True)
            return JSONResponse(
                status_code=500,
                content={
                    "error": "INTERNAL_SERVER_ERROR",
                    "message": "Có lỗi xảy ra tại API Gateway"
                }
            )