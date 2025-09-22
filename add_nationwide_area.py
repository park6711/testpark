#!/usr/bin/env python3

import os
import sys
import django

# Django 설정
sys.path.append('/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testpark_project.settings')
django.setup()

from area.models import Area

# 전국 지역 추가 (ID: 0)
try:
    nationwide = Area.objects.get(no=0)
    print(f'전국 지역이 이미 존재합니다: {nationwide.get_full_name()}')
except Area.DoesNotExist:
    nationwide = Area.objects.create(
        no=0,
        sState="전국",
        sCity=""
    )
    print(f'전국 지역을 추가했습니다: {nationwide.get_full_name()}')

# 현재 데이터 확인
print(f'\n현재 Area 총 개수: {Area.objects.count()}')
print('\n전국 및 광역지역:')
for area in Area.objects.filter(sCity="").order_by('no')[:10]:
    print(f'  {area.no}: {area.get_full_name()}')