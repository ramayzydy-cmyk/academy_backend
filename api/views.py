from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import StudentRegisterSerializer


class RegisterAPIView(APIView):

    def post(self, request):

        serializer = StudentRegisterSerializer(data=request.data)

        if serializer.is_valid():

            student = serializer.save()

            return Response(
                {
                    "success": True,
                    "id": student.id,
                    "full_name": student.full_name,
                    "email": student.email,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            {
                "success": False,
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

from accounts.models import Student, StudentStats
from courses.models import RecentActivity, WordOfTheDay

class HomeDashboardAPIView(APIView):
    def get(self, request, student_id):
        try:
            student = Student.objects.get(id=student_id)
        except Student.DoesNotExist:
            return Response({"success": False, "error": "Student not found"}, status=status.HTTP_404_NOT_FOUND)

        # Get or create stats
        stats, created = StudentStats.objects.get_or_create(
            student=student,
            defaults={
                'current_level_label': student.english_level if student.english_level else 'A1',
            }
        )

        # Get latest word of the day
        wotd = WordOfTheDay.objects.filter(is_active=True).order_by('-created_at').first()
        wotd_data = None
        if wotd:
            wotd_data = {
                "word_en": wotd.word_en,
                "translation_ar": wotd.translation_ar,
                "example_sentence": wotd.example_sentence,
            }

        # Get recent activity
        recent = RecentActivity.objects.filter(student=student).order_by('-last_accessed').first()
        recent_data = None
        if recent:
            recent_data = {
                "lesson_id": recent.lesson.id,
                "lesson_title": recent.lesson.title,
                "unit_title": recent.lesson.unit.title,
                "progress_percentage": recent.progress_percentage,
                "thumbnail": request.build_absolute_uri(recent.lesson.thumbnail.url) if recent.lesson.thumbnail else None,
            }

        data = {
            "success": True,
            "data": {
                "stats": {
                    "streak_days": stats.streak_days,
                    "xp_points": stats.xp_points,
                    "lessons_completed": stats.lessons_completed,
                    "badges_earned": stats.badges_earned,
                    "current_level_label": stats.current_level_label,
                    "level_progress": stats.level_progress,
                },
                "word_of_the_day": wotd_data,
                "recent_activity": recent_data,
            }
        }
        return Response(data, status=status.HTTP_200_OK)

from django.utils import timezone
from datetime import timedelta
from accounts.models import DailyLogin
from courses.models import Badge, StudentBadge, CompletedLesson, Lesson

class LogActivityAPIView(APIView):
    def post(self, request):
        student_id = request.data.get('student_id')
        if not student_id:
            return Response({"success": False, "error": "student_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            student = Student.objects.get(id=student_id)
        except Student.DoesNotExist:
            return Response({"success": False, "error": "Student not found"}, status=status.HTTP_404_NOT_FOUND)

        today = timezone.now().date()
        
        # Try to create today's login
        login, created = DailyLogin.objects.get_or_create(student=student, date=today)
        
        if created:
            # It's a new day, calculate streak
            stats, _ = StudentStats.objects.get_or_create(student=student)
            
            yesterday = today - timedelta(days=1)
            logged_yesterday = DailyLogin.objects.filter(student=student, date=yesterday).exists()
            
            if logged_yesterday:
                stats.streak_days += 1
            else:
                stats.streak_days = 1  # Reset to 1 since they missed a day
                
            stats.xp_points += 5 # Daily reward
            stats.save()
            
            return Response({"success": True, "message": "Streak updated", "streak_days": stats.streak_days, "xp_points": stats.xp_points}, status=status.HTTP_200_OK)
            
        return Response({"success": True, "message": "Already logged in today"}, status=status.HTTP_200_OK)

class CompleteLessonAPIView(APIView):
    def post(self, request):
        student_id = request.data.get('student_id')
        lesson_id = request.data.get('lesson_id')
        
        if not student_id or not lesson_id:
            return Response({"success": False, "error": "student_id and lesson_id are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            student = Student.objects.get(id=student_id)
            lesson = Lesson.objects.get(id=lesson_id)
        except (Student.DoesNotExist, Lesson.DoesNotExist):
            return Response({"success": False, "error": "Student or Lesson not found"}, status=status.HTTP_404_NOT_FOUND)

        completed, created = CompletedLesson.objects.get_or_create(student=student, lesson=lesson)
        
        if created:
            stats, _ = StudentStats.objects.get_or_create(student=student)
            stats.lessons_completed += 1
            stats.xp_points += 20 # Reward for completing a lesson
            
            # Check for new badges
            new_badges_earned = []
            available_badges = Badge.objects.filter(xp_required__lte=stats.xp_points).exclude(earned_by__student=student)
            
            for badge in available_badges:
                StudentBadge.objects.create(student=student, badge=badge)
                stats.badges_earned += 1
                new_badges_earned.append(badge.title)
                
            stats.save()
            
            return Response({
                "success": True, 
                "message": "Lesson completed", 
                "xp_points": stats.xp_points,
                "new_badges": new_badges_earned
            }, status=status.HTTP_200_OK)
            
        return Response({"success": True, "message": "Lesson already completed"}, status=status.HTTP_200_OK)