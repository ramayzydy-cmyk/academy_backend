from rest_framework import serializers

from .models import ReaderBook


class ReaderBookSerializer(serializers.ModelSerializer):

    class Meta:
        model = ReaderBook

        fields = [
            "id",
            "title",
            "title_ar",
            "cover_image",
            "folder_name",
            "total_pages",
            "source_type",
            "source_id",
        ]