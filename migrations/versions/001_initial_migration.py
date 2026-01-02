"""Initial migration

Revision ID: 001
Revises:
Create Date: 2026-01-03 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create initial tables."""
    op.create_table(
        'alembic_test',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
    )
    op.create_index('ix_alembic_test_name', 'alembic_test', ['name'])


def downgrade() -> None:
    """Drop initial tables."""
    op.drop_index('ix_alembic_test_name', table_name='alembic_test')
    op.drop_table('alembic_test')
