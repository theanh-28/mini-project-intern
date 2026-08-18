import pytest
from unittest.mock import MagicMock
from app.services.audit_log_service import AuditLogService
from app.core.exceptions import AuditLogNotFoundError
from app.models.audit_log import AuditLog


@pytest.fixture
def mock_audit_log_repo():
    return MagicMock()


@pytest.fixture
def audit_log_service(mock_audit_log_repo):
    return AuditLogService(audit_log_repository=mock_audit_log_repo)


def test_get_list_audit_logs_cursor(audit_log_service, mock_audit_log_repo):
    mock_log = AuditLog(id="uuid-1", action="CREATE", table_name="users", target_id="1")
    mock_audit_log_repo.get_by_cursor.return_value = ([mock_log], None, False)

    logs, next_cursor, has_more = audit_log_service.get_list_audit_logs(
        limit=10,
        cursor=None,
        filters={"action": "CREATE"},
    )

    assert len(logs) == 1
    assert logs[0].id == "uuid-1"
    assert next_cursor is None
    assert has_more is False
    mock_audit_log_repo.get_by_cursor.assert_called_once_with(
        limit=10,
        cursor=None,
        filters={"action": "CREATE"},
    )


def test_get_audit_log_by_id_success(audit_log_service, mock_audit_log_repo):
    mock_log = AuditLog(id="uuid-1", action="UPDATE", table_name="users", target_id="1")
    mock_audit_log_repo.get_by_id.return_value = mock_log

    result = audit_log_service.get_audit_log_by_id("uuid-1")

    assert result.id == "uuid-1"
    assert result.action == "UPDATE"
    mock_audit_log_repo.get_by_id.assert_called_once_with("uuid-1")


def test_get_audit_log_by_id_not_found(audit_log_service, mock_audit_log_repo):
    mock_audit_log_repo.get_by_id.return_value = None

    with pytest.raises(AuditLogNotFoundError) as exc_info:
        audit_log_service.get_audit_log_by_id("non-existent-uuid")

    assert exc_info.value.status_code == 404
    assert exc_info.value.code_error == "AUDIT_LOG_NOT_FOUND"


def test_get_user_audit_timeline_cursor(audit_log_service, mock_audit_log_repo):
    mock_log = AuditLog(id="uuid-1", action="UPDATE", table_name="users", target_id="10")
    mock_audit_log_repo.get_by_cursor.return_value = ([mock_log], "uuid-1", True)

    logs, next_cursor, has_more = audit_log_service.get_user_audit_timeline(
        user_id=10,
        limit=20,
        cursor="prev-uuid",
    )

    assert len(logs) == 1
    assert next_cursor == "uuid-1"
    assert has_more is True
    mock_audit_log_repo.get_by_cursor.assert_called_once_with(
        limit=20,
        cursor="prev-uuid",
        filters={"table_name": "users", "target_id": "10"},
    )
