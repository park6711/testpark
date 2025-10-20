#!/bin/bash

# TestPark 로컬 개발 환경 초기화 스크립트
# 사용법: ./scripts/local-reset.sh
# 주의: 모든 로컬 데이터가 삭제됩니다!

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${RED}========================================${NC}"
echo -e "${RED}⚠️  경고: 로컬 개발 환경 초기화${NC}"
echo -e "${RED}========================================${NC}"
echo -e "${YELLOW}이 작업은 다음을 수행합니다:${NC}"
echo "• 모든 Docker 컨테이너 중지 및 삭제"
echo "• 데이터베이스 볼륨 삭제"
echo "• Docker 이미지 재빌드"
echo "• 초기 데이터 설정"
echo ""

read -p "정말 진행하시겠습니까? (yes/no): " CONFIRM
if [ "$CONFIRM" != "yes" ]; then
    echo -e "${YELLOW}초기화가 취소되었습니다.${NC}"
    exit 0
fi

# 1. 컨테이너 및 볼륨 삭제
echo -e "${BLUE}1. 기존 환경 정리 중...${NC}"
docker-compose -f docker-compose.dev.yml down -v --remove-orphans

# 2. 이미지 삭제
echo -e "${BLUE}2. Docker 이미지 삭제 중...${NC}"
docker-compose -f docker-compose.dev.yml down --rmi local

# 3. 캐시 정리
echo -e "${BLUE}3. Docker 캐시 정리 중...${NC}"
docker system prune -f

# 4. 환경 변수 확인
echo -e "${BLUE}4. 환경 변수 확인 중...${NC}"
if [ ! -f ".env.local" ]; then
    cp .env.example .env.local
    echo -e "${YELLOW}.env.local 파일이 생성되었습니다.${NC}"
fi

# 5. 새로운 환경 시작
echo -e "${BLUE}5. 새 환경 시작 중...${NC}"
docker-compose -f docker-compose.dev.yml up -d --build

# 6. 초기 설정
echo -e "${BLUE}6. 초기 설정 진행 중...${NC}"
sleep 10  # DB가 준비될 때까지 대기

# 마이그레이션
echo -e "${YELLOW}마이그레이션 실행 중...${NC}"
docker-compose -f docker-compose.dev.yml exec -T web python manage.py migrate --no-input

# 정적 파일 수집
echo -e "${YELLOW}정적 파일 수집 중...${NC}"
docker-compose -f docker-compose.dev.yml exec -T web python manage.py collectstatic --no-input

# 슈퍼유저 생성 옵션
echo -e "${BLUE}7. 관리자 계정 생성${NC}"
read -p "관리자 계정을 생성하시겠습니까? (y/n): " CREATE_SUPER
if [ "$CREATE_SUPER" = "y" ]; then
    docker-compose -f docker-compose.dev.yml exec web python manage.py createsuperuser
fi

# 완료
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✨ 로컬 개발 환경 초기화 완료!${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "접속 정보:"
echo -e "  Django: ${GREEN}http://localhost:8000${NC}"
echo -e "  관리자: ${GREEN}http://localhost:8000/admin/${NC}"
echo -e ""
echo -e "DB 접속:"
echo -e "  Host: localhost:3306"
echo -e "  User: testpark_dev"
echo -e "  Pass: devpass123"