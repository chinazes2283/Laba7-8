from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render

from .models import Book
from .services import books_published_this_year


def book_list(request):
    books = Book.objects.all()
    if request.GET.get("recent") == "1":
        books = books_published_this_year()
    books = books.select_related("publisher").prefetch_related("authors")
    return render(request, "catalog/books.html", {"books": books})


def book_detail(request, pk):
    book = get_object_or_404(Book.objects.select_related("publisher"), pk=pk)
    return render(request, "catalog/detail.html", {"book": book})


@login_required
def member_books(request):
    return book_list(request)
