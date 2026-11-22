"""Add the optional summary and preserve existing rows."""

from alembic import op
import sqlalchemy as sa

revision = "0002_summary"
down_revision = "0001_catalog"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "book_details",
        sa.Column("summary", sa.Text(), nullable=False, server_default=""),
    )


def downgrade():
    op.drop_column("book_details", "summary")
