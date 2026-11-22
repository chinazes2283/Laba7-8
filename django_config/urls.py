from django.contrib.auth.views import LoginView
from django.urls import path

from catalog import views

urlpatterns = [
    path("", views.book_list, name="book-list"),
    path("books/<int:pk>/", views.book_detail, name="book-detail"),
    path("members/books/", views.member_books, name="member-books"),
    path("accounts/login/", LoginView.as_view(), name="login"),
]
