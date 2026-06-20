from django.db import models


class Student(models.Model):

    GENDER_CHOICES = (
        ("Male", "Male"),
        ("Female", "Female"),
    )

    LEVEL_CHOICES = (
        ("Beginner", "Beginner"),
        ("Elementary", "Elementary"),
        ("Intermediate", "Intermediate"),
        ("Upper Intermediate", "Upper Intermediate"),
        ("Advanced", "Advanced"),
    )

    full_name = models.CharField(max_length=200)
    age = models.PositiveIntegerField()
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)

    email = models.EmailField(unique=True)

    password = models.CharField(max_length=255)

    english_level = models.CharField(
        max_length=30,
        choices=LEVEL_CHOICES,
    )

    bio = models.TextField(blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name

class StudentStats(models.Model):
    student = models.OneToOneField(Student, on_delete=models.CASCADE, related_name='stats')
    streak_days = models.PositiveIntegerField(default=0)
    xp_points = models.PositiveIntegerField(default=0)
    lessons_completed = models.PositiveIntegerField(default=0)
    badges_earned = models.PositiveIntegerField(default=0)
    
    # Auto-calculated or updated based on lessons_completed
    current_level_label = models.CharField(max_length=50, default='A1')
    level_progress = models.PositiveIntegerField(default=0) # percentage 0-100

    def __str__(self):
        return f"Stats for {self.student.full_name}"

class DailyLogin(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='daily_logins')
    date = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'date')

    def __str__(self):
        return f"{self.student.full_name} logged in on {self.date}"