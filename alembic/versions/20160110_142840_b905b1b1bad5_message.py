"""message

Revision ID: b905b1b1bad5
Revises: c22d9102d2d7
Create Date: 2016-01-10 14:28:40.313855

"""

# revision identifiers, used by Alembic.
revision = 'b905b1b1bad5'
down_revision = 'c22d9102d2d7'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('messages',
    sa.Column('ts', sa.DateTime(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('channel_id', sa.Integer(), nullable=False),
    sa.Column('text', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['channel_id'], ['channels.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('ts', 'user_id', 'channel_id')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('messages')
    ### end Alembic commands ###