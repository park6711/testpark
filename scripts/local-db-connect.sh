#!/bin/bash

# 로컬 개발 DB 접속 정보 출력 스크립트
# 사용법: ./scripts/local-db-connect.sh

# 색상 정의
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}   TestPark 로컬 DB 접속 정보        ${NC}"
echo -e "${CYAN}========================================${NC}"
echo -e ""

# Docker 컨테이너 확인
if docker ps | grep -q testpark-dev-db; then
    echo -e "${GREEN}✅ MariaDB 컨테이너가 실행 중입니다.${NC}"
    echo -e ""
else
    echo -e "${YELLOW}⚠️  MariaDB 컨테이너가 실행되고 있지 않습니다.${NC}"
    echo -e "${YELLOW}먼저 ./scripts/local-start.sh를 실행하세요.${NC}"
    echo -e ""
fi

echo -e "${BLUE}📊 HeidiSQL / DBeaver 접속 정보:${NC}"
echo -e "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "  ${YELLOW}호스트:${NC}     localhost"
echo -e "  ${YELLOW}포트:${NC}       3306"
echo -e "  ${YELLOW}사용자:${NC}     testpark_dev"
echo -e "  ${YELLOW}비밀번호:${NC}   devpass123"
echo -e "  ${YELLOW}데이터베이스:${NC} testpark_dev"
echo -e "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e ""

echo -e "${BLUE}💻 MySQL CLI 접속 명령:${NC}"
echo -e "${CYAN}docker-compose -f docker-compose.dev.yml exec db mariadb -u testpark_dev -pdevpass123 testpark_dev${NC}"
echo -e ""

echo -e "${BLUE}🔧 Root 계정 정보:${NC}"
echo -e "  ${YELLOW}사용자:${NC}     root"
echo -e "  ${YELLOW}비밀번호:${NC}   devroot123"
echo -e ""

echo -e "${BLUE}📝 유용한 SQL 명령:${NC}"
echo -e "  테이블 목록: ${CYAN}SHOW TABLES;${NC}"
echo -e "  데이터베이스 목록: ${CYAN}SHOW DATABASES;${NC}"
echo -e "  테이블 구조: ${CYAN}DESCRIBE table_name;${NC}"
echo -e ""

# 연결 테스트
echo -e "${BLUE}🔍 연결 테스트:${NC}"
if docker-compose -f docker-compose.dev.yml exec -T db mariadb -u testpark_dev -pdevpass123 -e "SELECT 1" testpark_dev > /dev/null 2>&1; then
    echo -e "${GREEN}✅ 데이터베이스 연결 성공!${NC}"
else
    echo -e "${YELLOW}⚠️  데이터베이스 연결 실패. 컨테이너를 확인하세요.${NC}"
fi