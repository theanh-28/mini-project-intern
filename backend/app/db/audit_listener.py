import logging
from datetime import datetime, date
from decimal import Decimal
from uuid import UUID
from flask import g, request, has_request_context
from sqlalchemy.orm.attributes import get_history

from app.models.audit_log import AuditLog

logger = logging.getLogger(__name__)


def serialize_field(val):
    """
    Chuyển đổi các kiểu dữ liệu không được hỗ trợ bởi JSON (như datetime, Decimal, UUID)
    thành dạng chuỗi hoặc số thích hợp để lưu trữ an toàn trong cột JSON.
    """
    if isinstance(val, (datetime, date)):
        return val.isoformat()
    if isinstance(val, Decimal):
        return float(val)
    if isinstance(val, UUID):
        return str(val)
    return val


def get_current_actor_id():
    """
    Lấy actor_id từ request context của flask
    """
    try:
        if has_request_context():
            current_user = getattr(g, "current_user", None)
            if current_user:
                sub = current_user.get("sub")
                if sub is not None:
                    return int(sub)
    except (RuntimeError, ValueError, TypeError):
        # Tránh crash nếu ngoài request context hoặc sub bị thiếu/sai định dạng
        pass
    return None


def get_current_client_ip():
    """
    Lấy IP client từ request context của Flask.
    Hỗ trợ lấy IP thật qua proxy/Gateway (Kong Header X-Forwarded-For, X-Real-IP).
    """
    try:
        if has_request_context():
            forwarded = request.headers.get("X-Forwarded-For")
            if forwarded:
                return forwarded.split(",")[0].strip()
            real_ip = request.headers.get("X-Real-IP")
            if real_ip:
                return real_ip.strip()
            return request.remote_addr
    except Exception:
        pass
    return None


def get_changed_values(obj):
    """
    Kiểm tra giá trị cũ và mới của các cột thực sự thay đổi bằng get_history.
    Trả về (old_values, new_values).
    """
    old_values = {}
    new_values = {}

    # Lấy danh sách các trường nhạy cảm cần loại hoặc che giấu
    exclude_fields = getattr(obj, "__audit_exclude__", set())
    mask_fields = getattr(obj, "__audit_mask__", set())

    # Duyệt qua các thuộc tính đại diện cho column của model
    for prop in obj.__mapper__.iterate_properties:
        if hasattr(prop, "columns"):
            attr_name = prop.key

            # Bỏ qua trường nhạy cảm loại trừ
            if attr_name in exclude_fields:
                continue

            history = get_history(obj, attr_name)
            if history.has_changes():
                # history.deleted chứa giá trị cũ trước khi thay đổi
                if history.deleted:
                    if attr_name in mask_fields:
                        old_values[attr_name] = "[REDACTED]"
                    else:
                        old_values[attr_name] = serialize_field(history.deleted[0])

                # history.added chứa giá trị mới được gán
                if history.added:
                    if attr_name in mask_fields:
                        new_values[attr_name] = "[REDACTED]"
                    else:
                        new_values[attr_name] = serialize_field(history.added[0])
    
    return (old_values, new_values)


def before_flush_listener(session, flush_context, instances=None):
    """
    SQLAlchemy event listener bắt sự kiện trước khi session thực hiện flush dữ liệu xuống db
    """
    actor_id = get_current_actor_id()
    ip_address = get_current_client_ip()
    pending_logs = []

    # 1. Xử lý khi tạo mới đối tượng (CREATE - session.new)
    for obj in session.new:
        if isinstance(obj, AuditLog):
            continue    # Không log chính bảng audit_logs tránh vòng lặp

        exclude_fields = getattr(obj, "__audit_exclude__", set())
        mask_fields = getattr(obj, "__audit_mask__", set())
        new_values = {}

        # Lấy tất cả giá trị ban đầu trừ trường nhạy cảm
        for prop in obj.__mapper__.iterate_properties:
            if hasattr(prop, "columns"):
                attr_name = prop.key
                if attr_name not in exclude_fields:
                    if attr_name in mask_fields:
                        new_values[attr_name] = "[REDACTED]"
                    else:
                        new_values[attr_name] = serialize_field(getattr(obj, attr_name))

        log = AuditLog(
            actor_id=actor_id,
            action="CREATE",
            table_name=obj.__tablename__,
            target_id=None,   # Điền ở after_flush
            old_value=None,
            new_value=new_values,
            ip_address=ip_address,
        )
        pending_logs.append((obj, log))

    # 2. Xử lý khi cập nhật đối tượng (UPDATE - session.dirty)
    for obj in session.dirty:
        if isinstance(obj, AuditLog):
            continue     # Không log chính bảng audit_logs tránh vòng lặp
        
        old_values, new_values = get_changed_values(obj)

        if not old_values and not new_values:
            continue

        log = AuditLog(
            actor_id=actor_id,
            action="UPDATE",
            table_name=obj.__tablename__,
            target_id=None,   # Điền ở after_flush
            old_value=old_values,
            new_value=new_values,
            ip_address=ip_address,
        )
        pending_logs.append((obj, log))

    # 3. Xử lý khi xóa đối tượng (DELETE - session.deleted)
    for obj in session.deleted:
        if isinstance(obj, AuditLog):
            continue    # Không log chính bảng audit_logs tránh vòng lặp

        exclude_fields = getattr(obj, "__audit_exclude__", set())
        mask_fields = getattr(obj, "__audit_mask__", set())
        old_values = {}

        # Ghi lại toàn bộ dữ liệu trước khi xóa
        for prop in obj.__mapper__.iterate_properties:
            if hasattr(prop, "columns"):
                attr_name = prop.key
                if attr_name not in exclude_fields:
                    if attr_name in mask_fields:
                        old_values[attr_name] = "[REDACTED]"
                    else:
                        old_values[attr_name] = serialize_field(getattr(obj, attr_name))

        log = AuditLog(
            actor_id=actor_id,
            action="DELETE",
            table_name=obj.__tablename__,
            target_id=None,  
            old_value=old_values,
            new_value=None,
            ip_address=ip_address,
        )
        pending_logs.append((obj, log))

    # Lưu tạm vào session info
    session.info['pending_audit_log'] = pending_logs


def after_flush_listener(session, flush_context):
    """
    SQLAlchemy event listener bắt sự kiện sau khi session thực hiện flush dữ liệu xuống db
    Cho cái giá trị khóa chính default ở server db
    """
    pending_logs = session.info.pop('pending_audit_log', [])

    for obj, log in pending_logs:
        if log.target_id is None:
            pk_cols = obj.__mapper__.primary_key
            pk_values = [str(getattr(obj, col.name)) for col in pk_cols]
            pk_value = "-".join(pk_values)

            log.target_id = pk_value
            if isinstance(log.new_value, dict):
                # Tránh trường hợp delete => new_value = None
                for col in pk_cols:
                    log.new_value[col.name] = str(getattr(obj, col.name))
        
        session.add(log)
