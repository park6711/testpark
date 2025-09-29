
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testpark_project.settings')
os.environ['USE_MYSQL'] = 'False'  # 임시로 SQLite 사용
django.setup()

from django.contrib.auth import get_user_model
from django.apps import apps

# 각 모델의 레코드 수 확인
for app_config in apps.get_app_configs():
    for model in app_config.get_models():
        count = model.objects.count()
        if count > 0:
            print(f'{app_config.label}.{model.__name__}: {count} records')

