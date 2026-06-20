from django.db import models


class ReaderBook(models.Model):
    SOURCE_CHOICES = [
        ("book", "Book"),
        ("curriculum", "Curriculum"),
        ("novel", "Novel"),
        ("story", "Story"),
        ("other", "Other"),
    ]

    title = models.CharField(max_length=255)
    title_ar = models.CharField(max_length=255, blank=True)

    cover_image = models.ImageField(
        upload_to="reader/covers/",
        blank=True,
        null=True,
    )

    pdf_file = models.FileField(
        upload_to="reader/pdfs/",
        blank=True,
        null=True,
    )

    folder_name = models.CharField(
        max_length=255,
        unique=True,
        help_text="Folder containing page images",
    )

    total_pages = models.PositiveIntegerField(
        default=0,
    )

    source_type = models.CharField(
        max_length=30,
        choices=SOURCE_CHOICES,
        default="book",
    )

    source_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Original object id",
    )

    is_active = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["title"]
        verbose_name = "Reader Book"
        verbose_name_plural = "Reader Books"

    def __str__(self):
        return self.title