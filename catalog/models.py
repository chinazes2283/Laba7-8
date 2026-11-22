from django.db import models


class Publisher(models.Model):
    name = models.CharField(max_length=100, unique=True)
    city = models.CharField(max_length=80)
    founded_year = models.PositiveSmallIntegerField()

    class Meta:
        ordering = ["name"]
        verbose_name = "видавництво"
        verbose_name_plural = "видавництва"

    def __str__(self):
        return self.name


class Author(models.Model):
    full_name = models.CharField(max_length=120)
    country = models.CharField(max_length=80)
    bio = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["full_name", "id"]
        verbose_name = "автор"
        verbose_name_plural = "автори"

    def __str__(self):
        return self.full_name


class Book(models.Model):
    class Status(models.TextChoices):
        AVAILABLE = "available", "Доступна"
        ARCHIVED = "archived", "В архіві"

    title = models.CharField(max_length=150)
    isbn = models.CharField(max_length=13, unique=True)
    year = models.PositiveSmallIntegerField()
    status = models.CharField(
        max_length=12, choices=Status.choices, default=Status.AVAILABLE
    )
    publisher = models.ForeignKey(
        Publisher, on_delete=models.PROTECT, related_name="books"
    )
    authors = models.ManyToManyField(Author, related_name="books", blank=True)

    class Meta:
        ordering = ["title", "id"]
        verbose_name = "книжка"
        verbose_name_plural = "книжки"

    def __str__(self):
        return self.title


class BookDetails(models.Model):
    book = models.OneToOneField(
        Book, on_delete=models.CASCADE, related_name="details"
    )
    pages = models.PositiveIntegerField()
    language = models.CharField(max_length=40)
    summary = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["book_id"]
        verbose_name = "опис книжки"
        verbose_name_plural = "описи книжок"

    def __str__(self):
        return f"{self.book.title} ({self.language})"
