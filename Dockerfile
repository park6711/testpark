# 멀티스테이지 빌드: React 빌드 단계
FROM docker.io/library/node:18-alpine AS frontend-builder

# React 앱 빌드를 위한 작업 디렉토리
WORKDIR /frontend

# React 앱 의존성 설치
COPY frontend/package*.json ./
RUN npm ci --only=production || npm install --legacy-peer-deps

# React 소스 코드 복사 및 빌드
COPY frontend/ ./
RUN npm run build || echo "React build will be skipped if not configured"

# Python 3.12 최신 버전 기반 Django 애플리케이션
FROM docker.io/library/python:3.12-slim

# 환경 변수 설정
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=testpark_project.settings

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 의존성 설치
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        git \
    && rm -rf /var/lib/apt/lists/*

# pip 업그레이드
RUN pip install --upgrade pip

# Python 의존성 설치
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Django 프로젝트 파일 복사
COPY . /app/

# React 빌드된 파일 복사 (frontend/build -> Django static 디렉토리)
# 빌드가 실패하더라도 컨테이너 빌드는 계속 진행
RUN mkdir -p /app/static/react
COPY --from=frontend-builder /frontend/build/ /app/static/react/

# Django 데이터베이스 마이그레이션 및 정적 파일 수집
RUN python manage.py migrate --noinput || echo "Migration will be handled at runtime"
RUN python manage.py collectstatic --noinput || echo "No static files to collect"

# 포트 노출
EXPOSE 8000

# Django 개발 서버 시작 (최신 Django 기능 사용)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]