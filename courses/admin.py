from django.contrib import admin
from .models import (
    Category, CourseLevel, Skill, Unit, Lesson,
    Quiz, Question, Choice, StudentLessonProgress, StudentQuizProgress, StudentQuestionAnswer,
    LevelTest, LevelTestQuestion, LevelTestChoice, StudentLevelTestProgress, StudentLevelTestAnswer,
    OnlineCourse, OnlineLecture, RecentActivity, WordOfTheDay,
    Badge, StudentBadge, CompletedLesson
)


# ─── Inline Classes ──────────────────────────────────────────────────────────

class CourseLevelInline(admin.TabularInline):
    model = CourseLevel
    extra = 1


class SkillInline(admin.TabularInline):
    model = Skill
    extra = 1


class UnitInline(admin.TabularInline):
    model = Unit
    extra = 1


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1
    fields = ['title', 'title_ar', 'youtube_embed_url', 'duration', 'is_free', 'order']


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 3
    fields = ['text', 'is_correct', 'order']

class LevelTestChoiceInline(admin.TabularInline):
    model = LevelTestChoice
    extra = 3
    fields = ['text', 'is_correct', 'order']


class QuestionInline(admin.StackedInline):
    model = Question
    extra = 1
    fields = ['text', 'question_type', 'answer_type', 'correct_text_answer', 'youtube_url', 'audio_file', 'image', 'order']
    show_change_link = True


class StudentQuestionAnswerInline(admin.TabularInline):
    model = StudentQuestionAnswer
    extra = 0
    fields = ['question', 'display_selected_choices', 'text_answer']
    readonly_fields = ['question', 'display_selected_choices', 'text_answer']
    can_delete = False

    def display_selected_choices(self, obj):
        if obj.question.answer_type == 'multi_choices':
            return ", ".join([c.text for c in obj.selected_choices.all()])
        elif obj.question.answer_type == 'choices':
            return obj.selected_choice.text if obj.selected_choice else "-"
        return "N/A"
    display_selected_choices.short_description = "Selected Choice(s)"


# ─── Model Admins ────────────────────────────────────────────────────────────

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'name_ar', 'order']
    inlines = [CourseLevelInline]


@admin.register(CourseLevel)
class CourseLevelAdmin(admin.ModelAdmin):
    list_display = ['title', 'title_ar', 'category', 'order']
    list_filter = ['category']
    inlines = [SkillInline]


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ['title', 'title_ar', 'level', 'order']
    list_filter = ['level']
    inlines = [UnitInline]


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ['title', 'title_ar', 'skill', 'order']
    list_filter = ['skill']
    inlines = [LessonInline]


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['title', 'title_ar', 'unit', 'is_free', 'order', 'has_quiz_badge']
    list_filter = ['unit', 'is_free']
    fields = ['unit', 'title', 'title_ar', 'description', 'youtube_embed_url', 'thumbnail', 'duration', 'is_free', 'order']

    def has_quiz_badge(self, obj):
        return hasattr(obj, 'quiz')
    has_quiz_badge.boolean = True
    has_quiz_badge.short_description = 'Has Quiz'


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ['lesson', 'title', 'pass_score', 'question_count']
    inlines = [QuestionInline]
    readonly_fields = ['quiz_statistics']

    class Media:
        js = ('courses/admin/question_admin.js',)

    def question_count(self, obj):
        return obj.questions.count()
    question_count.short_description = 'Questions'

    def quiz_statistics(self, obj):
        if not obj.pk:
            return "يرجى حفظ الاختبار أولاً لرؤية الإحصائيات."
        
        attempts = StudentQuizProgress.objects.filter(quiz=obj)
        total_attempts = attempts.count()
        if total_attempts == 0:
            return "لا يوجد أي محاولات تقديم لهذا الاختبار بعد."
        
        passed_attempts = attempts.filter(is_passed=True).count()
        pass_rate = (passed_attempts / total_attempts) * 100
        
        questions = obj.questions.all()
        question_stats = []
        
        for q in questions:
            answers = StudentQuestionAnswer.objects.filter(question=q)
            total_answers = answers.count()
            if total_answers == 0:
                continue
            
            correct_count = 0
            for ans in answers:
                if ans.question.answer_type == 'choices':
                    if ans.selected_choice and ans.selected_choice.is_correct:
                        correct_count += 1
                elif ans.question.answer_type == 'multi_choices':
                    correct_choice_ids = set(ans.question.choices.filter(is_correct=True).values_list('id', flat=True))
                    selected_choice_ids = set(ans.selected_choices.values_list('id', flat=True))
                    if correct_choice_ids == selected_choice_ids:
                        correct_count += 1
                else:
                    if ans.text_answer and ans.text_answer.strip():
                        correct_count += 1
            
            success_rate = (correct_count / total_answers) * 100
            question_stats.append((q, success_rate))
        
        hardest_q_str = "لا يوجد بيانات كافية"
        easiest_q_str = "لا يوجد بيانات كافية"
        if question_stats:
            question_stats.sort(key=lambda x: x[1])
            hardest_q = question_stats[0]
            easiest_q = question_stats[-1]
            hardest_q_str = f"السؤال {hardest_q[0].order}: {hardest_q[0].text[:60]} ({hardest_q[1]:.1f}% إجابات صحيحة)"
            easiest_q_str = f"السؤال {easiest_q[0].order}: {easiest_q[0].text[:60]} ({easiest_q[1]:.1f}% إجابات صحيحة)"
        
        from django.utils.html import format_html
        return format_html(
            """
            <div style="background: #0d1f14; padding: 20px; border-radius: 12px; border: 2.5px solid #22c55e; margin-bottom: 24px; color: white; direction: rtl; font-family: sans-serif;">
                <h3 style="color: #22c55e; margin-top: 0; margin-bottom: 15px; font-size: 18px; border-bottom: 1px solid #22c55e; padding-bottom: 8px;">📊 إحصائيات اختبار الدرس</h3>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                    <div>
                        <p style="margin: 5px 0;">👥 <strong>عدد المختبرين:</strong> <span style="font-size: 16px; color: #22c55e; font-weight: bold;">{}</span></p>
                        <p style="margin: 5px 0;">📈 <strong>معدل النجاح:</strong> <span style="font-size: 16px; color: #22c55e; font-weight: bold;">{:.1f}%</span></p>
                    </div>
                    <div>
                        <p style="margin: 5px 0;">🔥 <strong>أسهل سؤال:</strong> <span style="color: #c8e1b7;">{}</span></p>
                        <p style="margin: 5px 0;">⚠️ <strong>أصعب سؤال:</strong> <span style="color: #f7dcdb;">{}</span></p>
                    </div>
                </div>
            </div>
            """,
            total_attempts,
            pass_rate,
            easiest_q_str,
            hardest_q_str
        )
    
    quiz_statistics.short_description = "إحصائيات الاختبار"


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['quiz', 'text_preview', 'question_type', 'answer_type', 'order']
    list_filter = ['quiz', 'question_type', 'answer_type']
    inlines = [ChoiceInline]

    class Media:
        js = ('courses/admin/question_admin.js',)

    def text_preview(self, obj):
        return obj.text[:60]
    text_preview.short_description = 'Question'

