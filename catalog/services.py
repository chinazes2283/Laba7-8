from django.core.mail import send_mail
from django.utils import timezone

from .models import Book


def notify_book_available(book, email):
    return send_mail(
        "Книжка доступна",
        f"«{book.title}» знову в каталозі бібліотеки.",
        "library@example.com",
        [email],
    )


def books_published_this_year():
    return Book.objects.filter(year=timezone.localdate().year)
