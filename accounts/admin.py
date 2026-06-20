from django.contrib import admin
from .models import Student, StudentStats, DailyLogin


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "full_name",
        "email",
        "age",
        "gender",
        "english_level",
        "created_at",
    )

    search_fields = (
        "full_name",
        "email",
    )

    list_filter = (
        "gender",
        "english_level",
    )

    ordering = (
        "-created_at",
    )

@admin.register(StudentStats)
class StudentStatsAdmin(admin.ModelAdmin):
    list_display = ('student', 'current_level_label', 'level_progress', 'streak_days', 'xp_points')
    search_fields = ('student__full_name',)

@admin.register(DailyLogin)
class DailyLoginAdmin(admin.ModelAdmin):
    list_display = ('student', 'date')
    search_fields = ('student__full_name',)
    list_filter = ('date',)