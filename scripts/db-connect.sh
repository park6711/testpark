#!/bin/bash

# TestPark MariaDB 접속 스크립트
# 사용법: ./scripts/db-connect.sh

# 색상 정의
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}TestPark MariaDB 접속${NC}"
echo -e "${BLUE}========================================${NC}"

echo -e "${YELLOW}데이터베이스 정보:${NC}"
echo "  호스트: localhost:3306"
echo "  데이터베이스: testpark"
echo "  사용자: testpark (또는 root)"
echo "  비밀번호: testpark123 (또는 testpark-root)"
echo ""

echo -e "${GREEN}MariaDB 콘솔로 접속 중...${NC}"
echo -e "${YELLOW}종료하려면 'exit' 또는 Ctrl+D를 입력하세요${NC}"
echo ""

# MariaDB 콘솔 접속
docker exec -it testpark-mariadb mariadb -u root -ptestpark-root testpark