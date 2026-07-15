import pytest
from datetime import datetime, timezone
from app.models import User
from app.models.audit_log import AuditLog

@pytest.fixture(autouse=True, scope="module")
def setup_audit_listener():
    """
    Tự động gọi create_app() một lần trước khi chạy các test trong module này
    để đảm bảo các event listener của SQLAlchemy được đăng ký.
    """
    from app import create_app
    create_app()


def test_when_create_user_then_create_audit_log_generated(db_session, user_example):
    """
    Test hành động tạo mới (CREATE) phải sinh log và loại trừ các trường nhạy cảm như password.
    """
    # 1. Thêm một user mới
    db_session.add(user_example)
    db_session.commit()

    log = db_session.query(AuditLog).filter_by(
        table_name="users", 
        target_id=str(user_example.user_id)
    ).first()
    
    assert log is not None
    assert log.action == "CREATE"
    assert log.new_value is not None
    assert log.new_value["name"] == "user_1"
    assert log.new_value["email"] == "user_1@example.com"
    # Đảm bảo mật khẩu không bị lộ (nằm trong danh sách loại trừ)
    assert "password" not in log.new_value
    assert log.old_value is None
    # Ngoài request context thì actor_id phải là None
    assert log.actor_id is None


def test_when_update_user_then_update_audit_log_generated(db_session, user_example):
    """
    Test hành động cập nhật (UPDATE) chỉ lưu các trường thực sự thay đổi.
    """
    # 1. Thêm một user sẵn
    db_session.add(user_example)
    db_session.commit()

    # 2. Cập nhật name và email
    user_example.name = "test_audit_updated"
    user_example.email = "test_audit_updated@example.com"
    db_session.commit()

    log = db_session.query(AuditLog).filter_by(
        table_name="users",
        target_id=str(user_example.user_id)
    ).order_by(AuditLog.id.desc()).first()
    
    assert log is not None
    assert log.action == "UPDATE"
    assert log.old_value["name"] == "user_1"
    assert log.new_value["name"] == "test_audit_updated"
    assert log.old_value["email"] == "user_1@example.com"
    assert log.new_value["email"] == "test_audit_updated@example.com"


def test_when_update_user_without_changes_then_no_log_generated(db_session, user_example):
    """
    Test cập nhật no-op không được sinh ra log.
    """
    # 1. Tạo user
    db_session.add(user_example)
    db_session.commit()

    # Xóa sạch log CREATE trước đó để test dễ hơn
    db_session.query(AuditLog).delete()
    db_session.commit()

    # 2. Gán lại giá trị cũ (không thay đổi) và commit
    user_example.name = "user_1"
    db_session.commit()

    # 3. Không được sinh thêm bất kỳ log nào
    log_count = db_session.query(AuditLog).count()
    assert log_count == 0


def test_when_delete_user_then_delete_audit_log_generated(db_session, user_example):
    """
    Test hành động xóa (DELETE) ghi lại trạng thái cũ của đối tượng.
    """
    # 1. Tạo user
    db_session.add(user_example)
    db_session.commit()

    # 2. Xóa user
    db_session.delete(user_example)
    db_session.commit()

    log = db_session.query(AuditLog).filter_by(
        table_name="users",
        target_id=str(user_example.user_id)
    ).order_by(AuditLog.id.desc()).first()
    
    assert log is not None
    assert log.action == "DELETE"
    assert log.old_value["name"] == "user_1"
    assert "password" not in log.old_value
    assert log.new_value is None


def test_when_transaction_rolled_back_then_no_orphaned_logs(db_session, user_example):
    """
    Test tính toàn vẹn transaction: Nếu nghiệp vụ chính bị rollback, audit log cũng phải bị hủy.
    """
    # 1. Thêm user mới và flush xuống DB để kích hoạt event listener
    db_session.add(user_example)
    db_session.flush()

    assert any(isinstance(x, AuditLog) for x in db_session.new)

    # 2. Rollback
    db_session.rollback()

    # 3. Đảm bảo toàn bộ log liên quan bị rollback sạch sẽ
    assert db_session.query(AuditLog).count() == 0


def test_when_api_request_processed_then_actor_id_captured_correctly(client, admin_token, db_session, user_example):
    """
    Test tích hợp: Khi cập nhật thông tin qua API endpoint, actor_id phải là ID của người dùng đã đăng nhập (g.current_user).
    """
    # 1. Seed user_example
    db_session.add(user_example)
    db_session.commit()

    # Xóa sạch log cũ của bước tạo
    db_session.query(AuditLog).delete()
    db_session.commit()

    # 2. Admin (admin_example có ID là 2) gửi request PUT cập nhật thông tin của User 1
    response = client.put(
        f"/admin/users/{user_example.user_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "name": "user_updated_by_admin",
            "email": "user_1@example.com",
            "is_active": True
        }
    )
    assert response.status_code == 200

    log = db_session.query(AuditLog).filter_by(
        table_name="users",
        target_id=str(user_example.user_id)
    ).order_by(AuditLog.id.desc()).first()
    
    assert log is not None
    assert log.action == "UPDATE"
    assert log.actor_id == 2
    assert log.new_value["name"] == "user_updated_by_admin"
