"""inital migration

Revision ID: 8088a198f0fb
Revises: 
Create Date: 2025-06-05 02:30:53.932103

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8088a198f0fb'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('devices',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=80), nullable=False),
    sa.Column('type', sa.String(length=20), nullable=False),
    sa.Column('status', sa.Boolean(), nullable=True),
    sa.Column('temperature', sa.Integer(), nullable=True),
    sa.Column('brightness', sa.Integer(), nullable=True),
    sa.Column('colour', sa.String(length=20), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('devices')
    # ### end Alembic commands ###
