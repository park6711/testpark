#!/bin/bash

# TestPark 로컬 개발 환경 자동 구성 스크립트
# 작성일: 2025년 1월
# 용도: Docker 기반 개발 환경 자동 구성 및 검증

set -e  # 에러 발생 시 즉시 종료

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 함수: 성공 메시지
success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# 함수: 에러 메시지
error() {
    echo -e "${RED}❌ $1${NC}"
    exit 1
}

# 함수: 정보 메시지
info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# 함수: 경고 메시지
warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# 함수: 구분선 출력
print_separator() {
    echo "=================================================="
}

# 헤더 출력
clear
echo "=================================================="
echo "   🚀 TestPark 로컬 개발 환경 구성 도구"
echo "=================================================="
echo ""

# 1. 사전 요구사항 체크
info "사전 요구사항 확인 중..."

# Docker 확인
if ! command -v docker &> /dev/null; then
    error "Docker가 설치되어 있지 않습니다. Docker를 먼저 설치해주세요."
fi
success "Docker 설치 확인 ($(docker --version))"

# Docker Compose 확인
if ! command -v docker-compose &> /dev/null; then
    error "Docker Compose가 설치되어 있지 않습니다."
fi
success "Docker Compose 설치 확인 ($(docker-compose --version))"

# Git 확인
if ! command -v git &> /dev/null; then
    error "Git이 설치되어 있지 않습니다."
fi
success "Git 설치 확인 ($(git --version))"

print_separator

# 2. 프로젝트 디렉토리 확인
info "프로젝트 구조 확인 중..."

if [ ! -f "docker-compose.yml" ]; then
    error "docker-compose.yml 파일을 찾을 수 없습니다. 프로젝트 루트 디렉토리에서 실행해주세요."
fi

if [ ! -f "manage.py" ]; then
    error "manage.py 파일을 찾을 수 없습니다. Django 프로젝트 루트인지 확인해주세요."
fi

success "프로젝트 구조 확인 완료"

print_separator

# 3. .env 파일 설정
info "환경 변수 설정 중..."

if [ ! -f ".env" ]; then
    warning ".env 파일이 없습니다. 기본 템플릿으로 생성합니다."

    cat > .env << 'EOF'
# Django 설정
DEBUG=True
SECRET_KEY=django-insecure-local-development-key-change-in-production
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# 데이터베이스 설정 (MariaDB)
DB_ENGINE=django.db.backends.mysql
DB_NAME=testpark_db
DB_USER=testpark_user
DB_PASSWORD=testpark_password_2024
DB_HOST=mariadb
DB_PORT=3306

# MariaDB Root 설정
MYSQL_ROOT_PASSWORD=root_password_2024
MYSQL_DATABASE=testpark_db
MYSQL_USER=testpark_user
MYSQL_PASSWORD=testpark_password_2024

# 네이버 OAuth 설정
NAVER_CLIENT_ID=your_naver_client_id_here
NAVER_CLIENT_SECRET=your_naver_client_secret_here

# 잔디 웹훅
JANDI_WEBHOOK_URL=https://wh.jandi.com/connect-api/webhook/your_webhook_here

# 타임존 설정
TZ=Asia/Seoul
EOF
    success ".env 파일 생성 완료"
    warning "⚠️  네이버 OAuth 정보를 실제 값으로 수정해주세요!"
else
    success ".env 파일 확인 완료"
fi

print_separator

# 4. Docker 환경 구성
info "Docker 컨테이너 구성 중..."

# 기존 컨테이너 정리
if [ "$(docker ps -aq -f name=testpark)" ]; then
    warning "기존 컨테이너 발견. 재시작합니다..."
    docker-compose down
fi

# Docker 이미지 빌드
info "Docker 이미지 빌드 중... (시간이 걸릴 수 있습니다)"
docker-compose build

# 컨테이너 실행
info "컨테이너 시작 중..."
docker-compose up -d

# 컨테이너 시작 대기
info "서비스 시작 대기 중..."
sleep 10

print_separator

# 5. 서비스 상태 확인
info "서비스 상태 확인 중..."

# TODO(human): Docker와 MariaDB 서비스 상태를 확인하는 코드를 작성해주세요
# docker-compose ps를 사용하여 컨테이너 상태 확인
# MariaDB 포트(3306)와 Django 포트(8000) 연결 테스트

print_separator

# 6. 데이터베이스 마이그레이션
info "데이터베이스 마이그레이션 실행 중..."

# 마이그레이션 실행
docker-compose exec -T testpark python manage.py migrate

success "마이그레이션 완료"

print_separator

# 7. 정적 파일 수집
info "정적 파일 수집 중..."
docker-compose exec -T testpark python manage.py collectstatic --noinput
success "정적 파일 수집 완료"

print_separator

# 8. 최종 확인
echo ""
echo "=================================================="
echo "   ✅ 로컬 개발 환경 구성 완료!"
echo "=================================================="
echo ""
echo "📌 접속 정보:"
echo "   - Django Admin: http://localhost:8000/admin/"
echo "   - 메인 페이지: http://localhost:8000/"
echo "   - MariaDB: localhost:3306"
echo ""
echo "📌 유용한 명령어:"
echo "   - 로그 확인: docker-compose logs -f"
echo "   - 쉘 접속: docker-compose exec testpark bash"
echo "   - DB 접속: docker-compose exec mariadb mysql -u root -p"
echo "   - 중지: docker-compose down"
echo ""
echo "🚀 개발을 시작하세요!"
echo ""