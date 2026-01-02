"""Add test column

Revision ID: 002
Revises: 001
Create Date: 2026-01-03 00:01:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add a new column to test table."""
    op.add_column('alembic_test', sa.Column('description', sa.Text(), nullable=True))


def downgrade() -> None:
    """Remove the test column."""
    op.drop_column('alembic_test', 'description')
