from django.contrib.auth.hashers import make_password
from rest_framework import serializers

from accounts.models import Student


class StudentRegisterSerializer(serializers.ModelSerializer):

    class Meta:
        model = Student

        fields = [
            "full_name",
            "age",
            "gender",
            "email",
            "password",
            "english_level",
        ]

        extra_kwargs = {
            "password": {
                "write_only": True,
            }
        }

    def create(self, validated_data):

        return Student.objects.create(
            full_name=validated_data["full_name"],
            age=validated_data["age"],
            gender=validated_data["gender"],
            email=validated_data["email"],
            password=make_password(validated_data["password"]),
            english_level=validated_data["english_level"],
        )