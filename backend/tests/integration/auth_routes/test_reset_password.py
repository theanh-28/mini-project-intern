import pytest
from app.models import User
from app.core.security import verify_password

def test_when_reset_password_valid_token_then_return_200_and_password_updated(client, db_session, insert_user, mock_redis):
    """
    Kịch bản: Đặt lại mật khẩu thành công với token hợp lệ.
    Kết quả: Trả về 200, đổi mật khẩu trong DB, thu hồi session cũ và hủy reset token.
    """
    # 1. Giả lập token reset liên kết tới user_id của insert_user
    mock_redis.get_user_id_by_reset_token.return_value = str(insert_user.user_id)

    # 2. Gửi request reset password
    response = client.post(
        "/auth/reset-password",
        json={
            "reset_token": "valid_reset_token",
            "new_password": "NewSecurePassword123",
            "confirm_password": "NewSecurePassword123"
        }
    )

    assert response.status_code == 200

    # 3. Kiểm tra DB: Mật khẩu mới đã được cập nhật chính xác và đã băm
    db_session.refresh(insert_user)
    assert verify_password("NewSecurePassword123", insert_user.password)

    # 4. Kiểm tra Redis: Hủy reset token và thu hồi các JWT token cũ
    mock_redis.invalidate_reset_token.assert_called_once_with(reset_token="valid_reset_token")
    mock_redis.revoke_user_sessions.assert_called_once_with(user_id=insert_user.user_id, ttl=3600)


def test_when_reset_password_confirm_mismatch_then_return_400_validation_error(client, insert_user, mock_redis):
    """
    Kịch bản: Đổi mật khẩu nhưng confirm_password không trùng khớp.
    Kết quả: Trả về 400 Validation Error.
    """
    response = client.post(
        "/auth/reset-password",
        json={
            "reset_token": "valid_reset_token",
            "new_password": "NewSecurePassword123",
            "confirm_password": "DifferentPassword123"
        }
    )

    assert response.status_code == 400
    data = response.get_json()
    assert data["code"] == "VALIDATION_ERROR"

def test_when_reset_password_invalid_token_then_return_401_invalid_token(client, mock_redis):
    """
    Kịch bản: Sử dụng token hết hạn hoặc không tồn tại.
    Kết quả: Trả về 401 Unauthorized do token không hợp lệ.
    """
    mock_redis.get_user_id_by_reset_token.return_value = None

    response = client.post(
        "/auth/reset-password",
        json={
            "reset_token": "expired_token",
            "new_password": "NewSecurePassword123",
            "confirm_password": "NewSecurePassword123"
        }
    )

    assert response.status_code == 401
    data = response.get_json()
    assert data["code"] == "INVALID_TOKEN"
