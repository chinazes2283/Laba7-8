import pytest
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

from flask_app.models import Book, BookDetails, db


def test_flask_book_defaults_and_relationships(flask_book):
    book = flask_book
    assert book.status == "available"
    assert str(book) == "River"
    assert str(book.publisher) == "Litera"
    assert str(book.authors[0]) == "Olena Bondar"
    assert str(book.details) == "River (Ukrainian)"
    assert book.details.summary == ""
    assert book.publisher.books == [book]
    assert book.authors[0].books == [book]


def test_flask_isbn_is_unique(flask_book):
    db.session.add(Book(
        title="Duplicate", isbn=flask_book.isbn, year=2020,
        publisher_id=flask_book.publisher_id,
    ))
    with pytest.raises(IntegrityError):
        db.session.commit()
    db.session.rollback()
    assert db.session.scalar(db.select(func.count(Book.id))) == 1


def test_flask_book_cascades_to_details(flask_book):
    details_id = flask_book.details.id
    author = flask_book.authors[0]
    db.session.expire(flask_book, ["details"])
    db.session.delete(flask_book)
    db.session.commit()
    assert db.session.get(BookDetails, details_id) is None
    assert author.books == []


def test_flask_book_requires_existing_publisher(app):
    db.session.add(Book(title="River", isbn="9780000000001", year=2024, publisher_id=999))
    with pytest.raises(IntegrityError):
        db.session.commit()
    db.session.rollback()
