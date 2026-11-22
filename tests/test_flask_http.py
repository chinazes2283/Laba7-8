import pytest


def test_flask_catalog(flask_client, flask_book):
    response = flask_client.get("/books")
    assert response.status_code == 200
    assert response.json == [{
        "id": flask_book.id, "title": "River", "isbn": flask_book.isbn,
    }]


def test_flask_creates_book_from_json(flask_client, flask_book):
    data = {
        "title": "  Forest  ", "isbn": "9780000000002",
        "year": 2019, "publisher_id": flask_book.publisher_id,
    }
    response = flask_client.post("/books", json=data)
    assert response.status_code == 201
    assert response.json["title"] == "Forest"
    assert response.json in flask_client.get("/books").json


@pytest.mark.parametrize("payload,expected", [
    ([], 400),
    ({"title": ""}, 400),
    ({"title": "Forest", "isbn": "9780000000002", "year": 2019, "publisher_id": 999}, 404),
])
def test_flask_rejects_bad_payload(flask_client, payload, expected):
    response = flask_client.post("/books", json=payload)
    assert response.status_code == expected
    assert "error" in response.json


def test_flask_rejects_duplicate_isbn(flask_client, flask_book):
    data = {
        "title": "Duplicate", "isbn": flask_book.isbn,
        "year": 2024, "publisher_id": flask_book.publisher_id,
    }
    assert flask_client.post("/books", json=data).status_code == 409
    assert len(flask_client.get("/books").json) == 1
