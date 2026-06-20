from django.urls import path
from . import views

urlpatterns = [
    # Categories & hierarchy
    path('categories/', views.CategoryListAPIView.as_view(), name='categories'),
    path('categories/<int:category_id>/levels/', views.LevelListAPIView.as_view(), name='levels'),
    path('levels/<int:level_id>/skills/', views.SkillListAPIView.as_view(), name='skills'),
    path('skills/<int:skill_id>/units/', views.UnitListAPIView.as_view(), name='units'),
    path('units/<int:unit_id>/lessons/', views.LessonListAPIView.as_view(), name='lessons'),

    # Library
    path('books/', views.BookListAPIView.as_view(), name='books'),
    path('book-series/', views.BookSeriesListAPIView.as_view(), name='book-series'),
    path('curriculums/', views.CurriculumListAPIView.as_view(), name='curriculums'),
    path('curriculum-series/', views.CurriculumSeriesListAPIView.as_view(), name='curriculum-series'),

    # Level Tests
    path('level-tests/', views.LevelTestListAPIView.as_view(), name='level-tests'),
    path('level-tests/<int:test_id>/submit/', views.LevelTestSubmitAPIView.as_view(), name='level-test-submit'),

    # Quiz
    path('lessons/<int:lesson_id>/quiz/', views.QuizDetailAPIView.as_view(), name='quiz-detail'),
    path('lessons/<int:lesson_id>/quiz/submit/', views.QuizSubmitAPIView.as_view(), name='quiz-submit'),
    path('lessons/<int:lesson_id>/complete/', views.LessonCompleteAPIView.as_view(), name='lesson-complete'),

    # News & Online Courses
    path('news/', views.NewsPostViewSet.as_view({'get': 'list'}), name='news'),
    path('online-courses/', views.OnlineCourseViewSet.as_view({'get': 'list'}), name='online-courses'),
]
