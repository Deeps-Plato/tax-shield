"""add irs_reference to strategies

Revision ID: a1b2c3d4e5f6
Revises: 8d26c093010f
Create Date: 2026-03-04 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '8d26c093010f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('strategies', sa.Column('irs_reference', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('strategies', 'irs_reference')
