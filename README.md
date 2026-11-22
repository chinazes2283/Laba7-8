# Лабораторна робота №7–8

Одна предметна область — каталог бібліотеки — у двох незалежних проєктах на Python. Django показує сторінки каталогу, Flask повертає JSON. Обидва проєкти використовують SQLite.

## Встановлення

Потрібен Python 3.12 або новіший. Команди запускаються з кореня проєкту.

```bash
python -m venv .venv
```

Активація в Windows PowerShell — `& .\.venv\Scripts\Activate.ps1`. У Linux або macOS — `source .venv/bin/activate`.

```bash
python -m pip install -r requirements.txt
```

## Django

```bash
python manage.py migrate
python manage.py demo_django
python manage.py runserver
```

Каталог відкривається за адресою [http://127.0.0.1:8000/](http://127.0.0.1:8000/). Для доступу до `/members/books/` створіть користувача командою `python manage.py createsuperuser` і ввійдіть через `/accounts/login/`.

## Flask

```bash
python -m flask --app flask_app db upgrade
python -m flask_app.demo
python -m flask --app flask_app run
```

Каталог доступний за адресою [http://127.0.0.1:5000/books](http://127.0.0.1:5000/books). `POST /books` приймає JSON з полями `title`, `isbn`, `year` і `publisher_id` наявного видавництва. Після першої міграції каталоги порожні. Демонстрації ORM самі створюють приклади та працюють із тимчасовими даними.

## Перевірка

```bash
python -m pytest -v
python -m pytest -v --cov=catalog --cov=flask_app --cov-report=term-missing
python verify.py
```

`verify.py` у тимчасових каталогах відтворює історію обох міграцій, перевіряє міграції з репозиторію на чистих базах і запускає демонстрації та тести. Опис завдань і результати наведено у [звіті](REPORT.md).
