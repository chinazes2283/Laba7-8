import pytest
from pytest_django.fixtures import client as django_client
from pytest_flask.fixtures import client as flask_client

from catalog.models import Author, Book, BookDetails, Publisher
from flask_app import create_app
from flask_app.models import Author as FlaskAuthor
from flask_app.models import Book as FlaskBook
from flask_app.models import BookDetails as FlaskDetails
from flask_app.models import Publisher as FlaskPublisher
from flask_app.models import db as flask_db


@pytest.fixture
def django_user(django_user_model, db):
    return django_user_model.objects.create_user(username="reader", password="library-test")


@pytest.fixture
def django_book(db):
    publisher = Publisher.objects.create(name="Litera", city="Kyiv", founded_year=1998)
    author = Author.objects.create(full_name="Olena Bondar", country="Ukraine")
    book = Book.objects.create(
        title="River", isbn="9780000000001", year=2024, publisher=publisher
    )
    book.authors.add(author)
    BookDetails.objects.create(book=book, pages=240, language="Ukrainian")
    return book


@pytest.fixture
def app():
    application = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
    })
    with application.app_context():
        flask_db.create_all()
    yield application
    with application.app_context():
        flask_db.session.remove()
        flask_db.engine.dispose()


@pytest.fixture
def flask_book(app):
    publisher = FlaskPublisher(name="Litera", city="Kyiv", founded_year=1998)
    author = FlaskAuthor(full_name="Olena Bondar", country="Ukraine")
    book = FlaskBook(
        title="River", isbn="9780000000001", year=2024, publisher=publisher
    )
    book.authors.append(author)
    book.details = FlaskDetails(pages=240, language="Ukrainian")
    flask_db.session.add(book)
    flask_db.session.commit()
    return book
