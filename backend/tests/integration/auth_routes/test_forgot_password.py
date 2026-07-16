import pytest
from app.models import User

def test_when_forgot_password_valid_email_then_return_200_and_token_saved(client, db_session, insert_user, mock_redis):
    """
    Kịch bản: Yêu cầu quên mật khẩu với email hợp lệ.
    Kết quả: Trả về 200, lưu token reset vào Redis.
    """
    response = client.post(
        "/auth/forgot-password",
        json={"email": insert_user.email}
    )

    assert response.status_code == 200
    
    # Kiểm tra Redis được gọi để lưu token
    mock_redis.save_reset_token.assert_called_once()
    call_kwargs = mock_redis.save_reset_token.call_args[1]
    assert call_kwargs["user_id"] == insert_user.user_id


def test_when_forgot_password_email_not_exist_then_return_200_without_token(client, db_session, mock_redis):
    """
    Kịch bản: Yêu cầu quên mật khẩu với email KHÔNG tồn tại.
    Kết quả: Trả về 200, không lưu gì vào Redis.
    """
    response = client.post(
        "/auth/forgot-password",
        json={"email": "non_existent_email@example.com"}
    )

    assert response.status_code == 200

    # Đảm bảo không lưu gì vào Redis
    mock_redis.save_reset_token.assert_not_called()


def test_when_forgot_password_inactive_user_then_return_200_without_token(client, db_session, insert_user, mock_redis):
    """
    Kịch bản: Yêu cầu quên mật khẩu với tài khoản đang bị khóa (inactive).
    Kết quả: Trả về 200, không lưu gì vào Redis.
    """
    insert_user.is_active = False
    db_session.commit()

    response = client.post(
        "/auth/forgot-password",
        json={"email": insert_user.email}
    )

    assert response.status_code == 200
    mock_redis.save_reset_token.assert_not_called()
