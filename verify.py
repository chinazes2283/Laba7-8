"""Recreate both migration histories and record the lab results."""

import os
from pathlib import Path
import shutil
import sqlite3
import subprocess
import sys
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parent


def run(directory, args, env):
    print("\n$ python", " ".join(args), flush=True)
    subprocess.run([sys.executable, *args], cwd=directory, env=env, check=True)


def recreate_migrations(folder):
    for package in ("catalog", "django_config", "flask_app"):
        shutil.copytree(
            ROOT / package, folder / package,
            ignore=shutil.ignore_patterns("__pycache__", "migrations"),
        )
    shutil.copy2(ROOT / "manage.py", folder)
    env = {**os.environ, "DJANGO_DB_PATH": str(folder / "django.sqlite3")}
    django_models = folder / "catalog/models.py"
    flask_models = folder / "flask_app/models.py"

    django_current = django_models.read_text(encoding="utf-8")
    django_models.write_text(
        django_current.replace('    summary = models.TextField(blank=True, default="")\n', ""),
        encoding="utf-8",
    )
    run(folder, ["manage.py", "makemigrations", "catalog"], env)
    run(folder, ["manage.py", "migrate", "--noinput"], env)
    django_models.write_text(django_current, encoding="utf-8")
    run(folder, ["manage.py", "makemigrations", "catalog"], env)
    run(folder, ["manage.py", "migrate", "--noinput"], env)
    run(folder, ["manage.py", "showmigrations", "catalog"], env)
    run(folder, ["manage.py", "sqlmigrate", "catalog", "0002"], env)

    flask = ["-m", "flask", "--app", "flask_app"]
    flask_current = flask_models.read_text(encoding="utf-8")
    flask_models.write_text(
        flask_current.replace('    summary = db.Column(db.Text, server_default="", nullable=False)\n', ""),
        encoding="utf-8",
    )
    run(folder, [*flask, "db", "init"], env)
    run(folder, [*flask, "db", "migrate", "-m", "initial catalog"], env)
    run(folder, [*flask, "db", "upgrade"], env)
    flask_models.write_text(flask_current, encoding="utf-8")
    run(folder, [*flask, "db", "migrate", "-m", "add summary"], env)
    run(folder, [*flask, "db", "upgrade"], env)
    run(folder, [*flask, "db", "history"], env)


def verify_saved_migrations(folder):
    for path in ("catalog", "django_config", "flask_app", "migrations", "tests"):
        shutil.copytree(ROOT / path, folder / path, ignore=shutil.ignore_patterns("__pycache__"))
    for filename in ("manage.py", "pytest.ini", "pyproject.toml"):
        shutil.copy2(ROOT / filename, folder)
    env = {**os.environ, "DJANGO_DB_PATH": str(folder / "django.sqlite3")}
    flask = ["-m", "flask", "--app", "flask_app"]

    print("\n=== Verifying bundled migrations ===", flush=True)
    run(folder, ["manage.py", "migrate", "--noinput"], env)
    run(folder, ["manage.py", "makemigrations", "--check", "--dry-run"], env)
    run(folder, ["manage.py", "showmigrations", "catalog"], env)
    run(folder, ["manage.py", "sqlmigrate", "catalog", "0002"], env)
    run(folder, [*flask, "db", "upgrade"], env)
    run(folder, [*flask, "db", "check"], env)
    run(folder, [*flask, "db", "current"], env)

    path = folder / "instance/library.sqlite3"
    with sqlite3.connect(f"{path.as_uri()}?mode=ro", uri=True) as connection:
        for table in ("publisher", "author", "book", "book_authors", "book_details"):
            columns = connection.execute(f"PRAGMA table_info({table})")
            print(table, [row[1] for row in columns], flush=True)
            foreign_keys = connection.execute(f"PRAGMA foreign_key_list({table})")
            for row in foreign_keys:
                print(f"  FK {row[3]} -> {row[2]}.{row[4]} (ON DELETE {row[6]})", flush=True)
    connection.close()

    run(folder, ["manage.py", "demo_django"], env)
    run(folder, ["-m", "flask_app.demo"], env)
    run(folder, ["-m", "pytest", "-v", "--cov=catalog", "--cov=flask_app", "--cov-report=term-missing"], env)


if __name__ == "__main__":
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        print("=== Recreating both migration histories ===", flush=True)
        recreate_migrations(root / "recreated")
        verify_saved_migrations(root / "bundled")
