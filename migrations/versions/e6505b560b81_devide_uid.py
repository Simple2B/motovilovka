"""devide.uid

Revision ID: e6505b560b81
Revises: 92df111c72c6
Create Date: 2022-07-27 18:24:29.795781

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "e6505b560b81"
down_revision = "92df111c72c6"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("devices", sa.Column("uid", sa.String(length=64), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("devices", "uid")
    # ### end Alembic commands ###
