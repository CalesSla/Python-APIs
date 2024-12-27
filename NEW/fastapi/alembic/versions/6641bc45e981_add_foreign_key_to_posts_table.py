"""add foreign-key to posts table

Revision ID: 6641bc45e981
Revises: 01b7f894258d
Create Date: 2024-12-27 14:41:29.586145

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6641bc45e981'
down_revision = '01b7f894258d'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("posts",
                  sa.Column("owner_id", sa.Integer(), nullable=False))
    op.create_foreign_key("post_users_fk",
                          source_table="posts",
                          referent_table="users",
                          local_cols=["owner_id"],
                          remote_cols=["id"],
                          ondelete="CASCADE")
    pass


def downgrade():
    op.drop_constraint("post_users_fk",
                      table_name="posts")
    op.drop_column("posts", "owner_id")
    pass
