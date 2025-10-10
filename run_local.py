#!/usr/bin/env python3
"""
운영 DB와 연결하여 로컬 Django 서버 실행
"""
import os
import sys
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 환경 변수 설정 (운영 DB 사용)
os.environ['USE_PRODUCTION_DB'] = 'True'
os.environ['USE_MYSQL'] = 'True'

# Django 실행
os.system('python3 manage.py runserver 8000')