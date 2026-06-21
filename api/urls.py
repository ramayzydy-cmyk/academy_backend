from django.urls import path

from .views import (
    RegisterAPIView,
    HomeDashboardAPIView,
    LogActivityAPIView,
    CompleteLessonAPIView,
    GetStudentProfileAPIView,
    UpdateProfileAPIView,
)
from .login_views import LoginAPIView

urlpatterns = [
    path("register/", RegisterAPIView.as_view(), name="register"),
    path("login/", LoginAPIView.as_view(), name="login"),
    path("home-dashboard/<int:student_id>/", HomeDashboardAPIView.as_view(), name="home-dashboard"),
    path("log-activity/", LogActivityAPIView.as_view(), name="log-activity"),
    path("complete-lesson/", CompleteLessonAPIView.as_view(), name="complete-lesson"),
    path("profile/<int:student_id>/", GetStudentProfileAPIView.as_view(), name="student-profile"),
    path("profile/<int:student_id>/update/", UpdateProfileAPIView.as_view(), name="update-profile"),

]