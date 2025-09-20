#!/usr/bin/env python
import os
import django
import sys

# Django 설정
sys.path.append('/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testpark_project.settings')
django.setup()

from stop.models import Stop

print("🔧 Stop 모델 필드 확인:")
print("=" * 40)

for field in Stop._meta.get_fields():
    field_info = f"  {field.name}: {field.__class__.__name__}"
    if hasattr(field, 'help_text') and field.help_text:
        field_info += f" - {field.help_text}"
    print(field_info)

print("\n✅ Stop 모델이 성공적으로 생성되었습니다!")
print(f"📊 데이터베이스 테이블명: {Stop._meta.db_table}")