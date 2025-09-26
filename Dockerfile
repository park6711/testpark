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

# Django 정적 파일 먼저 수집 (React 파일 복사 전에)
RUN python manage.py collectstatic --noinput --clear || true

# React 빌드 파일을 staticfiles로 직접 복사 (collectstatic 이후)
# 이렇게 하면 React chunk 파일들이 삭제되지 않음
COPY --from=frontend-builder /frontend/build/static/css /app/staticfiles/css/
COPY --from=frontend-builder /frontend/build/static/js /app/staticfiles/js/
COPY --from=frontend-builder /frontend/build/static/media /app/staticfiles/media/
COPY --from=frontend-builder /frontend/build /app/staticfiles/react/

# 권한 설정
RUN chmod -R 755 /app && \
    chmod -R 777 /app/media /app/logs

# 데이터베이스 마이그레이션 파일 생성
RUN python manage.py makemigrations --noinput || true

# 엔트리포인트 스크립트 생성
RUN echo '#!/bin/bash' > /app/entrypoint.sh && \
    echo 'set -e' >> /app/entrypoint.sh && \
    echo '' >> /app/entrypoint.sh && \
    echo 'echo "🚀 TestPark 프로덕션 서버 시작..."' >> /app/entrypoint.sh && \
    echo 'echo "📅 시작 시간: $(date '\''+%Y-%m-%d %H:%M:%S'\'')"' >> /app/entrypoint.sh && \
    echo '' >> /app/entrypoint.sh && \
    echo '# 환경 변수 확인' >> /app/entrypoint.sh && \
    echo 'echo "🔍 환경 설정 확인..."' >> /app/entrypoint.sh && \
    echo 'echo "  - DJANGO_SETTINGS_MODULE: $DJANGO_SETTINGS_MODULE"' >> /app/entrypoint.sh && \
    echo 'echo "  - DATABASE_URL: ${DATABASE_URL:-SQLite}"' >> /app/entrypoint.sh && \
    echo 'echo "  - ALLOWED_HOSTS: ${ALLOWED_HOSTS:-*}"' >> /app/entrypoint.sh && \
    echo '' >> /app/entrypoint.sh && \
    echo '# 데이터베이스 대기 (PostgreSQL 사용 시)' >> /app/entrypoint.sh && \
    echo 'if [ -n "$DATABASE_URL" ]; then' >> /app/entrypoint.sh && \
    echo '    echo "⏳ 데이터베이스 연결 대기 중..."' >> /app/entrypoint.sh && \
    echo '    while ! nc -z ${DATABASE_HOST:-db} ${DATABASE_PORT:-5432}; do' >> /app/entrypoint.sh && \
    echo '        echo "  데이터베이스 대기 중..."' >> /app/entrypoint.sh && \
    echo '        sleep 1' >> /app/entrypoint.sh && \
    echo '    done' >> /app/entrypoint.sh && \
    echo '    echo "✅ 데이터베이스 연결 준비 완료"' >> /app/entrypoint.sh && \
    echo 'fi' >> /app/entrypoint.sh && \
    echo '' >> /app/entrypoint.sh && \
    echo '# 마이그레이션 실행' >> /app/entrypoint.sh && \
    echo 'echo "🔄 데이터베이스 마이그레이션..."' >> /app/entrypoint.sh && \
    echo 'python manage.py migrate --noinput' >> /app/entrypoint.sh && \
    echo '' >> /app/entrypoint.sh && \
    echo '# 정적 파일 수집 (이미 빌드 시 완료, 변경사항만 추가)' >> /app/entrypoint.sh && \
    echo 'echo "📦 정적 파일 확인..."' >> /app/entrypoint.sh && \
    echo '# collectstatic은 빌드 시 이미 완료, React chunk 파일 보존' >> /app/entrypoint.sh && \
    echo 'ls -la /app/staticfiles/js/*.chunk.js | head -3' >> /app/entrypoint.sh && \
    echo '' >> /app/entrypoint.sh && \
    echo '# 슈퍼유저 생성 (필요시)' >> /app/entrypoint.sh && \
    echo 'if [ -n "$DJANGO_SUPERUSER_USERNAME" ]; then' >> /app/entrypoint.sh && \
    echo '    echo "👤 슈퍼유저 확인/생성..."' >> /app/entrypoint.sh && \
    echo '    python manage.py shell << PYTHON_SCRIPT' >> /app/entrypoint.sh && \
    echo 'from django.contrib.auth import get_user_model' >> /app/entrypoint.sh && \
    echo 'User = get_user_model()' >> /app/entrypoint.sh && \
    echo 'if not User.objects.filter(username='"'"'$DJANGO_SUPERUSER_USERNAME'"'"').exists():' >> /app/entrypoint.sh && \
    echo '    User.objects.create_superuser(' >> /app/entrypoint.sh && \
    echo '        username='"'"'$DJANGO_SUPERUSER_USERNAME'"'"',' >> /app/entrypoint.sh && \
    echo '        email='"'"'${DJANGO_SUPERUSER_EMAIL:-admin@testpark.com}'"'"',' >> /app/entrypoint.sh && \
    echo '        password='"'"'${DJANGO_SUPERUSER_PASSWORD:-testpark1234}'"'"'' >> /app/entrypoint.sh && \
    echo '    )' >> /app/entrypoint.sh && \
    echo '    print('"'"'✅ 슈퍼유저 생성 완료'"'"')' >> /app/entrypoint.sh && \
    echo 'else:' >> /app/entrypoint.sh && \
    echo '    print('"'"'✅ 슈퍼유저 이미 존재'"'"')' >> /app/entrypoint.sh && \
    echo 'PYTHON_SCRIPT' >> /app/entrypoint.sh && \
    echo 'fi' >> /app/entrypoint.sh && \
    echo '' >> /app/entrypoint.sh && \
    echo 'echo "✅ 초기화 완료!"' >> /app/entrypoint.sh && \
    echo 'echo "🌐 서버 시작: 0.0.0.0:${PORT:-8000}"' >> /app/entrypoint.sh && \
    echo '' >> /app/entrypoint.sh && \
    echo '# Gunicorn 실행' >> /app/entrypoint.sh && \
    echo 'exec gunicorn testpark_project.wsgi:application \' >> /app/entrypoint.sh && \
    echo '    --bind 0.0.0.0:${PORT:-8000} \' >> /app/entrypoint.sh && \
    echo '    --workers ${GUNICORN_WORKERS:-4} \' >> /app/entrypoint.sh && \
    echo '    --threads ${GUNICORN_THREADS:-2} \' >> /app/entrypoint.sh && \
    echo '    --worker-class sync \' >> /app/entrypoint.sh && \
    echo '    --worker-tmp-dir /dev/shm \' >> /app/entrypoint.sh && \
    echo '    --access-logfile - \' >> /app/entrypoint.sh && \
    echo '    --error-logfile - \' >> /app/entrypoint.sh && \
    echo '    --log-level ${LOG_LEVEL:-info} \' >> /app/entrypoint.sh && \
    echo '    --timeout 120 \' >> /app/entrypoint.sh && \
    echo '    --keep-alive 5 \' >> /app/entrypoint.sh && \
    echo '    --max-requests 1000 \' >> /app/entrypoint.sh && \
    echo '    --max-requests-jitter 50 \' >> /app/entrypoint.sh && \
    echo '    --preload' >> /app/entrypoint.sh

# 엔트리포인트 실행 권한
RUN chmod +x /app/entrypoint.sh

# 헬스체크 스크립트
RUN echo '#!/bin/bash' > /app/healthcheck.sh && \
    echo 'curl -f http://localhost:${PORT:-8000}/health/ || curl -f http://localhost:${PORT:-8000}/ || exit 1' >> /app/healthcheck.sh && \
    chmod +x /app/healthcheck.sh

# 포트 노출
EXPOSE 8000

# 헬스체크 설정
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD /app/healthcheck.sh

# 컨테이너 실행
ENTRYPOINT ["/app/entrypoint.sh"]