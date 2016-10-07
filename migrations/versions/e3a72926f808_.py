"""Adds table for 2 factor secret and checking if active

Revision ID: e3a72926f808
Revises: c3803ac9b7dd
Create Date: 2016-08-10 19:12:49.647496

"""

# revision identifiers, used by Alembic.
revision = 'e3a72926f808'
down_revision = 'c3803ac9b7dd'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('postmaster_admins', sa.Column('otp_active', sa.Boolean(), nullable=True))
    op.add_column('postmaster_admins', sa.Column('otp_secret', sa.String(length=16), nullable=True))


def downgrade():
    op.drop_column('postmaster_admins', 'otp_secret')
    op.drop_column('postmaster_admins', 'otp_active')
