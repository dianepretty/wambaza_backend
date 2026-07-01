"""add swahili fields to articles

Revision ID: a3f1c8e92b47
Revises: e58436c56eda
Create Date: 2026-07-01

"""
from alembic import op
import sqlalchemy as sa

revision = 'a3f1c8e92b47'
down_revision = 'e58436c56eda'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('articles', sa.Column('title_sw', sa.String(), nullable=True))
    op.add_column('articles', sa.Column('content_sw', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('articles', 'content_sw')
    op.drop_column('articles', 'title_sw')
