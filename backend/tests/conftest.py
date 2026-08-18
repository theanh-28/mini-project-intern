
import pytest
import bcrypt

# Tăng tốc độ bcrypt trong test (rounds=4 thay vì 12)
_original_gensalt = bcrypt.gensalt
bcrypt.gensalt = lambda rounds=4, prefix=b"2b": _original_gensalt(rounds=4, prefix=prefix)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import User
from app.models.role import Role
from app.models.permission import Permission, ActionEnum
from app.core.security import hash_password, create_access_token
from app.core.rbac import rbac_registry
from app.db.base import Base
from app import create_app

# Tính toán băm mật khẩu 1 lần duy nhất thay vì băm lại mỗi khi gọi fixture
DEFAULT_TEST_PASSWORD_HASH = hash_password("123456")

@pytest.fixture
def user_example():
    """
    User seed
    """
    user = User(
        user_id=1,
        name="user_1",
        email="user_1@example.com",
        password=DEFAULT_TEST_PASSWORD_HASH,
        is_active=True,
        must_change_password=False,
    )
    user.roles = []
    return user

@pytest.fixture
def admin_example():
    """
    Admin seed
    """
    admin = User(
        user_id=999,
        name="admin_1",
        email="admin_1@example.com",
        password=DEFAULT_TEST_PASSWORD_HASH,
        is_active=True,
        must_change_password=False,
    )
    admin.roles = []
    return admin

@pytest.fixture
def access_token(user_example):
    """
    Tạo access token cho user thường (roles=['user'])
    """
    roles = [r.code for r in user_example.roles] if user_example.roles else ["user"]
    return create_access_token(user_example.user_id, roles=roles)

@pytest.fixture
def admin_token(admin_example):
    """
    Tạo access token cho admin (roles=['admin'])
    """
    roles = [r.code for r in admin_example.roles] if admin_example.roles else ["admin"]
    return create_access_token(admin_example.user_id, roles=roles)

@pytest.fixture
def db_session():
    """
    Thiết lập phiên kết nối Database với DB SQLite trên RAM và seed RBAC ban đầu
    """
    # 1. Tạo Engine kết nối tới SQLite chạy trên RAM 
    engine = create_engine("sqlite:///:memory:",
                           connect_args={"check_same_thread": False})

    # 2. Khởi tạo tất cả bảng từ Model
    Base.metadata.create_all(bind=engine)

    # 3. Tạo session kết nối
    TestSessionLocal = sessionmaker(bind=engine,
                                    autocommit=False,
                                    autoflush=False,
                                    expire_on_commit=False)
    session = TestSessionLocal()

    # Seed roles và permissions mẫu
    admin_role = Role(role_id=1, name="Administrator", code="admin", is_system=True)
    user_role = Role(role_id=2, name="Regular User", code="user", is_system=True)

    perm_read_users = Permission(permission_id=1, name="Read Users", resource="users", action=ActionEnum.READ)
    perm_create_users = Permission(permission_id=2, name="Create User", resource="users", action=ActionEnum.CREATE)
    perm_update_users = Permission(permission_id=3, name="Update User", resource="users", action=ActionEnum.UPDATE)
    perm_delete_users = Permission(permission_id=4, name="Delete User", resource="users", action=ActionEnum.DELETE)
    perm_read_roles = Permission(permission_id=5, name="Read Roles", resource="roles", action=ActionEnum.READ)
    perm_assign_roles = Permission(permission_id=6, name="Assign Roles", resource="roles", action=ActionEnum.ASSIGN)
    perm_read_audit = Permission(permission_id=7, name="Read Audit Logs", resource="audit_logs", action=ActionEnum.READ)

    admin_role.permissions.extend([perm_read_users, perm_create_users, perm_update_users, perm_delete_users, perm_read_roles, perm_assign_roles, perm_read_audit])

    session.add_all([admin_role, user_role, perm_read_users, perm_create_users, perm_update_users, perm_delete_users, perm_read_roles, perm_assign_roles, perm_read_audit])
    session.commit()

    # Nạp In-Memory RBAC Registry
    rbac_registry.load_permissions(session)

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
    Khởi tạo app Flask cấu hình ở chế độ Testing
    """
    app_instance = create_app(test_config={"TESTING": True})

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
    mock.is_session_revoked.return_value = False
    mock.get.return_value = None

    return mock
