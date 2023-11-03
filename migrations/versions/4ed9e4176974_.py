"""empty message

Revision ID: 4ed9e4176974
Revises: 66d26f410193
Create Date: 2023-11-01 13:27:09.695625

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4ed9e4176974'
down_revision = '66d26f410193'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('layer', schema=None) as batch_op:
        batch_op.add_column(sa.Column('display_order', sa.Integer(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('layer', schema=None) as batch_op:
        batch_op.drop_column('display_order')

    # ### end Alembic commands ###