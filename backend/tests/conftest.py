
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import User
from app.core.security import hash_password, create_access_token
from app.db.base import Base
from app import create_app

@pytest.fixture
def user_example():
    """
    User seed
    """
    return User(
        user_id=1,
        name="user_1",
        email="user_1@example.com",
        password=hash_password("123456"),
        is_active=True
    )

@pytest.fixture
def admin_example():
    """
    Admin seed
    """
    return User(
        user_id=999,
        name="admin_1",
        email="admin_1@example.com",
        password=hash_password("123456"),
        is_active=True,
        is_admin=True
    )

@pytest.fixture
def access_token(user_example):
    """
    Tạo access token cho user thường (is_admin=False)
    """
    return create_access_token(user_example.user_id, user_example.is_admin)

@pytest.fixture
def admin_token(admin_example):
    """
    Tạo access token cho admin (is_admin=True)
    """
    return create_access_token(admin_example.user_id, admin_example.is_admin)

@pytest.fixture
def db_session():
    """
    Thiết lập phiên kết nối Database với DB SQLite trên RAM
    """
    # 1. Tạo Engine kết nối tới SQLite chạy trên RAM 
    engine = create_engine("sqlite:///:memory:",
                           connect_args = {"check_same_thread": False})

    # 2. Khởi tạo tất cả bảng từ Model
    Base.metadata.create_all(bind=engine)

    # 3. Tạo session kết nối
    TestSessionLocal = sessionmaker(bind=engine,
                                    autocommit=False,
                                    autoflush=False)
    session = TestSessionLocal()

    try:
        # 4. Cấp session cho hàm test
        yield session
    finally:
        # 5. Đóng session và xóa bảng sau khi test xong
        session.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def app(db_session):
    """
    Khởi tạo app Flask câu hình ở chế độ Testing
    """

    app_instance = create_app()
    app_instance.config.update({
        "TESTING": True
    })

    # Ghi đè get_db() bằng db_session để trả về session làm việc với SQLite trong RAM
    # Tránh kết nối DB thật khi test
    import app.db.session as session_module
    session_module.get_db = lambda: db_session

    yield app_instance

@pytest.fixture
def client(app):
    """ 
    Tạo Flask client test
    """
    return app.test_client()

@pytest.fixture(autouse=True)
def mock_redis(mocker):
    """
    Tự động mock redis_service cho tất cả các tests để tránh kết nối tới Redis thật.
    """
    
    mock = mocker.patch("app.services.redis_service.redis_service")

    mock.is_token_blacklisted.return_value = False
    mock.is_account_locked.return_value = False
    mock.get.return_value = None

    return mock
