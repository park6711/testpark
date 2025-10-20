#!/bin/bash

# TestPark 로컬 개발 환경 중지 스크립트
# 사용법: ./scripts/local-stop.sh

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}로컬 개발 환경을 중지합니다...${NC}"

# 컨테이너 중지
docker-compose -f docker-compose.dev.yml down

echo -e "${GREEN}✅ 로컬 개발 환경이 중지되었습니다.${NC}"

# 볼륨 삭제 옵션
read -p "데이터베이스 볼륨도 삭제하시겠습니까? (y/n): " DELETE_VOLUMES
if [ "$DELETE_VOLUMES" = "y" ]; then
    docker-compose -f docker-compose.dev.yml down -v
    echo -e "${YELLOW}⚠️  데이터베이스 볼륨이 삭제되었습니다.${NC}"
fi