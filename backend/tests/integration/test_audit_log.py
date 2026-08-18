import pytest
from datetime import datetime, timezone
from app.models import User
from app.models.audit_log import AuditLog

@pytest.fixture(autouse=True, scope="module")
def setup_audit_listener():
    """
    Tự động gọi create_app(test_config={"TESTING": True}) một lần trước khi chạy các test trong module này
    để đảm bảo các event listener của SQLAlchemy được đăng ký mà không kết nối MySQL thật.
    """
    from app import create_app
    create_app(test_config={"TESTING": True})


def test_when_create_user_then_create_audit_log_generated(db_session, user_example):
    """
    Test hành động tạo mới (CREATE) phải sinh log và loại trừ các trường nhạy cảm như password.
    """
    # 1. Thêm một user mới
    db_session.add(user_example)
    db_session.commit()

    logs = db_session.query(AuditLog).filter_by(
        table_name="users", 
        target_id=str(user_example.user_id)
    ).all()
    
    assert len(logs) == 1
    log = logs[0]
    assert log.action == "CREATE"
    assert log.new_value is not None
    assert log.new_value["name"] == "user_1"
    assert log.new_value["email"] == "user_1@example.com"
    # Đảm bảo mật khẩu được che giấu dưới dạng mặt nạ
    assert log.new_value["password"] == "[REDACTED]"
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

    update_logs = db_session.query(AuditLog).filter_by(
        table_name="users",
        target_id=str(user_example.user_id),
        action="UPDATE"
    ).all()
    
    assert len(update_logs) == 1
    log = update_logs[0]
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

    delete_logs = db_session.query(AuditLog).filter_by(
        table_name="users",
        target_id=str(user_example.user_id),
        action="DELETE"
    ).all()
    
    assert len(delete_logs) == 1
    log = delete_logs[0]
    assert log.action == "DELETE"
    assert log.old_value["name"] == "user_1"
    # Đảm bảo mật khẩu được che giấu dưới dạng mặt nạ
    assert log.old_value["password"] == "[REDACTED]"
    assert log.new_value is None


def test_when_transaction_rolled_back_then_no_orphaned_logs(db_session, user_example):
    """
    Test tính toàn vẹn transaction: Nếu nghiệp vụ chính bị rollback, audit log cũng phải bị hủy.
    """
    initial_count = db_session.query(AuditLog).count()

    # 1. Thêm user mới và flush xuống DB để kích hoạt event listener
    db_session.add(user_example)
    db_session.flush()

    assert any(isinstance(x, AuditLog) for x in db_session.new)

    # 2. Rollback
    db_session.rollback()

    # 3. Đảm bảo toàn bộ log liên quan bị rollback sạch sẽ
    assert db_session.query(AuditLog).count() == initial_count


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

    # 2. Admin (admin_example có ID là 999) gửi request PUT cập nhật thông tin của User 1
    response = client.put(
        f"/admin/users/{user_example.user_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "name": "user_updated_by_admin",
            "email": "user_1@example.com",
        }
    )
    assert response.status_code == 200

    api_update_logs = db_session.query(AuditLog).filter_by(
        table_name="users",
        target_id=str(user_example.user_id),
        action="UPDATE"
    ).all()
    
    assert len(api_update_logs) == 1
    log = api_update_logs[0]
    assert log.action == "UPDATE"
    assert log.actor_id == 999
    assert log.new_value["name"] == "user_updated_by_admin"


def test_when_reset_password_then_actor_id_captured_correctly(client, db_session, user_example, mock_redis):
    """
    Test tích hợp: Khi reset password qua public API (chưa login), actor_id vẫn phải ghi nhận là ID của chính user đó.
    """
    # 1. Seed user_example vào DB
    db_session.add(user_example)
    db_session.commit()

    # Xóa log của bước tạo
    db_session.query(AuditLog).delete()
    db_session.commit()

    # 2. Mock Redis trả về user_id tương ứng với reset token
    mock_redis.get_user_id_by_reset_token.return_value = str(user_example.user_id)

    # 3. Gửi request POST reset-password (luồng này tự động sinh log vì password dùng mặt nạ)
    response = client.post(
        "/auth/reset-password",
        json={
            "reset_token": "valid_reset_token",
            "new_password": "new_secure_password_123",
            "confirm_password": "new_secure_password_123"
        }
    )
    assert response.status_code == 200

    # 4. Kiểm tra xem Audit Log ghi nhận đúng actor_id là user_id của chính người đó
    log = db_session.query(AuditLog).filter_by(
        table_name="users",
        target_id=str(user_example.user_id)
    ).order_by(AuditLog.id.desc()).first()

    assert log is not None
    assert log.action == "UPDATE"
    assert log.actor_id == user_example.user_id
    # Đảm bảo mật khẩu mới trong log được che giấu
    assert log.new_value["password"] == "[REDACTED]"
