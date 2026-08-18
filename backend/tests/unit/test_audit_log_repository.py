from app.models.audit_log import AuditLog
from app.models.user import User
from app.repositories.audit_log_repository import AuditLogRepository


def test_audit_log_repo_get_by_id(db_session, user_example):
    db_session.add(user_example)
    db_session.commit()

    repo = AuditLogRepository(db=db_session)
    log = AuditLog(
        actor_id=user_example.user_id,
        action="UPDATE",
        table_name="users",
        target_id=str(user_example.user_id),
        old_value={"name": "old_name"},
        new_value={"name": "new_name"},
    )
    db_session.add(log)
    db_session.commit()

    found_log = repo.get_by_id(log.id)
    assert found_log is not None
    assert found_log.id == log.id
    assert found_log.action == "UPDATE"
    assert found_log.actor is not None
    assert found_log.actor.user_id == user_example.user_id


def test_audit_log_repo_get_by_id_not_found(db_session):
    repo = AuditLogRepository(db=db_session)
    assert repo.get_by_id("non-existent-uuid") is None


def test_audit_log_repo_get_by_cursor_pagination_and_filters(db_session, user_example):
    db_session.add(user_example)
    db_session.commit()

    # Xóa các log phát sinh tự động từ seed ban đầu để test chính xác
    db_session.query(AuditLog).delete()
    db_session.commit()

    repo = AuditLogRepository(db=db_session)

    log1 = AuditLog(
        actor_id=user_example.user_id,
        action="CREATE",
        table_name="users",
        target_id="101",
        new_value={"name": "user101"},
    )
    log2 = AuditLog(
        actor_id=user_example.user_id,
        action="UPDATE",
        table_name="users",
        target_id="102",
        old_value={"name": "old"},
        new_value={"name": "user102"},
    )
    log3 = AuditLog(
        actor_id=None,
        action="DELETE",
        table_name="roles",
        target_id="201",
    )
    db_session.add_all([log1, log2, log3])
    db_session.commit()

    # 1. Phân trang theo con trỏ: Trang 1 lấy 2 bản ghi
    page1_items, next_cursor, has_more = repo.get_by_cursor(limit=2)
    assert len(page1_items) == 2
    assert has_more is True
    assert next_cursor is not None
    assert next_cursor == page1_items[-1].id

    # 2. Trang 2 lấy tiếp bản ghi sau con trỏ next_cursor
    page2_items, next_cursor2, has_more2 = repo.get_by_cursor(limit=2, cursor=next_cursor)
    assert len(page2_items) >= 1
    assert has_more2 is False
    assert next_cursor2 is None

    # 3. Lọc theo action
    items, _, _ = repo.get_by_cursor(filters={"action": "CREATE"})
    assert len(items) >= 1
    assert any(i.target_id == "101" for i in items)

    # 4. Lọc theo table_name
    items, _, _ = repo.get_by_cursor(filters={"table_name": "roles"})
    assert len(items) >= 1
    assert any(i.target_id == "201" for i in items)

    # 5. Lọc theo target_id
    items, _, _ = repo.get_by_cursor(filters={"target_id": "102"})
    assert len(items) == 1
    assert items[0].action == "UPDATE"

    # 6. Lọc theo actor_id
    items, _, _ = repo.get_by_cursor(filters={"actor_id": user_example.user_id})
    assert len(items) >= 2

    # 7. Tìm kiếm theo search
    items, _, _ = repo.get_by_cursor(filters={"search": "102"})
    assert len(items) == 1
    assert items[0].target_id == "102"
