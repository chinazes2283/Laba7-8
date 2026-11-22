import sqlite3

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event
from sqlalchemy.engine import Engine

db = SQLAlchemy()


@event.listens_for(Engine, "connect")
def enable_sqlite_foreign_keys(connection, _):
    if isinstance(connection, sqlite3.Connection):
        connection.execute("PRAGMA foreign_keys=ON")


book_authors = db.Table(
    "book_authors",
    db.Column("book_id", db.ForeignKey("book.id", ondelete="CASCADE"), primary_key=True),
    db.Column("author_id", db.ForeignKey("author.id", ondelete="CASCADE"), primary_key=True),
)


class Publisher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    city = db.Column(db.String(80), nullable=False)
    founded_year = db.Column(db.Integer, nullable=False)

    def __str__(self):
        return self.name


class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    country = db.Column(db.String(80), nullable=False)
    bio = db.Column(db.Text, default="", nullable=False)

    def __str__(self):
        return self.full_name


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    isbn = db.Column(db.String(13), unique=True, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(12), default="available", nullable=False)
    publisher_id = db.Column(
        db.Integer, db.ForeignKey("publisher.id", ondelete="RESTRICT"), nullable=False
    )
    publisher = db.relationship("Publisher", backref=db.backref("books", lazy=True))
    authors = db.relationship("Author", secondary=book_authors, backref="books")

    def __str__(self):
        return self.title


class BookDetails(db.Model):
    __tablename__ = "book_details"

    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(
        db.Integer, db.ForeignKey("book.id", ondelete="CASCADE"),
        unique=True, nullable=False,
    )
    pages = db.Column(db.Integer, nullable=False)
    language = db.Column(db.String(40), nullable=False)
    summary = db.Column(db.Text, server_default="", nullable=False)
    book = db.relationship(
        "Book", backref=db.backref(
            "details", uselist=False, cascade="all, delete-orphan", passive_deletes=True
        )
    )

    def __str__(self):
        return f"{self.book.title} ({self.language})"
