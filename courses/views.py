from datetime import timedelta

from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets

from .models import (
    Category,
    CourseLevel,
    Skill,
    Unit,
    Lesson,
    Book,
    BookSeries,
    CurriculumSeries,
    Curriculum,
    LevelTest,
    LevelTestQuestion,
    LevelTestChoice,
    StudentLevelTestProgress,
    StudentLevelTestAnswer,
    Quiz,
    Question,
    Choice,
    StudentQuizProgress,
    StudentLessonProgress,
    NewsPost,
    OnlineCourse,
)

from .serializers import (
    CategorySerializer,
    LevelSerializer,
    SkillSerializer,
    UnitSerializer,
    LessonSerializer,
    BookSerializer,
    BookSeriesSerializer,
    CurriculumSerializer,
    CurriculumSeriesSerializer,
    QuizSerializer,
    QuestionSerializer,
    LevelTestSerializer,
    NewsPostSerializer,
    OnlineCourseSerializer,
)


# ----------------------------------------------------------------------
#  List endpoints
# ----------------------------------------------------------------------
class CategoryListAPIView(ListAPIView):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()


class LevelListAPIView(ListAPIView):
    serializer_class = LevelSerializer

    def get_queryset(self):
        category_id = self.kwargs["category_id"]
        return (
            CourseLevel.objects.filter(category_id=category_id)
            .order_by("order")
        )


class SkillListAPIView(ListAPIView):
    serializer_class = SkillSerializer

    def get_queryset(self):
        level_id = self.kwargs["level_id"]
        return (
            Skill.objects.filter(level_id=level_id)
            .order_by("order")
        )


class UnitListAPIView(ListAPIView):
    serializer_class = UnitSerializer

    def get_queryset(self):
        skill_id = self.kwargs["skill_id"]
        return (
            Unit.objects.filter(skill_id=skill_id)
            .order_by("order")
        )


