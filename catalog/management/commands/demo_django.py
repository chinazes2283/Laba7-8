from uuid import uuid4

from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Avg, Count, Q

from catalog.models import Author, Book, BookDetails, Publisher


class Command(BaseCommand):
    help = "Demonstrate Django ORM operations with temporary data."

    def handle(self, *args, **options):
        with transaction.atomic():
            key = uuid4().hex[:12]
            publisher = Publisher.objects.create(
                name=f"Demo {key}", city="Kyiv", founded_year=2001
            )
            author = Author.objects.create(full_name="Olena Bondar", country="Ukraine")
            book = Book.objects.create(
                title="River", isbn=f"1{key}", year=2024, publisher=publisher
            )
            second = Book.objects.create(
                title="Forest", isbn=f"2{key}", year=2019, publisher=publisher,
                status=Book.Status.ARCHIVED,
            )
            BookDetails.objects.create(book=book, pages=240, language="Ukrainian")
            book.authors.add(author)
            self.stdout.write(f"CREATE: {book.title}, {second.title}")
            self.stdout.write(f"READ: {Book.objects.get(pk=book.pk).title}")

            books = Book.objects.filter(publisher=publisher)
            recent = books.filter(year__gte=2020)
            available = books.exclude(status=Book.Status.ARCHIVED)
            selected = books.filter(Q(year__gte=2020) | Q(status=Book.Status.ARCHIVED))
            for label, query in [("FILTER", recent), ("EXCLUDE", available), ("OR", selected)]:
                self.stdout.write(f"{label}: {list(query.values_list('title', flat=True))}")

            summary = books.aggregate(count=Count("id"), average_year=Avg("year"))
            self.stdout.write(f"AGGREGATE: {summary}")
            row = Publisher.objects.annotate(book_count=Count("books")).get(pk=publisher.pk)
            self.stdout.write(f"ANNOTATE: {row.book_count}")
            loaded = books.select_related("publisher", "details").prefetch_related("authors").get(pk=book.pk)
            self.stdout.write(f"RELATED: {loaded.publisher.city}; {loaded.details.pages}; {[str(a) for a in loaded.authors.all()]}")
            self.stdout.write(f"REVERSE: {list(publisher.books.values_list('title', flat=True))}")

            book.title = "River Revised"
            book.save(update_fields=["title"])
            book.refresh_from_db()
            self.stdout.write(f"UPDATE: {book.title}")
            second_pk = second.pk
            second.delete()
            self.stdout.write(f"DELETE: remaining={books.count()}, exists={books.filter(pk=second_pk).exists()}")
            transaction.set_rollback(True)
