from pathlib import Path
from tempfile import TemporaryDirectory

from flask_migrate import upgrade
from sqlalchemy import func, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload, selectinload

from . import create_app
from .models import Author, Book, BookDetails, Publisher, db


def demonstrate():
    publisher = Publisher(name="Demo", city="Kyiv", founded_year=2001)
    author = Author(full_name="Olena Bondar", country="Ukraine")
    book = Book(title="River", isbn="9780000000001", year=2024, publisher=publisher)
    second = Book(
        title="Forest", isbn="9780000000002", year=2019,
        publisher=publisher, status="archived",
    )
    book.authors.append(author)
    book.details = BookDetails(pages=240, language="Ukrainian")
    db.session.add_all([book, second])
    db.session.commit()
    print(f"CREATE: {book.title}, {second.title}")
    print(f"READ: {db.session.get(Book, book.id).title}")

    books = db.select(Book.title).order_by(Book.title)
    recent = books.where(Book.year >= 2020)
    available = books.where(Book.status != "archived")
    selected = books.where(or_(Book.year >= 2020, Book.status == "archived"))
    for label, query in [("FILTER", recent), ("EXCLUDE", available), ("OR", selected)]:
        print(f"{label}: {db.session.scalars(query).all()}")

    count, average_year = db.session.execute(
        db.select(func.count(Book.id), func.avg(Book.year))
    ).one()
    print(f"AGGREGATE: {dict(count=count, average_year=average_year)}")
    counts = db.select(Publisher.id, func.count(Book.id)).outerjoin(Book).group_by(Publisher.id)
    print(f"GROUP BY: {db.session.execute(counts).one()[1]}")

    db.session.expire_all()
    loaded = db.session.scalars(
        db.select(Book).where(Book.isbn == "9780000000001").options(
            joinedload(Book.publisher), joinedload(Book.details), selectinload(Book.authors)
        )
    ).one()
    print(f"RELATED: {loaded.publisher.city}; {loaded.details.pages}; {[str(a) for a in loaded.authors]}")
    print(f"REVERSE: {sorted(b.title for b in publisher.books)}")
    book.title = "River Revised"
    db.session.commit()
    print(f"UPDATE: {book.title}")
    second_id = second.id
    db.session.delete(second)
    db.session.commit()
    remaining = db.session.scalar(db.select(func.count(Book.id)))
    print(f"DELETE: remaining={remaining}, exists={db.session.get(Book, second_id) is not None}")

    try:
        db.session.add(Author(full_name="Temporary Author", country="Ukraine"))
        db.session.flush()
        db.session.add(Book(title="Duplicate", isbn=book.isbn, year=2024, publisher=publisher))
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        count = db.session.scalar(
            db.select(func.count(Author.id)).where(Author.full_name == "Temporary Author")
        )
        print(f"ROLLBACK: duplicate ISBN, temporary authors={count}")


if __name__ == "__main__":
    with TemporaryDirectory() as directory:
        path = (Path(directory) / "demo.sqlite3").as_posix()
        app = create_app({"SQLALCHEMY_DATABASE_URI": f"sqlite:///{path}"})
        with app.app_context():
            upgrade()
            demonstrate()
            db.session.remove()
            db.engine.dispose()
