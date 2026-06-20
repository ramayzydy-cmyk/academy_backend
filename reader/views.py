from django.conf import settings
from django.http import JsonResponse
from rest_framework.generics import ListAPIView, RetrieveAPIView

from .models import ReaderBook
from .serializers import ReaderBookSerializer


class ReaderBookListAPIView(ListAPIView):

    serializer_class = ReaderBookSerializer
    queryset = ReaderBook.objects.filter(
        is_active=True
    ).order_by("title")


class ReaderBookDetailAPIView(RetrieveAPIView):

    serializer_class = ReaderBookSerializer
    queryset = ReaderBook.objects.filter(
        is_active=True
    )


def reader_page(request, book_id, page):

    book = ReaderBook.objects.get(
        id=book_id,
        is_active=True,
    )

    image_url = (
        settings.MEDIA_URL
        + "reader/books/"
        + book.folder_name
        + f"/page{page:03}.webp"
    )

    return JsonResponse(
        {
            "page": page,
            "image": image_url,
            "total_pages": book.total_pages,
        }
    )