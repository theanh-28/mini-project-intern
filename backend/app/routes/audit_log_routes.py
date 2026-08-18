import logging
from flask import Blueprint, request, jsonify

from app.services.audit_log_service import get_audit_log_service
from app.schemas.audit_log import (
    AuditLogListItemResponse,
    AuditLogDetailResponse,
    AuditLogListRequest,
    AuditLogListResponse,
)
from app.routes.decorators import require_permission

audit_log_bp = Blueprint("audit_log", __name__)
logger = logging.getLogger(__name__)


@audit_log_bp.route("/admin/audit-logs", methods=["GET"])
@require_permission("audit_logs:read")
def get_audit_logs():
    """
    Endpoint lấy danh sách Audit Logs phân trang theo con trỏ (Cursor-based Pagination).
    """
    data = AuditLogListRequest(**(request.args.to_dict() if request.args else {}))

    audit_log_service = get_audit_log_service()

    filters = {
        "actor_id": data.actor_id,
        "action": data.action,
        "table_name": data.table_name,
        "target_id": data.target_id,
        "search": data.search,
        "created_at_from": data.created_at_from,
        "created_at_to": data.created_at_to,
    }

    logs, next_cursor, has_more = audit_log_service.get_list_audit_logs(
        limit=data.limit,
        cursor=data.cursor,
        filters=filters,
    )

    response_data = AuditLogListResponse(
        audit_logs=[AuditLogListItemResponse.model_validate(log) for log in logs],
        limit=data.limit,
        next_cursor=next_cursor,
        has_more=has_more,
    )

    return jsonify(response_data.model_dump(mode="json")), 200


@audit_log_bp.route("/admin/audit-logs/<string:log_id>", methods=["GET"])
@require_permission("audit_logs:read")
def get_audit_log_detail(log_id: str):
    """
    Endpoint lấy chi tiết đầy đủ một bản ghi Audit Log (bao gồm old_value và new_value) theo ID.
    """
    audit_log_service = get_audit_log_service()
    log = audit_log_service.get_audit_log_by_id(log_id=log_id)

    response_data = AuditLogDetailResponse.model_validate(log)
    return jsonify(response_data.model_dump(mode="json")), 200


@audit_log_bp.route("/admin/users/<int:user_id>/audit-logs", methods=["GET"])
@require_permission("audit_logs:read")
def get_user_audit_timeline(user_id: int):
    """
    Endpoint lấy dòng thời gian ghi vết kiểm toán của riêng một tài khoản User.
    """
    limit = request.args.get("limit", default=20, type=int)
    cursor = request.args.get("cursor", default=None, type=str)

    audit_log_service = get_audit_log_service()
    logs, next_cursor, has_more = audit_log_service.get_user_audit_timeline(
        user_id=user_id,
        limit=limit,
        cursor=cursor,
    )

    response_data = AuditLogListResponse(
        audit_logs=[AuditLogListItemResponse.model_validate(log) for log in logs],
        limit=limit,
        next_cursor=next_cursor,
        has_more=has_more,
    )

    return jsonify(response_data.model_dump(mode="json")), 200
