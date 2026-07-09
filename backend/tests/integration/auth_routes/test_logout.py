def test_logout_when_token_is_valid_return_200_and_blacklists_token(client, access_token, mock_redis):
    """
    Trường hợp token hợp lệ, đăng xuất thành công và đưa token vào blacklist
    """
    response = client.post(
        '/auth/logout',
        headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data["message"] == "Đăng xuất thành công"
    mock_redis.blacklist_token.assert_called_once()


def test_logout_when_no_token_return_401(client):
    """
    Trường hợp không gửi token kèm theo khi gọi logout
    """
    response = client.post('/auth/logout')

    assert response.status_code == 401


def test_logout_when_token_is_blacklisted_return_401(client, access_token, mock_redis):
    """
    Trường hợp gửi token đã bị blacklist từ trước khi logout
    """
    mock_redis.is_token_blacklisted.return_value = True

    response = client.post(
        '/auth/logout',
        headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == 401