@admin.register(StudentLessonProgress)
class StudentLessonProgressAdmin(admin.ModelAdmin):
    list_display = ['student_id', 'lesson', 'completed_at']
    list_filter = ['lesson']


@admin.register(StudentQuizProgress)
class StudentQuizProgressAdmin(admin.ModelAdmin):
    list_display = ['student_id', 'quiz', 'score', 'total', 'is_passed', 'completed_at']
    list_filter = ['is_passed']
    inlines = [StudentQuestionAnswerInline]


# ─── CourseLevel Tests ─────────────────────────────────────────────────────────────

@admin.register(LevelTest)
class LevelTestAdmin(admin.ModelAdmin):
    list_display = ['title', 'pass_score', 'order', 'created_at']

@admin.register(LevelTestQuestion)
class LevelTestQuestionAdmin(admin.ModelAdmin):
    list_display = ['level_test', 'text_preview', 'question_type', 'score', 'time_limit_seconds', 'order']
    list_filter = ['level_test', 'question_type', 'answer_type']
    inlines = [LevelTestChoiceInline]

    class Media:
        js = ('courses/admin/question_admin.js',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('level_test', 'text', 'order', 'score', 'time_limit_seconds')
        }),
        ('Type Settings', {
            'fields': ('question_type', 'answer_type', 'correct_text_answer')
        }),
        ('Media Options (Fill only for specific types)', {
            'fields': ('image', 'video_file', 'youtube_url', 'audio_file'),
            'description': 'Leave these blank if the question type is Text Only. Use video fields for Video type, audio for Audio type, etc.'
        }),
    )

    def text_preview(self, obj):
        return obj.text[:60]
    text_preview.short_description = 'Question'

@admin.register(StudentLevelTestProgress)
class StudentLevelTestProgressAdmin(admin.ModelAdmin):
    list_display = ['student_id', 'level_test', 'score', 'total', 'is_passed', 'completed_at']
    list_filter = ['is_passed', 'level_test']

@admin.register(StudentLevelTestAnswer)
class StudentLevelTestAnswerAdmin(admin.ModelAdmin):
    list_display = ['progress', 'question', 'is_correct', 'awarded_score']





# --- Online Courses ----------------------------------------------------------

class OnlineLectureInline(admin.TabularInline):
    model = OnlineLecture
    extra = 1

@admin.register(OnlineCourse)
class OnlineCourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'start_date', 'time', 'is_active', 'price']
    list_filter = ['is_active', 'start_date']
    search_fields = ['title', 'title_ar']
    inlines = [OnlineLectureInline]

@admin.register(RecentActivity)
class RecentActivityAdmin(admin.ModelAdmin):
    list_display = ('student', 'lesson', 'progress_percentage', 'last_accessed')
    list_filter = ('last_accessed',)
    search_fields = ('student__full_name', 'lesson__title')

@admin.register(WordOfTheDay)
class WordOfTheDayAdmin(admin.ModelAdmin):
    list_display = ('word_en', 'translation_ar', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('word_en', 'translation_ar')

# --- Gamification ------------------------------------------------------------

@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ('title', 'xp_required')
    search_fields = ('title',)

@admin.register(StudentBadge)
class StudentBadgeAdmin(admin.ModelAdmin):
    list_display = ('student', 'badge', 'awarded_at')
    list_filter = ('badge', 'awarded_at')
    search_fields = ('student__full_name',)

@admin.register(CompletedLesson)
class CompletedLessonAdmin(admin.ModelAdmin):
    list_display = ('student', 'lesson', 'completed_at')
    list_filter = ('completed_at',)
    search_fields = ('student__full_name', 'lesson__title')
