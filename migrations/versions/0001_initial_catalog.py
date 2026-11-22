"""Create the catalog tables."""

from alembic import op
import sqlalchemy as sa

revision = "0001_catalog"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "author",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("full_name", sa.String(120), nullable=False),
        sa.Column("country", sa.String(80), nullable=False),
        sa.Column("bio", sa.Text(), nullable=False),
    )
    op.create_table(
        "publisher",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False, unique=True),
        sa.Column("city", sa.String(80), nullable=False),
        sa.Column("founded_year", sa.Integer(), nullable=False),
    )
    op.create_table(
        "book",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(150), nullable=False),
        sa.Column("isbn", sa.String(13), nullable=False, unique=True),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(12), nullable=False),
        sa.Column(
            "publisher_id", sa.Integer(),
            sa.ForeignKey("publisher.id", ondelete="RESTRICT"), nullable=False,
        ),
    )
    op.create_table(
        "book_authors",
        sa.Column(
            "book_id", sa.Integer(), sa.ForeignKey("book.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "author_id", sa.Integer(), sa.ForeignKey("author.id", ondelete="CASCADE"),
            primary_key=True,
        ),
    )
    op.create_table(
        "book_details",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "book_id", sa.Integer(), sa.ForeignKey("book.id", ondelete="CASCADE"),
            unique=True, nullable=False,
        ),
        sa.Column("pages", sa.Integer(), nullable=False),
        sa.Column("language", sa.String(40), nullable=False),
    )


def downgrade():
    op.drop_table("book_details")
    op.drop_table("book_authors")
    op.drop_table("book")
    op.drop_table("publisher")
    op.drop_table("author")
