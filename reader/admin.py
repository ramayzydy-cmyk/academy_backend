from django.contrib import admin

from .models import ReaderBook
from .services import PDFConverterService


@admin.register(ReaderBook)
class ReaderBookAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "source_type",
        "total_pages",
        "is_active",
        "created_at",
    )

    list_filter = (
        "source_type",
        "is_active",
    )

    search_fields = (
        "title",
        "title_ar",
        "folder_name",
    )

    list_editable = (
        "is_active",
    )

    readonly_fields = (
        "created_at",
        "total_pages",
    )

    fieldsets = (
        (
            "Basic Information",
            {
                "fields": (
                    "title",
                    "title_ar",
                    "cover_image",
                    "pdf_file",
                )
            },
        ),
        (
            "Reader Settings",
            {
                "fields": (
                    "folder_name",
                    "total_pages",
                    "source_type",
                    "source_id",
                    "is_active",
                )
            },
        ),
        (
            "System",
            {
                "fields": (
                    "created_at",
                )
            },
        ),
    )

    def save_model(self, request, obj, form, change):

        super().save_model(
            request,
            obj,
            form,
            change,
        )

        if obj.pdf_file:
            PDFConverterService.convert(obj)