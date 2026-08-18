"""create_rbac_tables_and_seed_roles

Revision ID: 07
Revises: 06
Create Date: 2026-08-12 17:10:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

import uuid_utils as uuid

# revision identifiers, used by Alembic.
revision: str = '07'
down_revision: Union[str, Sequence[str], None] = '06'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 0. Chuyển đổi audit_logs.id từ INT sang UUIDv7 String(36) và khôi phục server_default cho created_at
    connection = op.get_bind()

    op.add_column('audit_logs', sa.Column('uuid_id', sa.String(length=36), nullable=True))

    # Sinh UUIDv7 bằng Python dựa theo đúng mốc thời gian created_at của từng log cũ
    logs = connection.execute(sa.text("SELECT id, created_at FROM audit_logs")).fetchall()
    for row in logs:
        log_id, created_at = row[0], row[1]
        ts_ms = int(created_at.timestamp() * 1000) if created_at else None
        log_uuid = str(uuid.uuid7(ts_ms)) if ts_ms else str(uuid.uuid7())
        connection.execute(
            sa.text("UPDATE audit_logs SET uuid_id = :uuid WHERE id = :id"),
            {"uuid": log_uuid, "id": log_id}
        )

    op.drop_column('audit_logs', 'id')
    op.alter_column('audit_logs', 'uuid_id', new_column_name='id', existing_type=sa.String(length=36), nullable=False)
    op.create_primary_key('pk_audit_logs', 'audit_logs', ['id'])

    # Khôi phục server_default cho cột created_at của audit_logs trên MySQL
    op.alter_column(
        'audit_logs',
        'created_at',
        existing_type=sa.DateTime(timezone=True),
        nullable=True,
        server_default=sa.text('now()')
    )

    # 1. Tạo bảng roles
    op.create_table(
        'roles',
        sa.Column('role_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('is_system', sa.Boolean(), server_default='0', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('role_id'),
        sa.UniqueConstraint('name'),
        sa.UniqueConstraint('code')
    )

    # 2. Tạo bảng permissions
    op.create_table(
        'permissions',
        sa.Column('permission_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('resource', sa.String(length=50), nullable=False),
        sa.Column('action', sa.String(length=50), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('permission_id'),
        sa.UniqueConstraint('resource', 'action', name='uq_permission_resource_action')
    )

    # Thêm cột updated_at, must_change_password và deleted_at cho bảng users hiện tại
    op.add_column('users', sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False))
    op.add_column('users', sa.Column('must_change_password', sa.Boolean(), server_default='0', nullable=False))
    op.add_column('users', sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True))

    # 3. Tạo bảng trung gian user_roles
    op.create_table(
        'user_roles',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('role_id', sa.Integer(), index=True, nullable=False),
        sa.ForeignKeyConstraint(['role_id'], ['roles.role_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('user_id', 'role_id')
    )

    # 4. Tạo bảng trung gian role_permissions
    op.create_table(
        'role_permissions',
        sa.Column('role_id', sa.Integer(), nullable=False),
        sa.Column('permission_id', sa.Integer(), index=True, nullable=False),
        sa.ForeignKeyConstraint(['permission_id'], ['permissions.permission_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['role_id'], ['roles.role_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('role_id', 'permission_id')
    )

    # 5. Seed dữ liệu role hệ thống mặc định (admin & user)
    op.execute("""
        INSERT INTO roles (name, code, is_system) 
        VALUES 
            ('Administrator', 'admin', TRUE),
            ('Regular User', 'user', TRUE);
    """)

    # 6. Seed các permission mặc định với resource và action chuẩn CRUD
    op.execute("""
        INSERT INTO permissions (name, resource, action, description)
        VALUES
            ('Read Users', 'users', 'read', 'View users list and details'),
            ('Create User', 'users', 'create', 'Create new users'),
            ('Update User', 'users', 'update', 'Update user details'),
            ('Delete User', 'users', 'delete', 'Soft delete or restore users'),
            ('Read Roles', 'roles', 'read', 'View roles and assigned permissions'),
            ('Create Role', 'roles', 'create', 'Create new roles'),
            ('Update Role', 'roles', 'update', 'Update role details and permissions'),
            ('Delete Role', 'roles', 'delete', 'Delete custom roles'),
            ('Assign Roles to User', 'roles', 'assign', 'Assign or revoke roles from users'),
            ('Read Permissions', 'permissions', 'read', 'View system permissions list'),
            ('Read Audit Logs', 'audit_logs', 'read', 'View system audit logs');
    """)

    # 7. Gán toàn bộ permissions cho Role Admin
    op.execute("""
        INSERT INTO role_permissions (role_id, permission_id)
        SELECT r.role_id, p.permission_id
        FROM roles r, permissions p
        WHERE r.code = 'admin';
    """)

    # 8. Data Migration: Map dữ liệu is_admin của users hiện tại sang user_roles
    op.execute("""
        INSERT INTO user_roles (user_id, role_id)
        SELECT u.user_id, r.role_id
        FROM users u
        JOIN roles r ON (CASE WHEN u.is_admin = 1 OR u.is_admin IS TRUE THEN 'admin' ELSE 'user' END) = r.code;
    """)


def downgrade() -> None:
    connection = op.get_bind()
    inspector = sa.inspect(connection)

    # 1. Xóa các bảng trung gian phụ trước (nếu tồn tại)
    connection.execute(sa.text("DROP TABLE IF EXISTS role_permissions"))
    connection.execute(sa.text("DROP TABLE IF EXISTS user_roles"))

    # 2. Xóa các bảng chính (nếu tồn tại)
    connection.execute(sa.text("DROP TABLE IF EXISTS permissions"))
    connection.execute(sa.text("DROP TABLE IF EXISTS roles"))

    # 3. Xóa các cột đã thêm vào bảng users (nếu tồn tại)
    user_cols = [c['name'] for c in inspector.get_columns('users')]
    if 'deleted_at' in user_cols:
        op.drop_column('users', 'deleted_at')
    if 'must_change_password' in user_cols:
        op.drop_column('users', 'must_change_password')
    if 'updated_at' in user_cols:
        op.drop_column('users', 'updated_at')

    # 4. Rollback audit_logs.id về INT autoincrement (nếu cột id đang là String/UUID)
    audit_cols = {c['name']: c for c in inspector.get_columns('audit_logs')}
    if 'id' in audit_cols and not isinstance(audit_cols['id']['type'], sa.Integer):
        op.drop_column('audit_logs', 'id')
        connection.execute(sa.text("ALTER TABLE audit_logs ADD COLUMN id INT NOT NULL AUTO_INCREMENT PRIMARY KEY"))
