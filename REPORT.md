# Звіт до лабораторної роботи №7–8

**Тема** — розробка та тестування моделей даних у Django ORM та Flask-SQLAlchemy.

**Мета** — спроєктувати моделі бібліотеки, відтворити міграції, виконати ORM-запити й перевірити поведінку моделей і маршрутів за допомогою PyTest.

Повний фактичний вивід команд збережено у [verification.txt](verification.txt). Перевірку виконано на Linux із Python 3.12.16, Django 5.2.19 і pytest 9.2.0. [Запуск GitHub Actions](https://github.com/chinazes2283/Laba7-8/actions/runs/44978375869)

## 1. Моделі Django

| Модель | Роль і поля |
| --- | --- |
| `Publisher` | Видавництво. Унікальна назва, місто, рік заснування. |
| `Author` | Автор книжки. Повне ім’я, країна, необов’язкова біографія. |
| `Book` | Позиція каталогу. Назва до 150 символів, унікальний ISBN, рік видання, статус із `choices`, обов’язкове видавництво й список авторів. За замовчуванням книжка доступна. |
| `BookDetails` | Додатковий опис книжки. Книжка, кількість сторінок, мова, необов’язкова анотація. |

- `Publisher` 1 → N `Book`. `ForeignKey` з `PROTECT` зберігає прив’язку книжок до видавництва. Поки є пов’язані книжки, видалення видавництва викликає `ProtectedError`.
- `Book` N ↔ M `Author`. Книжка може мати кількох авторів, автор може написати кілька книжок. Django створює проміжну таблицю `catalog_book_authors`. Під час видалення книжки видаляються її зв’язки з авторами. Записи авторів зберігаються.
- `Book` 1 → 0..1 `BookDetails`. `OneToOneField` забезпечує максимум один опис для книжки. `CASCADE` видаляє опис разом із книжкою, бо він залежить від неї.

Кожна модель має `Meta` з `ordering`, `verbose_name` і `verbose_name_plural`. Видавництва впорядковуються за назвою, автори за іменем і ID, книжки за назвою та ID, описи за ID книжки. `__str__` повертає назву або ім’я, а для опису повертає назву книжки з мовою в дужках. Для необов’язкових текстових полів `blank=True` допускає порожній рядок, `default=""` задає його за замовчуванням.

## 2. Міграції Django

У тимчасовій копії проєкту `verify.py` спочатку використовує модель без `summary`, генерує `0001_initial.py` і застосовує її. Після повернення поля генерує й застосовує `0002_bookdetails_summary.py`. Перший файл створює чотири моделі та їхні зв’язки, другий додає анотацію книжки й заповнює її порожнім рядком для наявних записів.

```text
$ python manage.py makemigrations catalog
Migrations for 'catalog':
  catalog/migrations/0001_initial.py
    + Create model Author
    + Create model Publisher
    + Create model Book
    + Create model BookDetails
$ python manage.py migrate --noinput
  Applying catalog.0001_initial... OK
$ python manage.py makemigrations catalog
Migrations for 'catalog':
  catalog/migrations/0002_bookdetails_summary.py
    + Add field summary to bookdetails
$ python manage.py migrate --noinput
  Applying catalog.0002_bookdetails_summary... OK
$ python manage.py showmigrations catalog
catalog
 [X] 0001_initial
 [X] 0002_bookdetails_summary
```

Фактичний SQL від `python manage.py sqlmigrate catalog 0002`. Django створює нову таблицю, переносить дані та перейменовує її.

```sql
BEGIN;
--
-- Add field summary to bookdetails
--
CREATE TABLE "new__catalog_bookdetails" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "summary" text NOT NULL, "pages" integer unsigned NOT NULL CHECK ("pages" >= 0), "language" varchar(40) NOT NULL, "book_id" bigint NOT NULL UNIQUE REFERENCES "catalog_book" ("id") DEFERRABLE INITIALLY DEFERRED);
INSERT INTO "new__catalog_bookdetails" ("id", "pages", "language", "book_id", "summary") SELECT "id", "pages", "language", "book_id", '' FROM "catalog_bookdetails";
DROP TABLE "catalog_bookdetails";
ALTER TABLE "new__catalog_bookdetails" RENAME TO "catalog_bookdetails";
COMMIT;
```

Міграції з репозиторію окремо застосовано на іншій чистій базі. Команда `python manage.py makemigrations --check --dry-run` повернула `No changes detected`. [Документація Django](https://docs.djangoproject.com/en/5.2/topics/migrations/)

## 3. Моделі та міграції Flask

СУБД — SQLite. URI — `sqlite:///library.sqlite3`, файл за замовчуванням — `instance/library.sqlite3`. `book_authors` створено через `db.Table` зі складеним первинним ключем. `db.relationship` і `backref` забезпечують зворотну навігацію. Для `book_details.book_id` діє обмеження `UNIQUE`, а видалення книжки каскадно видаляє її опис і рядки таблиці зв’язків. Видалення видавництва з книжками обмежено зовнішнім ключем з `RESTRICT`.

| Крок | Фактичний результат у тимчасовій копії |
| --- | --- |
| `python -m flask --app flask_app db init` | Створено `migrations/`, `versions/`, `env.py`, `alembic.ini` і шаблон ревізій. |
| `python -m flask --app flask_app db migrate -m "initial catalog"` | Виявлено п’ять нових таблиць. Згенеровано ревізію `0f70e59a79ff`. |
| `python -m flask --app flask_app db upgrade` | `Running upgrade  -> 0f70e59a79ff, initial catalog` |
| Повернення поля `summary` і `python -m flask --app flask_app db migrate -m "add summary"` | `Detected added column 'book_details.summary'`. Згенеровано `7dd8bb9d8026`. |
| `python -m flask --app flask_app db upgrade` | `Running upgrade 0f70e59a79ff -> 7dd8bb9d8026, add summary` |

У репозиторії ті самі зміни зафіксовані в `0001_initial_catalog.py` (`0001_catalog`) та `0002_add_summary.py` (`0002_summary`). Після застосування до чистої бази `db current` показала `0002_summary (head)`, а `db check` повернула `No new upgrade operations detected.` Інспекція SQLite підтвердила п’ять таблиць, поле `summary` і зовнішні ключі з політиками видалення. У другій ревізії `server_default=""` дозволяє додати обов’язковий стовпець і зберегти наявні рядки.

| Питання | Django ORM | Flask-Migrate |
| --- | --- | --- |
| Ініціалізація | `makemigrations` створює каталог міграцій застосунку. | Спочатку виконується `db init`, який налаштовує Alembic. |
| Генерація | `makemigrations` порівнює моделі зі станом у файлах міграцій. | `db migrate` порівнює метадані SQLAlchemy з поточною схемою БД. Згенеровані операції перевіряються вручну. |
| Застосування | `migrate` застосовує зміни, `showmigrations` показує їхній стан. | `db upgrade` застосовує ревізії, `db history` і `db current` показують історію та стан. |
| Злиття гілок | Перевіряються залежності. Для сумісних гілок можна створити міграцію через `makemigrations --merge`. | Перевіряються кілька кінцевих ревізій через `db heads`, сумісні ревізії об’єднуються через `db merge`. |
 
Після злиття потрібно перевірити як чисте встановлення, так і оновлення наявної бази. [Документація Flask-Migrate](https://flask-migrate.readthedocs.io/en/latest/)

## 4. ORM-запити та транзакції

Команди `python manage.py demo_django` і `python -m flask_app.demo` створили `River` (2024, доступна) та `Forest` (2019, в архіві). Обидві книжки належать одному видавництву.

| Операція | Сценарій та очікуваний результат | Фактичний вивід |
| --- | --- | --- |
| Create | Створити дві книжки. | `CREATE: River, Forest` |
| Read | Вибрати `River` за первинним ключем. | `READ: River` |
| Filter | Вибрати книжки від 2020 року. | `FILTER: ['River']` |
| Exclude | Виключити архівні книжки. | `EXCLUDE: ['River']` |
| OR | Вибрати нові або архівні книжки. Django використовує `Q`, Flask використовує `or_`. | `OR: ['Forest', 'River']` |
| Aggregate | Порахувати книжки й середній рік видання. | `AGGREGATE: {'count': 2, 'average_year': 2021.5}` |
| Annotate / Group by | Порахувати книжки для видавництва. | Django `ANNOTATE: 2`, Flask `GROUP BY: 2` |
| Related | Завантажити видавництво, опис і авторів. | `RELATED: Kyiv; 240; ['Olena Bondar']` |
| Reverse | Отримати книжки через `publisher.books`. | `REVERSE: ['Forest', 'River']` |
| Update | Перейменувати `River`. | `UPDATE: River Revised` |
| Delete | Видалити `Forest` і перевірити відсутність. | `DELETE: remaining=1, exists=False` |
| Rollback | Додати тимчасового автора, потім спробувати зберегти дублікат ISBN. Після відкату авторів із цим іменем має бути 0. | Flask `ROLLBACK: duplicate ISBN, temporary authors=0` |

Django використовує `create()`, `save()`, `delete()` і `transaction.atomic()`. Flask додає та видаляє об’єкти через `db.session`, а зміни зберігає через `commit()`. У прикладі Flask автор потрапляє в незавершену транзакцію через `flush()`; порушення унікальності ISBN відкочує і вставлення автора. Для уникнення N+1 у Django використано `select_related` і `prefetch_related`, у Flask — `joinedload` і `selectinload`. HTTP-тест Django перевіряє, що каталог виконує два запити. SQL у звіті отримано штатною командою Django, а `PRAGMA` використано лише для інспекції схеми SQLite.

## 5. PyTest, фікстури і параметризація

```text
tests/
├── conftest.py
├── test_django_models.py
├── test_flask_models.py
├── test_django_http.py
├── test_flask_http.py
└── test_mocks.py
```

Дев’ять функцій тестують моделі. Перевіряються створення, `__str__`, значення за замовчуванням, унікальність ISBN, прямі та зворотні зв’язки, захист видавництва і каскадне видалення. Параметризований тест Django перевіряє довжини назви 1, 150 і 151, а параметризований HTTP-тест Flask перевіряє три некоректні запити. `conftest.py` готує тестового користувача, пов’язані записи, Flask-застосунок і фікстури клієнтів обох плагінів. Django використовує тестову базу pytest-django, Flask створює нову SQLite-базу в пам’яті для кожного залученого тесту.

```bash
python -m pytest -v
python -m pytest -v --cov=catalog --cov=flask_app --cov-report=term-missing
```

Фактично запущено другу команду. PyTest зібрав 24 випадки й повідомив `24 passed in 0.63s`. Результат для кожного випадку є у [verification.txt](verification.txt).

## 6. Інтеграційні HTTP-тести

| Тест | Маршрут і сценарій | Очікуваний результат |
| --- | --- | --- |
| `test_django_catalog` | `GET /`, каталог із книжкою й автором. | 200, шаблон `catalog/books.html`, назва й автор у відповіді, два SQL-запити. |
| `test_django_detail` | `GET /books/<pk>/`, книжка існує. | 200, шаблон `catalog/detail.html` та ISBN. |
| `test_django_missing_book` | `GET /books/9999/`, книжки немає. | 404. |
| `test_django_member_catalog_redirects_guest` | `GET /members/books/`, гість. | 302 на сторінку входу з параметром `next`. |
| `test_django_member_catalog_opens_for_user` | `GET /members/books/`, авторизований читач. | 200, книжка у відповіді. |
| `test_flask_catalog` | `GET /books`, каталог із книжкою. | 200, очікуваний JSON. |
| `test_flask_creates_book_from_json` | `POST /books`, валідний JSON із пробілами навколо назви. | 201, пробіли прибрано, книжка доступна через GET. |
| `test_flask_rejects_bad_payload` | `POST /books`, JSON-масив, порожня назва або невідоме видавництво. | 400, 400 або 404 відповідно й повідомлення про помилку. |
| `test_flask_rejects_duplicate_isbn` | `POST /books`, ISBN уже існує. | 409, у каталозі лишається один запис. |

## 7. Моки й покриття

- `test_notify_book_available_calls_mail_backend` підміняє виклик `send_mail`. Тест перевіряє отримувача, відправника, тему й тіло через `assert_called_once_with`. Відправлення пошти ізольовано, тому тест працює без поштового сервера та мережевої затримки.
- `test_current_year_catalog_uses_local_date` підміняє `timezone.localdate` датою 1 січня 2024 року, перевіряє виклик без аргументів і виконує справжній ORM-запит. Результат стабільний незалежно від поточної дати.

Фактичний звіт покриття рядків.

```text
Name                                         Stmts   Miss  Cover   Missing
--------------------------------------------------------------------------
catalog/__init__.py                              0      0   100%
catalog/management/__init__.py                   0      0   100%
catalog/management/commands/__init__.py          0      0   100%
catalog/management/commands/demo_django.py      39     39     0%   1-54
catalog/models.py                               48      0   100%
catalog/services.py                              7      0   100%
catalog/views.py                                16      1    94%   11
flask_app/__init__.py                           13      0   100%
flask_app/demo.py                               59     59     0%   1-80
flask_app/models.py                             45      0   100%
flask_app/views.py                              29      0   100%
--------------------------------------------------------------------------
TOTAL                                          256     99    61%
============================== 24 passed in 0.63s ==============================
```

`Stmts` — кількість виконуваних інструкцій. `Miss` — кількість інструкцій, які тести не виконали. `Cover` — частка виконаних інструкцій у відсотках. `Missing` — номери непокритих рядків.

Найменше покрито `demo_django.py` і `flask_app/demo.py`. Їх запущено окремими командами в `verify.py` перед стартом PyTest, тому їхній фактичний запуск є у виводі, а coverage зафіксував 0% для кожного. У `catalog/views.py` непокритий рядок 11 — HTTP-гілка `?recent=1`. Сам запит для поточного року перевірено окремим мок-тестом. Усі файли моделей, сервісів і Flask-маршрутів мають 100% покриття рядків. Загальний показник — 61%. Покриття гілок окремо не вимірювалося.

Обидва проєкти відтворюють однакові зв’язки предметної області. Перевірки на чистих базах підтвердили узгодженість моделей і міграцій, а тести — поведінку моделей, HTTP-маршрутів і двох ізольованих залежностей.
