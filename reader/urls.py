from django.urls import path

from .views import (
    ReaderBookListAPIView,
    ReaderBookDetailAPIView,
    reader_page,
)

urlpatterns = [
    path(
        "books/",
        ReaderBookListAPIView.as_view(),
    ),
    path(
        "books/<int:pk>/",
        ReaderBookDetailAPIView.as_view(),
    ),
    path(
        "books/<int:book_id>/page/<int:page>/",
        reader_page,
    ),
]