import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Author",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("full_name", models.CharField(max_length=120)),
                ("country", models.CharField(max_length=80)),
                ("bio", models.TextField(blank=True, default="")),
            ],
            options={
                "ordering": ["full_name", "id"],
                "verbose_name": "автор",
                "verbose_name_plural": "автори",
            },
        ),
        migrations.CreateModel(
            name="Publisher",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100, unique=True)),
                ("city", models.CharField(max_length=80)),
                ("founded_year", models.PositiveSmallIntegerField()),
            ],
            options={
                "ordering": ["name"],
                "verbose_name": "видавництво",
                "verbose_name_plural": "видавництва",
            },
        ),
        migrations.CreateModel(
            name="Book",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=150)),
                ("isbn", models.CharField(max_length=13, unique=True)),
                ("year", models.PositiveSmallIntegerField()),
                ("status", models.CharField(choices=[("available", "Доступна"), ("archived", "В архіві")], default="available", max_length=12)),
                ("authors", models.ManyToManyField(blank=True, related_name="books", to="catalog.author")),
                ("publisher", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="books", to="catalog.publisher")),
            ],
            options={
                "ordering": ["title", "id"],
                "verbose_name": "книжка",
                "verbose_name_plural": "книжки",
            },
        ),
        migrations.CreateModel(
            name="BookDetails",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("pages", models.PositiveIntegerField()),
                ("language", models.CharField(max_length=40)),
                ("book", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="details", to="catalog.book")),
            ],
            options={
                "ordering": ["book_id"],
                "verbose_name": "опис книжки",
                "verbose_name_plural": "описи книжок",
            },
        ),
    ]
