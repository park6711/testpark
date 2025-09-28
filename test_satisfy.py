#!/usr/bin/env python3
import os
import sys
import django

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testpark_project.settings')
django.setup()

from django.test import Client
from django.urls import reverse

# 테스트 클라이언트 생성
client = Client()

# satisfy_list URL 확인
try:
    url = reverse('evaluation:satisfy_list')
    print(f"URL 확인: {url}")

    # 페이지 요청
    response = client.get(url)
    print(f"응답 상태: {response.status_code}")

    if response.status_code == 200:
        print("페이지 로드 성공!")
        # 응답 내용 일부 확인
        content = response.content.decode('utf-8')
        if '고객만족도 이력' in content:
            print("✓ 페이지 제목 확인됨")
        else:
            print("✗ 페이지 제목이 없습니다")

    elif response.status_code == 302:
        print(f"리다이렉션: {response.url}")
    else:
        print(f"오류: {response.status_code}")

except Exception as e:
    print(f"에러 발생: {e}")
    import traceback
    traceback.print_exc()