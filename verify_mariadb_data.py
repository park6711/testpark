
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testpark_project.settings')
os.environ['USE_MYSQL'] = 'True'
os.environ['DB_HOST'] = '127.0.0.1'
os.environ['DB_PORT'] = '3306'
os.environ['DB_NAME'] = 'testpark'
os.environ['DB_USER'] = 'testpark'
os.environ['DB_PASSWORD'] = '**jeje4211'
django.setup()

from django.apps import apps
from django.contrib.auth import get_user_model

print('=== MariaDB 데이터 검증 ===\n')

total_records = 0
for app_config in apps.get_app_configs():
    for model in app_config.get_models():
        count = model.objects.count()
        if count > 0:
            print(f'{app_config.label}.{model.__name__}: {count} records')
            total_records += count

print(f'\n총 레코드 수: {total_records}')

