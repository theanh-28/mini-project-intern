from fastapi import FastAPI

from app.core.config import settings
from app.core.logger import setup_logging
from app.middleware.logging import LoggingMiddleware
from app.middleware.exception import ExceptionMiddleware
from app.gateway.router import router as gateway_router

# Khởi tạo cấu hình Logger hệ thống khi khởi động ứng dụng
setup_logging(debug=settings.debug)

app = FastAPI(
    title="Custom API Gateway"
)

# Đăng ký Middleware ghi log toàn cục
app.add_middleware(LoggingMiddleware)

# Đăng ký Middleware bắt lỗi hệ thống (Bọc ngoài cùng)
app.add_middleware(ExceptionMiddleware)


@app.get("/")
async def root():
    return {"message": "Hello World"}

# Đăng ký Router định tuyến của API Gateway
app.include_router(gateway_router)