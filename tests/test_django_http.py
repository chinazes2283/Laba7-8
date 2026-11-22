from django.urls import reverse


def test_django_catalog(django_client, django_book, django_assert_num_queries):
    with django_assert_num_queries(2):
        response = django_client.get("/")
    assert response.status_code == 200
    assert any(t.name == "catalog/books.html" for t in response.templates)
    assert b"River" in response.content
    assert b"Olena Bondar" in response.content


def test_django_detail(django_client, django_book):
    response = django_client.get(reverse("book-detail", args=[django_book.pk]))
    assert response.status_code == 200
    assert any(t.name == "catalog/detail.html" for t in response.templates)
    assert django_book.isbn.encode() in response.content


def test_django_missing_book(django_client, db):
    assert django_client.get("/books/9999/").status_code == 404


def test_django_member_catalog_redirects_guest(django_client):
    response = django_client.get("/members/books/")
    assert response.status_code == 302
    assert response.url == "/accounts/login/?next=/members/books/"


def test_django_member_catalog_opens_for_user(django_client, django_user, django_book):
    django_client.force_login(django_user)
    response = django_client.get("/members/books/")
    assert response.status_code == 200
    assert b"River" in response.content
