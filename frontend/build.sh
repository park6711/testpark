#!/bin/bash

# React 앱 빌드 스크립트

echo "🚀 React 앱 빌드 시작..."

# 의존성 설치
echo "📦 의존성 설치 중..."
npm install

# 빌드 실행
echo "🔨 프로덕션 빌드 중..."
npm run build

# Django 정적 파일 디렉토리로 복사
DJANGO_STATIC_DIR="/var/www/testpark/static/react"
echo "📂 빌드 파일을 Django 정적 디렉토리로 복사 중..."

# 기존 파일 삭제
rm -rf $DJANGO_STATIC_DIR

# 디렉토리 생성
mkdir -p $DJANGO_STATIC_DIR/js
mkdir -p $DJANGO_STATIC_DIR/css
mkdir -p $DJANGO_STATIC_DIR/media

# 빌드 파일 복사
cp -r build/static/js/* $DJANGO_STATIC_DIR/js/
cp -r build/static/css/* $DJANGO_STATIC_DIR/css/
if [ -d "build/static/media" ]; then
    cp -r build/static/media/* $DJANGO_STATIC_DIR/media/
fi

echo "✅ 빌드 완료!"
echo "📍 빌드 파일 위치: $DJANGO_STATIC_DIR"
echo ""
echo "🎯 다음 단계:"
echo "1. Django collectstatic 실행: python manage.py collectstatic"
echo "2. 서버 재시작: sudo systemctl restart apache2"