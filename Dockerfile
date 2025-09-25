# Python 3.12 최신 버전 기반 Django 애플리케이션 (React 빌드 통합)
FROM python:3.12-slim

# 환경 변수 설정
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=testpark_project.settings

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 의존성 설치 (Node.js 포함)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        git \
        nodejs \
        npm \
    && rm -rf /var/lib/apt/lists/*

# pip 업그레이드
RUN pip install --upgrade pip

# Python 의존성 설치
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Django 프로젝트 파일 복사
COPY . /app/

# React 앱 빌드 (선택적)
RUN if [ -d "frontend" ] && [ -f "frontend/package.json" ]; then \
        cd frontend && \
        npm install --legacy-peer-deps && \
        npm run build && \
        echo "React build completed" || echo "React build failed, continuing..."; \
    else \
        echo "No React app found"; \
    fi

# Django 데이터베이스 마이그레이션 및 정적 파일 수집
RUN python manage.py migrate --noinput || echo "Migration will be handled at runtime"
RUN python manage.py collectstatic --noinput || echo "No static files to collect"

# 포트 노출
EXPOSE 8000

# Django 개발 서버 시작 (최신 Django 기능 사용)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]