from rest_framework import serializers

from .models import (
    CourseLevel,
    Category,
    Skill,
    Unit,
    Lesson,
    Book,
    BookSeries,
    CurriculumSeries,
    Curriculum,
    Quiz,
    Question,
    Choice,
    StudentQuizProgress,
    StudentLessonProgress,
    LevelTest,
    LevelTestQuestion,
    LevelTestChoice,
    StudentLevelTestProgress,
    NewsPost,
    OnlineCourse,
    OnlineLecture,
)

from reader.models import ReaderBook


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category

        fields = [
            "id",
            "name",
            "name_ar",
        ]


class LevelSerializer(serializers.ModelSerializer):
    is_completed = serializers.SerializerMethodField()
    is_current = serializers.SerializerMethodField()
    is_locked = serializers.SerializerMethodField()

    class Meta:
        model = CourseLevel

        fields = [
            "id",
            "title",
            "title_ar",
            "code",
            "description",
            "image",
            "order",
            "is_completed",
            "is_current",
            "is_locked",
        ]
        
    def get_is_completed(self, obj):
        return False
        
    def get_is_current(self, obj):
        return False
        
    def get_is_locked(self, obj):
        return False


class SkillSerializer(serializers.ModelSerializer):

    class Meta:
        model = Skill

        fields = [
            "id",
            "title",
            "title_ar",
            "description",
            "order",
        ]


class UnitSerializer(serializers.ModelSerializer):

    class Meta:
        model = Unit

        fields = [
            "id",
            "title",
            "title_ar",
            "description",
            "order",
        ]


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ["id", "text"]


class QuestionSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True, read_only=True)
    audio_file = serializers.SerializerMethodField()
    video_file = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = [
            "id",
            "text",
            "question_type",
            "youtube_url",
            "video_file",
            "audio_file",
            "image",
            "answer_type",
            "choices",
            "order",
        ]

    def get_audio_file(self, obj):
        if obj.audio_file:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.audio_file.url)
            return obj.audio_file.url
        return None

    def get_video_file(self, obj):
        if obj.video_file:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.video_file.url)
            return obj.video_file.url
        return None

    def get_image(self, obj):
        if obj.image:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None


class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = ["id", "title", "questions"]


class LessonSerializer(serializers.ModelSerializer):
    is_completed = serializers.SerializerMethodField()
    is_locked = serializers.SerializerMethodField()
    has_quiz = serializers.SerializerMethodField()

    class Meta:
        model = Lesson

        fields = [
            "id",
            "title",
            "title_ar",
            "description",
            "youtube_embed_url",
            "thumbnail",
            "duration",
            "order",
            "is_free",
            "is_completed",
            "is_locked",
            "has_quiz",
        ]

    def get_is_completed(self, obj):
        student_id = self.context.get('student_id')
        if not student_id:
            return False

        if hasattr(obj, 'quiz'):
            return StudentQuizProgress.objects.filter(
                student_id=student_id,
                quiz=obj.quiz,
                is_passed=True,
            ).exists()

        return StudentLessonProgress.objects.filter(
            student_id=student_id,
            lesson=obj,
            is_completed=True,
        ).exists()

    def get_is_locked(self, obj):
        student_id = self.context.get('student_id')
        if not student_id:
            return True

        # First lesson in unit is unlocked by default
        previous_lessons = Lesson.objects.filter(
            unit=obj.unit,
            
            order__lt=obj.order,
        ).order_by('-order')

        if not previous_lessons.exists():
            return False

        prev_lesson = previous_lessons.first()
        if hasattr(prev_lesson, 'quiz'):
            prev_completed = StudentQuizProgress.objects.filter(
                student_id=student_id,
                quiz=prev_lesson.quiz,
                is_passed=True,
            ).exists()
        else:
            prev_completed = StudentLessonProgress.objects.filter(
                student_id=student_id,
                lesson=prev_lesson,
                is_completed=True,
            ).exists()

        return not prev_completed

    def get_has_quiz(self, obj):
        return hasattr(obj, 'quiz')


class BookSerializer(serializers.ModelSerializer):
    reader_book_id = serializers.SerializerMethodField()

    class Meta:
        model = Book

        fields = [
            "id",
            "title",
            "title_ar",
            "description",
            "cover_image",
            "pdf_file",
            "order",
            "series",
            "reader_book_id",
        ]

    def get_reader_book_id(self, obj):
        reader_book = ReaderBook.objects.filter(
            source_type="book",
            source_id=obj.id,
            is_active=True,
        ).first()

        if reader_book:
            return reader_book.id

        return None

