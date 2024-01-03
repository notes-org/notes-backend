"""Store hashed passwords

... and drop auth0_sub column

Revision ID: v0.0.3
Revises: v0.0.2
Create Date: 2023-12-27 17:40:43.576481

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'v0.0.3'
down_revision = 'v0.0.2'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('users', sa.Column('hashed_password', sa.String(), nullable=False))
    op.drop_index('ix_users_auth0_sub', table_name='users')
    op.drop_column('users', 'auth0_sub')


def downgrade() -> None:
    op.add_column('users', sa.Column('auth0_sub', sa.String(), autoincrement=False, nullable=False))
    op.create_index('ix_users_auth0_sub', 'users', ['auth0_sub'], unique=False)
    op.drop_column('users', 'hashed_password')
