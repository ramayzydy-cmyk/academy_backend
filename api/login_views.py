from django.contrib.auth.hashers import check_password
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import Student


class LoginAPIView(APIView):

    def post(self, request):

        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response(
                {
                    "success": False,
                    "message": "Email and password are required",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            student = Student.objects.get(email=email)

        except Student.DoesNotExist:
            return Response(
                {
                    "success": False,
                    "message": "Invalid email or password",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not check_password(password, student.password):
            return Response(
                {
                    "success": False,
                    "message": "Invalid email or password",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "success": True,
                "id": student.id,
                "full_name": student.full_name,
                "email": student.email,
            },
            status=status.HTTP_200_OK,
        )