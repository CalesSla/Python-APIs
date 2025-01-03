"""create posts table

Revision ID: 3a18bdd888d5
Revises: 
Create Date: 2024-12-27 14:09:22.694805

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3a18bdd888d5'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("posts", 
                    sa.Column("id", sa.Integer(), nullable=False, primary_key=True),
                    sa.Column("title", sa.String(), nullable=False))
    pass

def downgrade():
    op.drop_table("posts")
    pass
