########################################
# TestPark 완전한 프로덕션 Dockerfile
# 모든 기능을 포함한 최종 버전
########################################

# Stage 1: React 프론트엔드 빌드
FROM node:18-alpine AS frontend-builder

WORKDIR /frontend

# package.json 파일들 복사
COPY frontend/package*.json ./

# 의존성 설치 (devDependencies 포함하여 빌드 가능하게)
RUN npm install --legacy-peer-deps

# React 소스 전체 복사
COPY frontend/ ./

# 프로덕션 빌드
RUN npm run build && \
    echo "✅ React 프로덕션 빌드 완료" && \
    ls -la build/

########################################
# Stage 2: Django 애플리케이션
########################################
FROM python:3.12-slim

# 환경 변수 설정
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=testpark_project.settings \
    NODE_ENV=production \
    PORT=8000

# 작업 디렉토리
WORKDIR /app

# 시스템 패키지 설치 (프로덕션 필수 항목)
RUN apt-get update && apt-get install -y --no-install-recommends \
    # 빌드 도구
    gcc \
    g++ \
    python3-dev \
    # PostgreSQL 클라이언트 (필요시)
    libpq-dev \
    # 네트워크 도구
    curl \
    netcat-openbsd \
    # 이미지 처리 (Pillow용)
    libjpeg-dev \
    zlib1g-dev \
    libpng-dev \
    # 기타 유틸리티
    vim \
    htop \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Python 패키지 업그레이드
RUN pip install --upgrade pip setuptools wheel

# requirements.txt 복사 및 설치
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# 프로덕션 서버 패키지 추가 설치
RUN pip install --no-cache-dir \
    gunicorn \
    whitenoise \
    django-cors-headers \
    django-environ \
    psycopg2-binary

# Django 프로젝트 전체 복사
COPY . /app/

# React 빌드 파일 복사 (frontend/build -> static)
COPY --from=frontend-builder /frontend/build /app/static/react
COPY --from=frontend-builder /frontend/build/static /app/static/

# 정적 파일 디렉토리 구조 생성
RUN mkdir -p \
    /app/static \
    /app/staticfiles \
    /app/media \
    /app/logs \
    /app/static/css \
    /app/static/js \
    /app/static/images \
    /app/static/admin \
    /app/static/react

# 권한 설정
RUN chmod -R 755 /app && \
    chmod -R 777 /app/media /app/logs

# Django 정적 파일 수집
RUN python manage.py collectstatic --noinput --clear || true

# 데이터베이스 마이그레이션 파일 생성
RUN python manage.py makemigrations --noinput || true

# 엔트리포인트 스크립트 생성
RUN cat > /app/entrypoint.sh << 'EOF'
#!/bin/bash
set -e

echo "🚀 TestPark 프로덕션 서버 시작..."
echo "📅 시작 시간: $(date '+%Y-%m-%d %H:%M:%S')"

# 환경 변수 확인
echo "🔍 환경 설정 확인..."
echo "  - DJANGO_SETTINGS_MODULE: $DJANGO_SETTINGS_MODULE"
echo "  - DATABASE_URL: ${DATABASE_URL:-SQLite}"
echo "  - ALLOWED_HOSTS: ${ALLOWED_HOSTS:-*}"

# 데이터베이스 대기 (PostgreSQL 사용 시)
if [ -n "$DATABASE_URL" ]; then
    echo "⏳ 데이터베이스 연결 대기 중..."
    while ! nc -z ${DATABASE_HOST:-db} ${DATABASE_PORT:-5432}; do
        echo "  데이터베이스 대기 중..."
        sleep 1
    done
    echo "✅ 데이터베이스 연결 준비 완료"
fi

# 마이그레이션 실행
echo "🔄 데이터베이스 마이그레이션..."
python manage.py migrate --noinput

# 정적 파일 수집
echo "📦 정적 파일 수집..."
python manage.py collectstatic --noinput --clear

# 슈퍼유저 생성 (필요시)
if [ -n "$DJANGO_SUPERUSER_USERNAME" ]; then
    echo "👤 슈퍼유저 확인/생성..."
    python manage.py shell << PYTHON_SCRIPT
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='$DJANGO_SUPERUSER_USERNAME').exists():
    User.objects.create_superuser(
        username='$DJANGO_SUPERUSER_USERNAME',
        email='${DJANGO_SUPERUSER_EMAIL:-admin@testpark.com}',
        password='${DJANGO_SUPERUSER_PASSWORD:-testpark1234}'
    )
    print('✅ 슈퍼유저 생성 완료')
else:
    print('✅ 슈퍼유저 이미 존재')
PYTHON_SCRIPT
fi

echo "✅ 초기화 완료!"
echo "🌐 서버 시작: 0.0.0.0:${PORT:-8000}"

# Gunicorn 실행
exec gunicorn testpark_project.wsgi:application \
    --bind 0.0.0.0:${PORT:-8000} \
    --workers ${GUNICORN_WORKERS:-4} \
    --threads ${GUNICORN_THREADS:-2} \
    --worker-class sync \
    --worker-tmp-dir /dev/shm \
    --access-logfile - \
    --error-logfile - \
    --log-level ${LOG_LEVEL:-info} \
    --timeout 120 \
    --keep-alive 5 \
    --max-requests 1000 \
    --max-requests-jitter 50 \
    --preload
EOF

# 엔트리포인트 실행 권한
RUN chmod +x /app/entrypoint.sh

# 헬스체크 스크립트
RUN cat > /app/healthcheck.sh << 'EOF'
#!/bin/bash
curl -f http://localhost:${PORT:-8000}/health/ || curl -f http://localhost:${PORT:-8000}/ || exit 1
EOF
RUN chmod +x /app/healthcheck.sh

# 포트 노출
EXPOSE 8000

# 헬스체크 설정
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD /app/healthcheck.sh

# 컨테이너 실행
ENTRYPOINT ["/app/entrypoint.sh"]