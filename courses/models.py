from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=200)
    name_ar = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class CourseLevel(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='levels')
    title = models.CharField(max_length=200)
    title_ar = models.CharField(max_length=200, blank=True)
    code = models.CharField(max_length=50, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='levels/', blank=True, null=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title


class Skill(models.Model):
    level = models.ForeignKey(CourseLevel, on_delete=models.CASCADE, related_name='skills')
    title = models.CharField(max_length=200)
    title_ar = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title


class Unit(models.Model):
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name='units')
    title = models.CharField(max_length=200)
    title_ar = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title


class Lesson(models.Model):
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    title_ar = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    youtube_embed_url = models.URLField(blank=True)
    thumbnail = models.ImageField(upload_to='thumbnails/', blank=True, null=True)
    duration = models.CharField(max_length=20, blank=True)
    order = models.IntegerField(default=0)
    is_free = models.BooleanField(default=False)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title


class BookSeries(models.Model):
    title = models.CharField(max_length=200)
    title_ar = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    cover_image = models.ImageField(upload_to='book_series/', blank=True, null=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']
        verbose_name_plural = 'Book Series'

    def __str__(self):
        return self.title

class CurriculumSeries(models.Model):
    title = models.CharField(max_length=200)
    title_ar = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    cover_image = models.ImageField(upload_to='curriculum_series/', blank=True, null=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']
        verbose_name_plural = 'Curriculum Series'

    def __str__(self):
        return self.title

class Curriculum(models.Model):
    series = models.ForeignKey(CurriculumSeries, on_delete=models.SET_NULL, null=True, blank=True, related_name='curriculums')
    title = models.CharField(max_length=200)
    title_ar = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    pdf_file = models.FileField(upload_to='curriculums/', blank=True, null=True)
    audio_file = models.FileField(upload_to='curriculum_audio/', blank=True, null=True)
    cover_image = models.ImageField(upload_to='curriculum_covers/', blank=True, null=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title

class Book(models.Model):
    series = models.ForeignKey(BookSeries, on_delete=models.SET_NULL, null=True, blank=True, related_name='books')
    title = models.CharField(max_length=200)
    title_ar = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    pdf_file = models.FileField(upload_to='books/', blank=True, null=True)
    cover_image = models.ImageField(upload_to='book_covers/', blank=True, null=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title


# ─── Quiz System ─────────────────────────────────────────────────────────────

class Quiz(models.Model):
    lesson = models.OneToOneField(Lesson, on_delete=models.CASCADE, related_name='quiz')
    title = models.CharField(max_length=200, blank=True)
    pass_score = models.IntegerField(default=60, help_text="Minimum percentage to pass (0-100)")
    duration = models.IntegerField(default=10, help_text="Duration in minutes")
    random_questions_count = models.IntegerField(blank=True, null=True, help_text="Number of random questions to select. If blank, all questions are shown.")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Quiz'
        verbose_name_plural = 'Quizzes'

    def __str__(self):
        return f"Quiz for: {self.lesson.title}"


class Question(models.Model):
    QUESTION_TYPE_CHOICES = [
        ('text', 'Text Only'),
        ('image', 'Image + Text'),
        ('video', 'Video + Text'),
        ('audio', 'Audio + Text'),
    ]
    ANSWER_TYPE_CHOICES = [
        ('choices', 'Multiple Choice (Single Select)'),
        ('multi_choices', 'Multiple Selection (Checkboxes)'),
        ('text', 'Text Answer'),
    ]

    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField(help_text="Question text")
    question_type = models.CharField(max_length=10, choices=QUESTION_TYPE_CHOICES, default='text')
    answer_type = models.CharField(max_length=15, choices=ANSWER_TYPE_CHOICES, default='choices')
    correct_text_answer = models.CharField(max_length=500, blank=True, null=True, help_text="The correct text answer (if answer type is Text Answer)")
    youtube_url = models.URLField(blank=True, null=True, help_text="YouTube URL for video questions")
    video_file = models.FileField(upload_to='quiz_video/', blank=True, null=True, help_text="Video file for video questions")
    audio_file = models.FileField(upload_to='quiz_audio/', blank=True, null=True, help_text="Audio file for audio questions")
    image = models.ImageField(upload_to='quiz_images/', blank=True, null=True, help_text="Optional image for the question")
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Q{self.order}: {self.text[:60]}"


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{'✓' if self.is_correct else '✗'} {self.text[:60]}"


class StudentLessonProgress(models.Model):
    student_id = models.IntegerField(default=0)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='progress_records')
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student_id', 'lesson')
        verbose_name = 'Lesson Progress'
        verbose_name_plural = 'Lesson Progress Records'

    def __str__(self):
        return f"Student {self.student_id} - {self.lesson.title}"


class StudentQuizProgress(models.Model):
    student_id = models.IntegerField(default=0)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='student_progress')
    score = models.IntegerField(default=0)
    total = models.IntegerField(default=0)
    is_passed = models.BooleanField(default=False)
    failed_attempts = models.IntegerField(default=0)
    retry_available_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('student_id', 'quiz')
        verbose_name = 'Quiz Progress'
        verbose_name_plural = 'Quiz Progress Records'

    def __str__(self):
        return f"Student {self.student_id} - {self.quiz} - {'Passed' if self.is_passed else 'Failed'}"


class StudentQuestionAnswer(models.Model):
    student_id = models.IntegerField(default=0)
    quiz_progress = models.ForeignKey(StudentQuizProgress, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_choice = models.ForeignKey(Choice, on_delete=models.SET_NULL, null=True, blank=True, related_name='selected_by_students')
    selected_choices = models.ManyToManyField(Choice, blank=True, related_name='multi_selected_by_students')
    text_answer = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('student_id', 'question')
        verbose_name = 'Student Answer'
        verbose_name_plural = 'Student Answers'

    def __str__(self):
        return f"Student {self.student_id} - Q{self.question.id} Answer"

# ─── Level Tests ─────────────────────────────────────────────────────────────

class LevelTest(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    cover_image = models.ImageField(upload_to='level_tests/', blank=True, null=True)
    pass_score = models.IntegerField(default=60)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title

class LevelTestQuestion(models.Model):
    QUESTION_TYPE_CHOICES = [
        ('text', 'Text Only'),
        ('image', 'Image + Text'),
        ('video', 'Video + Text'),
        ('audio', 'Audio + Text'),
    ]
    ANSWER_TYPE_CHOICES = [
        ('choices', 'Multiple Choice (Single Select)'),
        ('multi_choices', 'Multiple Selection (Checkboxes)'),
        ('text', 'Text Answer'),
    ]

    level_test = models.ForeignKey(LevelTest, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField(help_text="Question text")
    question_type = models.CharField(max_length=10, choices=QUESTION_TYPE_CHOICES, default='text')
    answer_type = models.CharField(max_length=15, choices=ANSWER_TYPE_CHOICES, default='choices')
    correct_text_answer = models.CharField(max_length=500, blank=True, null=True, help_text="The correct text answer (if answer type is Text Answer)")
    youtube_url = models.URLField(blank=True, help_text="YouTube URL for video questions")
    video_file = models.FileField(upload_to='level_test_video/', blank=True, null=True)
    audio_file = models.FileField(upload_to='level_test_audio/', blank=True, null=True)
    image = models.ImageField(upload_to='level_test_images/', blank=True, null=True)
    
    time_limit_seconds = models.IntegerField(default=60, help_text="Time limit for this question in seconds")
    score = models.IntegerField(default=1, help_text="Score for this question")
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.level_test.title} - Q{self.order}: {self.text[:30]}"

class LevelTestChoice(models.Model):
    question = models.ForeignKey(LevelTestQuestion, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{'✓' if self.is_correct else '✗'} {self.text[:30]}"

class StudentLevelTestProgress(models.Model):
    student_id = models.IntegerField()
    level_test = models.ForeignKey(LevelTest, on_delete=models.CASCADE, related_name='student_progress')
    score = models.IntegerField(default=0)
    total = models.IntegerField(default=0)
    is_passed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-completed_at']

    def __str__(self):
        return f"Student {self.student_id} - {self.level_test}"

class StudentLevelTestAnswer(models.Model):
    progress = models.ForeignKey(StudentLevelTestProgress, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(LevelTestQuestion, on_delete=models.CASCADE)
    selected_choice = models.ForeignKey(LevelTestChoice, on_delete=models.SET_NULL, null=True, blank=True)
    selected_choices = models.ManyToManyField(LevelTestChoice, blank=True, related_name='+')
    text_answer = models.TextField(blank=True, null=True)
    is_correct = models.BooleanField(default=False)
    awarded_score = models.IntegerField(default=0)

    def __str__(self):
        return f"Progress {self.progress.id} - Q{self.question.id}"


# --- News --------------------------------------------------------------------

class NewsPost(models.Model):
    title = models.CharField(max_length=255, help_text="News title in English")
    title_ar = models.CharField(max_length=255, help_text="News title in Arabic")
    content = models.TextField(help_text="News content in English")
    content_ar = models.TextField(help_text="News content in Arabic")
    image = models.ImageField(upload_to='news_images/', blank=True, null=True, help_text="Optional news image")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


# --- Online Courses ----------------------------------------------------------

class OnlineCourse(models.Model):
    title = models.CharField(max_length=255, help_text="Course title in English")
    title_ar = models.CharField(max_length=255, help_text="Course title in Arabic")
    description = models.TextField(help_text="Course description in English")
    description_ar = models.TextField(help_text="Course description in Arabic")
    image = models.ImageField(upload_to='online_courses/', blank=True, null=True, help_text="Course cover image")
    start_date = models.DateField(help_text="Course start date")
    time = models.TimeField(help_text="Course daily/weekly time")
    duration_weeks = models.IntegerField(default=4, help_text="Duration in weeks")
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0.0, help_text="Course price (0 for free)")
    is_active = models.BooleanField(default=True, help_text="Is course currently open for registration?")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class OnlineLecture(models.Model):
    course = models.ForeignKey(OnlineCourse, on_delete=models.CASCADE, related_name='lectures')
    title = models.CharField(max_length=255, help_text="Lecture title in English")
    title_ar = models.CharField(max_length=255, help_text="Lecture title in Arabic")
    meeting_url = models.URLField(help_text="Zoom or Meet link")
    date = models.DateField(help_text="Lecture date")
    time = models.TimeField(help_text="Lecture time")
    order = models.IntegerField(default=0, help_text="Lecture order")

    class Meta:
        ordering = ['date', 'time', 'order']

    def __str__(self):
        return f"{self.course.title} - {self.title}"


# --- Home Dashboard Features -------------------------------------------------

class RecentActivity(models.Model):
    student = models.ForeignKey('accounts.Student', on_delete=models.CASCADE, related_name='recent_activities')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='recent_activities')
    progress_percentage = models.IntegerField(default=0)
    last_accessed = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-last_accessed']
        verbose_name_plural = 'Recent Activities'

    def __str__(self):
        return f"{self.student.full_name} - {self.lesson.title}"


class WordOfTheDay(models.Model):
    word_en = models.CharField(max_length=100, help_text="The word in English")
    translation_ar = models.CharField(max_length=200, help_text="Translation in Arabic")
    example_sentence = models.TextField(blank=True, null=True, help_text="Optional example sentence")
    is_active = models.BooleanField(default=True, help_text="Only one should be active ideally")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Words of the Day'

    def __str__(self):
        return self.word_en

# --- Gamification Features ---------------------------------------------------

class Badge(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    icon = models.ImageField(upload_to='badges/', blank=True, null=True)
    xp_required = models.PositiveIntegerField(default=0, help_text="XP points required to earn this badge")

    class Meta:
        ordering = ['xp_required']

    def __str__(self):
        return self.title

class StudentBadge(models.Model):
    student = models.ForeignKey('accounts.Student', on_delete=models.CASCADE, related_name='badges')
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE, related_name='earned_by')
    awarded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'badge')
        ordering = ['-awarded_at']

    def __str__(self):
        return f"{self.student.full_name} earned {self.badge.title}"

class CompletedLesson(models.Model):
    student = models.ForeignKey('accounts.Student', on_delete=models.CASCADE, related_name='completed_lessons')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='completed_by')
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'lesson')
        ordering = ['-completed_at']

    def __str__(self):
        return f"{self.student.full_name} completed {self.lesson.title}"
