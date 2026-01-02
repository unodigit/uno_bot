"""Add test table for rollback testing

Revision ID: 8cabb091cdfc
Revises: d280d291ddfc
Create Date: 2026-01-03 00:07:37.625269

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8cabb091cdfc'
down_revision: Union[str, Sequence[str], None] = 'd280d291ddfc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create a test table for rollback testing
    op.create_table(
        'test_table',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('created_at', sa.DateTime, server_default=sa.text('(CURRENT_TIMESTAMP)')),
        sa.Column('data', sa.Text, nullable=True),
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Drop the test table
    op.drop_table('test_table')
