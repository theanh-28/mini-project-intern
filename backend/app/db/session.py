from flask import g 
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

engine = create_engine(
    settings.database_url,
    echo=settings.debug,        
    pool_pre_ping=True,         # Kiểm tra kết nối trước khi sử dụng
    pool_size=5,                # Số lượng kết nối tối đa trong pool
    max_overflow=10,            # Số lượng kết nối tối đa có thể được tạo ra ngoài pool_size
    pool_timeout=30,            # Thời gian chờ để lấy kết nối từ pool
    pool_recycle=3600,
    connect_args={
        "init_command": "SET time_zone = '+07:00'",
    }
)

# session factory
SessionLocal = sessionmaker(
    bind=engine,            # engine kết nối
    autocommit=False,       # không tự commit
    autoflush=False,        # không tự flush
    expire_on_commit=False  # ojbjects không bị hết hạn sau khi commit
)

def get_db():
    if 'db' not in g:
        g.db = SessionLocal()
    return g.db