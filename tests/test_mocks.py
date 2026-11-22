from datetime import date
from unittest.mock import patch

from catalog.models import Book
from catalog.services import books_published_this_year, notify_book_available


@patch("catalog.services.send_mail", return_value=1)
def test_notify_book_available_calls_mail_backend(send_mail, django_book):
    assert notify_book_available(django_book, "reader@example.com") == 1
    send_mail.assert_called_once_with(
        "Книжка доступна",
        "«River» знову в каталозі бібліотеки.",
        "library@example.com",
        ["reader@example.com"],
    )


@patch("catalog.services.timezone.localdate", return_value=date(2024, 1, 1))
def test_current_year_catalog_uses_local_date(localdate, django_book):
    Book.objects.create(
        title="Forest", isbn="9780000000002",
        year=2019, publisher=django_book.publisher,
    )
    assert list(books_published_this_year()) == [django_book]
    localdate.assert_called_once_with()