class LessonListAPIView(ListAPIView):
    serializer_class = LessonSerializer

    def get_queryset(self):
        unit_id = self.kwargs["unit_id"]
        return (
            Lesson.objects.filter(unit_id=unit_id)
            .order_by("order")
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        student_id = self.request.query_params.get("student_id")
        if student_id:
            context["student_id"] = student_id
        return context


class BookListAPIView(ListAPIView):
    serializer_class = BookSerializer
    queryset = Book.objects.all().order_by("order")

class BookSeriesListAPIView(ListAPIView):
    serializer_class = BookSeriesSerializer
    queryset = BookSeries.objects.all().order_by("order")

class CurriculumSeriesListAPIView(ListAPIView):
    serializer_class = CurriculumSeriesSerializer
    queryset = CurriculumSeries.objects.all().order_by("order")

class CurriculumListAPIView(ListAPIView):
    serializer_class = CurriculumSerializer
    queryset = Curriculum.objects.all().order_by("order")

class LevelTestListAPIView(ListAPIView):
    serializer_class = LevelTestSerializer
    queryset = LevelTest.objects.all().order_by("order")
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        student_id = self.request.query_params.get("student_id")
        if student_id:
            context["student_id"] = student_id
        return context


# ----------------------------------------------------------------------
#  Quiz endpoints – custom logic
# ----------------------------------------------------------------------
class QuizDetailAPIView(APIView):
    """
    Returns quiz data together with information about whether the student
    can start the quiz or must wait for a cooldown period.
    """

    def get(self, request, lesson_id):
        student_id = request.query_params.get("student_id")

        quiz = get_object_or_404(Quiz, lesson_id=lesson_id)

        # If a student is supplied, check cooldown status
        if student_id:
            progress = StudentQuizProgress.objects.filter(
                student_id=student_id,
                quiz=quiz,
            ).first()

            if (
                progress
                and not progress.is_passed
                and progress.retry_available_at
                and progress.retry_available_at > timezone.now()
            ):
                remaining = int(
                    (progress.retry_available_at - timezone.now()).total_seconds()
                )
                return Response(
                    {
                        "can_start": False,
                        "remaining_seconds": remaining,
                        "message": "You must wait before trying again.",
                    },
                    status=status.HTTP_200_OK,
                )

        # No cooldown, or student not provided → quiz can be started
        # Handle dynamic/random questions if random_questions_count is defined
        if quiz.random_questions_count and quiz.random_questions_count > 0:
            all_questions = list(quiz.questions.all().order_by('order'))
            import random
            random.shuffle(all_questions)
            selected_questions = all_questions[:quiz.random_questions_count]
            selected_questions.sort(key=lambda x: x.order)
            
            # Serialize quiz header
            serializer = QuizSerializer(
                quiz,
                context={
                    "request": request,
                },
            )
            data = serializer.data
            # Override serialized questions with the shuffled/selected subset
            data["questions"] = QuestionSerializer(
                selected_questions, 
                many=True, 
                context={"request": request}
            ).data
        else:
            serializer = QuizSerializer(
                quiz,
                context={
                    "request": request,
                },
            )
            data = serializer.data

        data["can_start"] = True

        return Response(
            data,
            status=status.HTTP_200_OK,
        )


class QuizSubmitAPIView(APIView):
    """
    Handles submission of a quiz. Evaluates answers, updates the
    StudentQuizProgress record (including cooldown handling), and returns
    detailed results.
    """

    def post(self, request, lesson_id):
        student_id = request.data.get("student_id")
        answers = request.data.get("answers", {})

        if not student_id:
            return Response(
                {"error": "student_id is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ------------------------------------------------------------------
        #  Retrieve quiz and early lock check
        # ------------------------------------------------------------------
        quiz = get_object_or_404(Quiz, lesson_id=lesson_id)

        # Lock‑out logic: prevent submission while cooldown is active
        progress = StudentQuizProgress.objects.filter(
            student_id=student_id,
            quiz=quiz,
        ).first()

        if (
            progress
            and not progress.is_passed
            and progress.retry_available_at
            and progress.retry_available_at > timezone.now()
        ):
            remaining = int(
                (progress.retry_available_at - timezone.now()).total_seconds()
            )
            return Response(
                {
                    "success": False,
                    "message": "Quiz is locked",
                    "remaining_seconds": remaining,
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        # ------------------------------------------------------------------
        #  Evaluate answers
        # ------------------------------------------------------------------
        questions = quiz.questions.all()

        total_questions = questions.count()
        correct_count = 0
        details = []

        for q in questions:
            user_ans = answers.get(str(q.id))
            is_correct = False

            if q.answer_type == "choices":
                try:
                    choice = Choice.objects.get(id=user_ans, question=q)
                    if choice.is_correct:
                        is_correct = True
                except (Choice.DoesNotExist, ValueError):
                    pass
            elif q.answer_type == "text":
                if user_ans and q.correct_text_answer:
                    if (
                        str(user_ans).strip().lower()
                        == str(q.correct_text_answer).strip().lower()
                    ):
                        is_correct = True
            elif q.answer_type == "multi_choices":
                # user_ans should be a list of choice IDs
                if isinstance(user_ans, list):
                    correct_choices_set = set(q.choices.filter(is_correct=True).values_list('id', flat=True))
                    selected_set = set()
                    for val in user_ans:
                        try:
                            selected_set.add(int(val))
                        except (ValueError, TypeError):
                            pass
                    if correct_choices_set == selected_set and len(correct_choices_set) > 0:
                        is_correct = True

            if is_correct:
                correct_count += 1

            details.append(
                {
                    "question_id": q.id,
                    "is_correct": is_correct,
                }
            )

        # ------------------------------------------------------------------
        #  Pass/fail logic – 60 % is now the required threshold
        # ------------------------------------------------------------------
        PASS_PERCENTAGE = 60

        percentage = (
            (correct_count / total_questions) * 100
            if total_questions
            else 0
        )

        is_passed = percentage >= PASS_PERCENTAGE

        # ------------------------------------------------------------------
        #  Update / create StudentQuizProgress with cooldown handling
        # ------------------------------------------------------------------
        progress, created = StudentQuizProgress.objects.get_or_create(
            student_id=student_id,
            quiz=quiz,
        )

        if is_passed:
            # أول نجاح يحفظ الاجتياز نهائياً
            progress.is_passed = True
            progress.failed_attempts = 0
            progress.retry_available_at = None
        else:
            # إذا كان مجتازاً سابقاً فهي مراجعة فقط
            if not progress.is_passed:
                progress.failed_attempts += 1
                progress.retry_available_at = (
                    timezone.now() + timedelta(minutes=25)
                )

        progress.save()

        # ------------------------------------------------------------------
        #  Build response – include remaining_seconds for a failed attempt
        # ------------------------------------------------------------------
        remaining_seconds = 0
        if not is_passed:
            # 25 minutes expressed in seconds
            remaining_seconds = 25 * 60

        if is_passed:
            StudentLessonProgress.objects.get_or_create(
                student_id=student_id,
                lesson=quiz.lesson,
            )

        return Response(
            {
                "success": True,
                "is_passed": progress.is_passed,
                "is_review": progress.is_passed and not is_passed,
                "score": correct_count,
                "total": total_questions,
                "percentage": round(percentage, 2),
                "remaining_seconds": remaining_seconds,
                "details": details,
            },
            status=status.HTTP_200_OK,
        )


# ----------------------------------------------------------------------
#  Lesson completion endpoint
# ----------------------------------------------------------------------
class LessonCompleteAPIView(APIView):
    def post(self, request, lesson_id):
        student_id = request.data.get("student_id")
        if not student_id:
            return Response(
                {"error": "student_id is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Fixed typo: use get_object_or_404 (not get_object_or_454)
        lesson = get_object_or_404(Lesson, id=lesson_id)

        progress, created = StudentLessonProgress.objects.get_or_create(
            student_id=student_id,
            lesson=lesson,
        )

        return Response(
            {
                "success": True,
                "message": "Lesson marked as completed successfully",
            },
            status=status.HTTP_200_OK,
        )

# ----------------------------------------------------------------------
#  Level Test Submit endpoint
# ----------------------------------------------------------------------
class LevelTestSubmitAPIView(APIView):
    def post(self, request, test_id):
        student_id = request.data.get("student_id")
        answers_data = request.data.get("answers", [])
        
        if not student_id:
            return Response({"error": "student_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        test = get_object_or_404(LevelTest, id=test_id)
        
        # Check cooldown
        last_progress = StudentLevelTestProgress.objects.filter(student_id=student_id, level_test=test).order_by('-completed_at').first()
        if last_progress:
            from django.utils import timezone
            import datetime
            if timezone.now() < last_progress.completed_at + datetime.timedelta(hours=24):
                return Response({"error": "You must wait 24 hours before retaking this test."}, status=status.HTTP_400_BAD_REQUEST)

        total_score = 0
        total_possible = sum(q.score for q in test.questions.all())
        
        progress = StudentLevelTestProgress.objects.create(
            student_id=student_id,
            level_test=test,
        )
        
        details = []

        for item in answers_data:
            q_id = item.get("question_id")
            selected_choice_id = item.get("selected_choice_id")
            selected_choice_ids = item.get("selected_choices_ids", [])
            text_answer = item.get("text_answer", "")

            try:
                question = LevelTestQuestion.objects.get(id=q_id, level_test=test)
            except LevelTestQuestion.DoesNotExist:
                continue

            is_correct = False
            awarded_score = 0

            ans_record = StudentLevelTestAnswer(
                progress=progress,
                question=question,
                text_answer=text_answer
            )

            if question.answer_type == "choices" and selected_choice_id:
                try:
                    choice = LevelTestChoice.objects.get(id=selected_choice_id, question=question)
                    ans_record.selected_choice = choice
                    is_correct = choice.is_correct
                except LevelTestChoice.DoesNotExist:
                    pass
            elif question.answer_type == "multi_choices":
                pass # Handled after save to add M2M
            elif question.answer_type == "text":
                correct_choices = question.choices.filter(is_correct=True)
                for correct in correct_choices:
                    if correct.text.strip().lower() == text_answer.strip().lower():
                        is_correct = True
                        break

            if is_correct:
                awarded_score = question.score
                total_score += awarded_score
            
            ans_record.is_correct = is_correct
            ans_record.awarded_score = awarded_score
            ans_record.save()
            
            if question.answer_type == "multi_choices" and selected_choice_ids:
                choices = LevelTestChoice.objects.filter(id__in=selected_choice_ids, question=question)
                ans_record.selected_choices.set(choices)
                
                correct_choices_set = set(question.choices.filter(is_correct=True).values_list('id', flat=True))
                selected_set = set(c.id for c in choices)
                if correct_choices_set == selected_set and len(correct_choices_set) > 0:
                    is_correct = True
                    awarded_score = question.score
                    total_score += awarded_score
                    ans_record.is_correct = is_correct
                    ans_record.awarded_score = awarded_score
                    ans_record.save()

            details.append({
                "question_id": question.id,
                "is_correct": is_correct,
                "score_awarded": awarded_score,
                "question_score": question.score
            })

        progress.score = total_score
        progress.total = total_possible
        progress.is_passed = (total_score >= test.pass_score)
        progress.save()

        return Response(
            {
                "success": True,
                "score": total_score,
                "total": total_possible,
                "is_passed": progress.is_passed,
                "details": details,
            },
            status=status.HTTP_200_OK,
        )





# --- News --------------------------------------------------------------------

class NewsPostViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = NewsPost.objects.all().order_by('-created_at')
    serializer_class = NewsPostSerializer


# --- Online Courses ----------------------------------------------------------

class OnlineCourseViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = OnlineCourse.objects.filter(is_active=True).order_by('start_date')
    serializer_class = OnlineCourseSerializer