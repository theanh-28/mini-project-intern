"""drop is_admin column from users table

Revision ID: 08
Revises: 07
Create Date: 2026-08-17

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '08'
down_revision: Union[str, Sequence[str], None] = '07'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    connection = op.get_bind()
    user_cols = [c['name'] for c in sa.inspect(connection).get_columns('users')]
    if 'is_admin' in user_cols:
        op.drop_column('users', 'is_admin')


def downgrade() -> None:
    connection = op.get_bind()
    user_cols = [c['name'] for c in sa.inspect(connection).get_columns('users')]
    if 'is_admin' not in user_cols:
        op.add_column('users', sa.Column('is_admin', sa.Boolean(), server_default='0', nullable=False))
