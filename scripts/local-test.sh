#!/bin/bash

# TestPark 테스트 실행 스크립트
# 사용법: ./scripts/local-test.sh [app_name]

set -e

# 색상 정의
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

APP_NAME=$1

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}   TestPark 테스트 실행${NC}"
echo -e "${BLUE}========================================${NC}"

# 컨테이너 실행 확인
if ! docker ps | grep -q testpark-dev-web; then
    echo -e "${RED}❌ 개발 환경이 실행되고 있지 않습니다.${NC}"
    echo -e "${YELLOW}./scripts/local-start.sh 를 먼저 실행하세요.${NC}"
    exit 1
fi

# 테스트 실행
if [ -z "$APP_NAME" ]; then
    echo -e "${YELLOW}전체 테스트를 실행합니다...${NC}"
    docker-compose -f docker-compose.dev.yml exec web python manage.py test --parallel
else
    echo -e "${YELLOW}$APP_NAME 앱 테스트를 실행합니다...${NC}"
    docker-compose -f docker-compose.dev.yml exec web python manage.py test $APP_NAME --parallel
fi

# 테스트 결과
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ 모든 테스트를 통과했습니다!${NC}"
else
    echo -e "${RED}❌ 일부 테스트가 실패했습니다.${NC}"
    exit 1
fi

# 커버리지 확인 옵션
echo ""
read -p "코드 커버리지를 확인하시겠습니까? (y/n): " CHECK_COVERAGE
if [ "$CHECK_COVERAGE" = "y" ]; then
    echo -e "${BLUE}코드 커버리지 분석 중...${NC}"
    docker-compose -f docker-compose.dev.yml exec web coverage run --source='.' manage.py test
    docker-compose -f docker-compose.dev.yml exec web coverage report
    echo -e "${YELLOW}HTML 리포트를 생성하려면: coverage html${NC}"
fi