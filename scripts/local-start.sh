#!/bin/bash

# TestPark 로컬 개발 환경 시작 스크립트
# 사용법: ./scripts/local-start.sh

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}   TestPark 로컬 개발 환경 시작      ${NC}"
echo -e "${CYAN}========================================${NC}"

# 환경 파일 확인
if [ ! -f ".env.local" ]; then
    echo -e "${YELLOW}⚠️  .env.local 파일이 없습니다. 생성 중...${NC}"
    if [ -f ".env.example" ]; then
        cp .env.example .env.local
        echo -e "${GREEN}✓ .env.local 파일이 생성되었습니다.${NC}"
        echo -e "${YELLOW}📝 .env.local 파일을 편집하여 설정을 완료하세요.${NC}"
        exit 0
    else
        echo -e "${RED}❌ .env.example 파일을 찾을 수 없습니다.${NC}"
        exit 1
    fi
fi

# Docker 실행 확인
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker가 실행되고 있지 않습니다.${NC}"
    echo -e "${YELLOW}Docker Desktop을 시작하고 다시 시도하세요.${NC}"
    exit 1
fi

# 기존 컨테이너 정리
echo -e "${BLUE}🧹 기존 컨테이너 정리 중...${NC}"
docker-compose -f docker-compose.dev.yml down 2>/dev/null || true

# 컨테이너 시작
echo -e "${BLUE}🚀 개발 환경 시작 중...${NC}"
docker-compose -f docker-compose.dev.yml up -d

# 상태 확인
echo -e "${BLUE}⏳ 서비스 준비 대기 중...${NC}"
sleep 5

# 서비스 상태 표시
echo -e "${GREEN}✅ 서비스 상태:${NC}"
docker-compose -f docker-compose.dev.yml ps

# 로그 확인 옵션
echo -e ""
echo -e "${CYAN}========================================${NC}"
echo -e "${GREEN}✨ 로컬 개발 환경이 시작되었습니다!${NC}"
echo -e "${CYAN}========================================${NC}"
echo -e ""
echo -e "${YELLOW}접속 정보:${NC}"
echo -e "  Django: ${GREEN}http://localhost:8000${NC}"
echo -e "  MariaDB: ${GREEN}localhost:3306${NC}"
echo -e "  Redis: ${GREEN}localhost:6379${NC}"
echo -e ""
echo -e "${YELLOW}유용한 명령어:${NC}"
echo -e "  로그 확인: ${CYAN}docker-compose -f docker-compose.dev.yml logs -f${NC}"
echo -e "  쉘 접속: ${CYAN}docker-compose -f docker-compose.dev.yml exec web bash${NC}"
echo -e "  중지: ${CYAN}docker-compose -f docker-compose.dev.yml down${NC}"
echo -e ""
echo -e "${YELLOW}DB 접속 정보:${NC}"
echo -e "  Host: localhost"
echo -e "  Port: 3306"
echo -e "  Database: testpark_dev"
echo -e "  User: testpark_dev"
echo -e "  Password: devpass123"

# 로그 실시간 보기 옵션
read -p "로그를 실시간으로 보시겠습니까? (y/n): " SHOW_LOGS
if [ "$SHOW_LOGS" = "y" ]; then
    docker-compose -f docker-compose.dev.yml logs -f
fi