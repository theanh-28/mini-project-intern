from app.models.audit_log import AuditLog
from app.models.user import User


def test_get_audit_logs_as_admin_return_200_and_list(client, admin_token, db_session, user_example):
    db_session.add(user_example)
    db_session.commit()

    # 1. Tạo các bản ghi AuditLog mẫu
    log1 = AuditLog(
        actor_id=user_example.user_id,
        action="UPDATE",
        table_name="users",
        target_id=str(user_example.user_id),
        old_value={"name": "old_name"},
        new_value={"name": "new_name"},
    )
    log2 = AuditLog(
        actor_id=None,
        action="CREATE",
        table_name="users",
        target_id="999",
        new_value={"name": "created_user"},
    )
    db_session.add_all([log1, log2])
    db_session.commit()

    # 2. Admin gọi API lấy danh sách Audit Logs (Cursor-based)
    response = client.get(
        "/admin/audit-logs?limit=20",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200
    data = response.get_json()
    assert "audit_logs" in data
    assert "limit" in data
    assert "has_more" in data
    assert data["limit"] == 20
    assert len(data["audit_logs"]) >= 2

    # Kiểm tra cấu trúc bản ghi (danh sách rút gọn không chứa old_value / new_value)
    first_log = next(item for item in data["audit_logs"] if item["id"] == log1.id)
    assert first_log["action"] == "UPDATE"
    assert first_log["table_name"] == "users"
    assert first_log["actor_id"] == user_example.user_id
    assert first_log["actor"] is not None
    assert first_log["actor"]["name"] == user_example.name
    assert "old_value" not in first_log
    assert "new_value" not in first_log


def test_get_audit_logs_with_cursor_pagination(client, admin_token, db_session, user_example):
    db_session.add(user_example)
    db_session.commit()

    db_session.query(AuditLog).delete()
    db_session.commit()

    log1 = AuditLog(actor_id=user_example.user_id, action="CREATE", table_name="users", target_id="1")
    log2 = AuditLog(actor_id=user_example.user_id, action="UPDATE", table_name="users", target_id="2")
    log3 = AuditLog(actor_id=user_example.user_id, action="DELETE", table_name="users", target_id="3")
    db_session.add_all([log1, log2, log3])
    db_session.commit()

    # Trang 1: lấy 2 items
    res1 = client.get(
        "/admin/audit-logs?limit=2",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert res1.status_code == 200
    data1 = res1.get_json()
    assert len(data1["audit_logs"]) == 2
    assert data1["has_more"] is True
    assert data1["next_cursor"] is not None

    # Trang 2: truyền cursor lấy tiếp item còn lại
    res2 = client.get(
        f"/admin/audit-logs?limit=2&cursor={data1['next_cursor']}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert res2.status_code == 200
    data2 = res2.get_json()
    assert len(data2["audit_logs"]) == 1
    assert data2["has_more"] is False
    assert data2["next_cursor"] is None


def test_get_audit_logs_with_filter_and_search(client, admin_token, db_session, user_example):
    db_session.add(user_example)
    db_session.commit()

    log1 = AuditLog(
        actor_id=user_example.user_id,
        action="CREATE",
        table_name="custom_users_table",
        target_id="501",
        new_value={"name": "unique_keyword_target"},
    )
    log2 = AuditLog(
        actor_id=user_example.user_id,
        action="DELETE",
        table_name="custom_roles_table",
        target_id="502",
    )
    db_session.add_all([log1, log2])
    db_session.commit()

    # 1. Lọc theo action=DELETE
    res_action = client.get(
        "/admin/audit-logs?action=DELETE",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert res_action.status_code == 200
    data_action = res_action.get_json()
    assert all(item["action"] == "DELETE" for item in data_action["audit_logs"])

    # 2. Lọc theo table_name=custom_roles_table
    res_table = client.get(
        "/admin/audit-logs?table_name=custom_roles_table",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert res_table.status_code == 200
    data_table = res_table.get_json()
    assert all(item["table_name"] == "custom_roles_table" for item in data_table["audit_logs"])

    # 3. Tìm kiếm theo search (khớp target_id)
    res_search = client.get(
        "/admin/audit-logs?search=501",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert res_search.status_code == 200
    data_search = res_search.get_json()
    assert len(data_search["audit_logs"]) == 1
    assert data_search["audit_logs"][0]["target_id"] == "501"


def test_get_audit_logs_as_regular_user_return_403(client, access_token):
    response = client.get(
        "/admin/audit-logs",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 403
    data = response.get_json()
    assert data["code"] == "PERMISSION_DENIED"


def test_get_audit_logs_unauthenticated_return_401(client):
    response = client.get("/admin/audit-logs")
    assert response.status_code == 401


def test_get_audit_log_detail_success(client, admin_token, db_session, user_example):
    db_session.add(user_example)
    db_session.commit()

    log = AuditLog(
        actor_id=user_example.user_id,
        action="UPDATE",
        table_name="users",
        target_id=str(user_example.user_id),
        old_value={"name": "before"},
        new_value={"name": "after"},
    )
    db_session.add(log)
    db_session.commit()

    response = client.get(
        f"/admin/audit-logs/{log.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data["id"] == log.id
    assert data["action"] == "UPDATE"
    assert data["old_value"]["name"] == "before"
    assert data["new_value"]["name"] == "after"
    assert data["actor"] is not None
    assert data["actor"]["user_id"] == user_example.user_id


def test_get_audit_log_detail_not_found_return_404(client, admin_token):
    response = client.get(
        "/admin/audit-logs/018f0000-0000-7000-8000-000000000000",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 404
    data = response.get_json()
    assert data["code"] == "AUDIT_LOG_NOT_FOUND"


def test_get_user_audit_timeline(client, admin_token, db_session, user_example):
    db_session.add(user_example)
    db_session.commit()

    log1 = AuditLog(
        actor_id=999,
        action="UPDATE",
        table_name="users",
        target_id=str(user_example.user_id),
        old_value={"is_active": True},
        new_value={"is_active": False},
    )
    log2 = AuditLog(
        actor_id=999,
        action="UPDATE",
        table_name="users",
        target_id="888",  # User khác
        old_value={"name": "other"},
        new_value={"name": "other_updated"},
    )
    db_session.add_all([log1, log2])
    db_session.commit()

    response = client.get(
        f"/admin/users/{user_example.user_id}/audit-logs",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200
    data = response.get_json()
    assert "audit_logs" in data
    assert "limit" in data
    assert "has_more" in data
    assert any(item["target_id"] == str(user_example.user_id) for item in data["audit_logs"])
    assert all(item["target_id"] == str(user_example.user_id) for item in data["audit_logs"])
