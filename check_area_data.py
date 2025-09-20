#!/usr/bin/env python3

import os
import sys
import django

# Django 설정
sys.path.append('/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testpark_project.settings')
django.setup()

from area.models import Area

# Area 데이터 확인
area_count = Area.objects.count()
print(f'Area 총 개수: {area_count}')

if area_count > 0:
    print('\n첫 10개 지역:')
    for area in Area.objects.all()[:10]:
        print(f'  {area.no}: {area.get_full_name()}')

    print('\n광역지역 (sCity가 빈 값):')
    for area in Area.objects.filter(sCity="")[:5]:
        print(f'  {area.no}: {area.get_full_name()}')

    print('\n시군구지역 (sCity가 있는 값):')
    for area in Area.objects.exclude(sCity="")[:10]:
        print(f'  {area.no}: {area.get_full_name()}')
else:
    print('Area 테이블에 데이터가 없습니다.')
    print('create_area_test_data.py를 실행해서 테스트 데이터를 생성해야 합니다.')