class BookSeriesSerializer(serializers.ModelSerializer):
    books = serializers.SerializerMethodField()
    class Meta:
        model = BookSeries
        fields = ['id', 'title', 'title_ar', 'description', 'cover_image', 'order', 'books']

    def get_books(self, obj):
        return BookSerializer(obj.books.all(), many=True, context=self.context).data

class CurriculumSerializer(serializers.ModelSerializer):
    reader_book_id = serializers.SerializerMethodField()

    class Meta:
        model = Curriculum

        fields = [
            "id",
            "title",
            "title_ar",
            "description",
            "pdf_file",
            "audio_file",
            "cover_image",
            "order",
            "series",
            "reader_book_id",
        ]

    def get_reader_book_id(self, obj):
        reader_book = ReaderBook.objects.filter(
            source_type="curriculum",
            source_id=obj.id,
            is_active=True,
        ).first()

        if reader_book:
            return reader_book.id

        return None

class CurriculumSeriesSerializer(serializers.ModelSerializer):
    curriculums = serializers.SerializerMethodField()
    class Meta:
        model = CurriculumSeries
        fields = ['id', 'title', 'title_ar', 'description', 'cover_image', 'order', 'curriculums']

    def get_curriculums(self, obj):
        return CurriculumSerializer(obj.curriculums.all(), many=True, context=self.context).data

class LevelTestChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = LevelTestChoice
        fields = ['id', 'text']

class LevelTestQuestionSerializer(serializers.ModelSerializer):
    choices = LevelTestChoiceSerializer(many=True, read_only=True)
    audio_file = serializers.SerializerMethodField()
    video_file = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    class Meta:
        model = LevelTestQuestion
        fields = [
            "id", "text", "question_type", "youtube_url", "video_file", "audio_file", "image",
            "answer_type", "choices", "time_limit_seconds", "score", "order"
        ]

    def get_audio_file(self, obj):
        if obj.audio_file:
            request = self.context.get("request")
            if request: return request.build_absolute_uri(obj.audio_file.url)
            return obj.audio_file.url
        return None

    def get_video_file(self, obj):
        if obj.video_file:
            request = self.context.get("request")
            if request: return request.build_absolute_uri(obj.video_file.url)
            return obj.video_file.url
        return None

    def get_image(self, obj):
        if obj.image:
            request = self.context.get("request")
            if request: return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None

class LevelTestSerializer(serializers.ModelSerializer):
    questions = LevelTestQuestionSerializer(many=True, read_only=True)
    is_locked = serializers.SerializerMethodField()
    time_remaining = serializers.SerializerMethodField()

    class Meta:
        model = LevelTest
        fields = ['id', 'title', 'description', 'cover_image', 'pass_score', 'order', 'questions', 'is_locked', 'time_remaining']

    def get_is_locked(self, obj):
        student_id = self.context.get('student_id')
        if not student_id: return False
        
        last_progress = StudentLevelTestProgress.objects.filter(student_id=student_id, level_test=obj).order_by('-completed_at').first()
        if not last_progress: return False
        
        from django.utils import timezone
        import datetime
        if timezone.now() < last_progress.completed_at + datetime.timedelta(hours=24):
            return True
        return False

    def get_time_remaining(self, obj):
        student_id = self.context.get('student_id')
        if not student_id: return 0
        
        last_progress = StudentLevelTestProgress.objects.filter(student_id=student_id, level_test=obj).order_by('-completed_at').first()
        if not last_progress: return 0
        
        from django.utils import timezone
        import datetime
        next_available = last_progress.completed_at + datetime.timedelta(hours=24)
        if timezone.now() < next_available:
            return (next_available - timezone.now()).total_seconds()
        return 0



# --- News --------------------------------------------------------------------

class NewsPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsPost
        fields = '__all__'


# --- Online Courses ----------------------------------------------------------

class OnlineLectureSerializer(serializers.ModelSerializer):
    class Meta:
        model = OnlineLecture
        fields = '__all__'

class OnlineCourseSerializer(serializers.ModelSerializer):
    lectures = OnlineLectureSerializer(many=True, read_only=True)

    class Meta:
        model = OnlineCourse
        fields = '__all__'