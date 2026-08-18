"""add ip_address column to audit_logs table

Revision ID: 09
Revises: 08
Create Date: 2026-08-18

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '09'
down_revision: Union[str, Sequence[str], None] = '08'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    connection = op.get_bind()
    cols = [c['name'] for c in sa.inspect(connection).get_columns('audit_logs')]
    if 'ip_address' not in cols:
        op.add_column('audit_logs', sa.Column('ip_address', sa.String(length=45), nullable=True))


def downgrade() -> None:
    connection = op.get_bind()
    cols = [c['name'] for c in sa.inspect(connection).get_columns('audit_logs')]
    if 'ip_address' in cols:
        op.drop_column('audit_logs', 'ip_address')
