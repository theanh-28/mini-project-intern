"""create_rbac_tables_and_seed_roles

Revision ID: 07
Revises: 06
Create Date: 2026-08-12 17:10:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '07'
down_revision: Union[str, Sequence[str], None] = '06'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
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

    # Thêm cột updated_at cho bảng users hiện tại
    op.add_column('users', sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False))

    # Tạo index cho actor_id ở bảng audit_logs hiện tại
    op.create_index(op.f('ix_audit_logs_actor_id'), 'audit_logs', ['actor_id'], unique=False)

    # 3. Tạo bảng trung gian user_roles
    op.create_table(
        'user_roles',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('role_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['role_id'], ['roles.role_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('user_id', 'role_id')
    )

    # 4. Tạo bảng trung gian role_permissions
    op.create_table(
        'role_permissions',
        sa.Column('role_id', sa.Integer(), nullable=False),
        sa.Column('permission_id', sa.Integer(), nullable=False),
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

    # 6. Seed các permission mặc định với resource và action
    op.execute("""
        INSERT INTO permissions (name, resource, action, description)
        VALUES
            ('Read Users', 'users', 'read', 'View users list and details'),
            ('Create User', 'users', 'create', 'Create new users'),
            ('Update User', 'users', 'update', 'Update user details'),
            ('Delete User', 'users', 'delete', 'Soft delete or restore users'),
            ('Manage Roles', 'roles', 'manage', 'Create and assign roles'),
            ('Read Permissions', 'permissions', 'read', 'View system permissions list'),
            ('Manage Permissions', 'permissions', 'manage', 'Create and update system permissions');
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
        JOIN roles r ON (CASE WHEN u.is_admin = TRUE THEN 'admin' ELSE 'user' END) = r.code;
    """)


def downgrade() -> None:
    op.drop_index(op.f('ix_audit_logs_actor_id'), table_name='audit_logs')
    op.drop_column('users', 'updated_at')
    op.drop_table('role_permissions')
    op.drop_table('user_roles')
    op.drop_table('permissions')
    op.drop_table('roles')
