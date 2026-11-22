from flask import Blueprint, request
from sqlalchemy.exc import IntegrityError

from .models import Book, Publisher, db

api = Blueprint("api", __name__)


@api.get("/books")
def book_list():
    books = db.session.scalars(db.select(Book).order_by(Book.title, Book.id))
    return [{"id": book.id, "title": book.title, "isbn": book.isbn} for book in books]


@api.post("/books")
def book_create():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return {"error": "Очікується JSON-об'єкт"}, 400

    title = data.get("title")
    isbn = data.get("isbn")
    year = data.get("year")
    publisher_id = data.get("publisher_id")
    if (
        not isinstance(title, str) or not 1 <= len(title.strip()) <= 150
        or not isinstance(isbn, str) or not (len(isbn) == 13 and isbn.isascii() and isbn.isdecimal())
        or type(year) is not int or not 1 <= year <= 9999
        or type(publisher_id) is not int or not 1 <= publisher_id <= 2**63 - 1
    ):
        return {"error": "Некоректні поля книжки"}, 400

    if db.session.get(Publisher, publisher_id) is None:
        return {"error": "Видавництво не знайдено"}, 404

    book = Book(title=title.strip(), isbn=isbn, year=year, publisher_id=publisher_id)
    db.session.add(book)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {"error": "ISBN уже існує або видавництво недоступне"}, 409

    return {"id": book.id, "title": book.title, "isbn": book.isbn}, 201
