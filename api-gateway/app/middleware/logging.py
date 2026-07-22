import uuid
import time
import logging
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.gateway.context import ContextStore, RequestContext

logger = logging.getLogger("gateway")


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware ghi log và trace ID cho mỗi request đi vào hệ thống.
    """
    async def dispatch(self, request: Request, call_next) -> Response:
        # 1. Khởi tạo RequestContext cho request hiện tại
        correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
        context = RequestContext(correlation_id=correlation_id)
        ContextStore.set_context(context)

        start_time = time.time()

        # 2. Ghi log request đầu vào
        logger.info(f"Incoming Request: {request.method} {request.url.path}")

        # 3. Chuyển tiếp xử lý
        try:
            response = await call_next(request)
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            logger.error(
                f"Request Failed: {request.method} {request.url.path} "
                f"| Error: {e} | Latency: {latency:.2f}ms",
                exc_info=True,
            )
            raise

        # 4. Tính toán và ghi log thời gian phản hồi (Latency)
        latency = (time.time() - start_time) * 1000
        logger.info(f"Completed Request: Status {response.status_code} | Latency: {latency:.2f}ms")

        # 5. Gắn mã trace ID vào response headers trả về client
        response.headers["X-Correlation-ID"] = correlation_id

        return response