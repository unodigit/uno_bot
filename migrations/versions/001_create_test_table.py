"""Create test table for rollback testing

Revision ID: 001
Revises:
Create Date: 2026-01-03

"""
from alembic import op
import sqlalchemy as sa

revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """Create test table."""
    op.create_table(
        'rollback_test_table',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
    )


def downgrade():
    """Drop test table."""
    op.drop_table('rollback_test_table')
