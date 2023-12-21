"""Create users table

Revision ID: v0.0.2
Revises: v0.0.1
Create Date: 2023-07-06 13:49:27.120555

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'v0.0.2'
down_revision = 'v0.0.1'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('uuid', sa.UUID(), nullable=False),
    sa.Column('auth0_sub', sa.String(), nullable=False),
    sa.Column('username', sa.String(), nullable=False),
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('is_superuser', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('uuid')
    )
    op.create_index(op.f('ix_users_auth0_sub'), 'users', ['auth0_sub'], unique=True)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    op.add_column('notes', sa.Column('creator_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'notes', 'users', ['creator_id'], ['id'])


def downgrade() -> None:
    op.drop_column('notes', 'creator_id')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_index(op.f('ix_users_auth0_sub'), table_name='users')
    op.drop_table('users')
