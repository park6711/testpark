#!/usr/bin/env python
import os
import django
import sys

# Django 설정
sys.path.append('/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testpark_project.settings')
django.setup()

from license.models import License

# License 데이터 확인
total_count = License.objects.count()
print(f"📊 Total License records: {total_count}")

print("\n📋 First 10 records:")
for license_obj in License.objects.all()[:10]:
    print(f"  {license_obj.no}. {license_obj.sCompanyName} ({license_obj.sCeoName}) - {license_obj.sLicenseNo}")

print(f"\n✅ License 테스트 데이터 {total_count}개가 성공적으로 생성되었습니다!")