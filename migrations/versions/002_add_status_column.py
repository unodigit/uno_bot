"""Add status column for rollback testing

Revision ID: 002
Revises: 001
Create Date: 2026-01-03

"""
from alembic import op
import sqlalchemy as sa

revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade():
    """Add status column."""
    op.add_column('rollback_test_table', sa.Column('status', sa.String(50), nullable=True))


def downgrade():
    """Remove status column."""
    op.drop_column('rollback_test_table', 'status')
