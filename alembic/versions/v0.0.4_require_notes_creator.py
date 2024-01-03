"""Require creator ID for notes

Revision ID: v0.0.4
Revises: v0.0.3
Create Date: 2023-12-28 15:36:02.038563

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "v0.0.4"
down_revision = "v0.0.3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column("notes", "creator_id", existing_type=sa.INTEGER(), nullable=False)

def downgrade() -> None:
    op.alter_column("notes", "creator_id", existing_type=sa.INTEGER(), nullable=True)
