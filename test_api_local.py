import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'academy_backend.settings')
django.setup()

from django.test import Client

c = Client()
try:
    response = c.get('/api/categories/')
    print("Status code:", response.status_code)
    print("Content:", response.content.decode('utf-8'))
except Exception as e:
    import traceback
    traceback.print_exc()

try:
    response = c.get('/api/skills/1/units/')
    print("Status code:", response.status_code)
    print("Content:", response.content.decode('utf-8'))
except Exception as e:
    import traceback
    traceback.print_exc()
