import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models.deletion import ProtectedError

from catalog.models import Book, BookDetails


def test_django_book_defaults_and_labels(django_book):
    book = Book.objects.get(pk=django_book.pk)
    assert book.status == Book.Status.AVAILABLE
    assert str(book) == "River"
    assert str(book.publisher) == "Litera"
    assert str(book.authors.get()) == "Olena Bondar"
    assert str(book.details) == "River (Ukrainian)"
    assert book.details.summary == ""


@pytest.mark.parametrize("length,valid", [(1, True), (150, True), (151, False)])
def test_django_title_length(django_book, length, valid):
    django_book.title = "a" * length
    if valid:
        django_book.full_clean()
    else:
        with pytest.raises(ValidationError) as error:
            django_book.full_clean()
        assert "title" in error.value.message_dict


def test_django_unique_isbn(django_book):
    with pytest.raises(IntegrityError), transaction.atomic():
        Book.objects.create(
            title="Duplicate", isbn=django_book.isbn,
            year=2020, publisher=django_book.publisher,
        )


def test_django_cascade_and_reverse_relationships(django_book):
    book = django_book
    author = book.authors.get()
    assert author.books.get() == book
    assert book.publisher.books.get() == book
    details_id = book.details.pk
    book.delete()
    assert not BookDetails.objects.filter(pk=details_id).exists()
    assert not author.books.exists()


def test_django_publisher_is_protected(django_book):
    with pytest.raises(ProtectedError):
        django_book.publisher.delete()
