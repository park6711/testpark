#!/usr/bin/env python
"""
날짜 디버깅 스크립트
"""

import os
import sys
import django

# Django 설정
sys.path.append('/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testpark_project.settings')
django.setup()

from django.utils import timezone
from datetime import datetime

def debug_date():
    print("=== 날짜 디버깅 ===")

    # 현재 시간 (UTC)
    now_utc = timezone.now()
    print(f"현재 UTC 시간: {now_utc}")

    # 현재 날짜 (UTC)
    today_utc = now_utc.date()
    print(f"현재 UTC 날짜: {today_utc}")

    # 시간대 설정 확인
    print(f"TIME_ZONE 설정: {timezone.get_current_timezone()}")

    # 로컬 시간
    now_local = timezone.localtime()
    print(f"현재 로컬 시간: {now_local}")

    # 로컬 날짜
    today_local = now_local.date()
    print(f"현재 로컬 날짜: {today_local}")

    # Python 기본 시간
    now_python = datetime.now()
    print(f"Python datetime.now(): {now_python}")

    today_python = now_python.date()
    print(f"Python today: {today_python}")

if __name__ == '__main__':
    debug_date()