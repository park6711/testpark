#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testpark_project.settings')
django.setup()

from point.models import Point

# 업체 10번의 최신 포인트 조회
latest = Point.objects.filter(noCompany=10).order_by('-time', '-no').first()

if latest:
    print(f'업체 10번의 최신 포인트:')
    print(f'  - Point ID: {latest.no}')
    print(f'  - nRemainPoint: {latest.nRemainPoint:,}원')
    print(f'  - time: {latest.time}')
    print(f'  - nType: {latest.nType} ({latest.get_nType_display()})')
    print(f'  - sWorker: {latest.sWorker}')
else:
    print('업체 10번의 포인트 내역이 없습니다.')
    print('시작 잔액: 0원')
