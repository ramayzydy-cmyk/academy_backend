import re

with open(r'D:\newprojects\academy74\academy_backend\courses\views.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('from rest_framework import status', 'from rest_framework import status, viewsets')

content = content.replace('    StudentLessonProgress,\n)', '    StudentLessonProgress,\n    NewsPost,\n    OnlineCourse,\n)')

content = content.replace('    LevelTestSerializer,\n)', '    LevelTestSerializer,\n    NewsPostSerializer,\n    OnlineCourseSerializer,\n)')

content += '''

# --- News --------------------------------------------------------------------

class NewsPostViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = NewsPost.objects.all().order_by('-created_at')
    serializer_class = NewsPostSerializer


# --- Online Courses ----------------------------------------------------------

class OnlineCourseViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = OnlineCourse.objects.filter(is_active=True).order_by('start_date')
    serializer_class = OnlineCourseSerializer
'''

with open(r'D:\newprojects\academy74\academy_backend\courses\views.py', 'w', encoding='utf-8') as f:
    f.write(content)
