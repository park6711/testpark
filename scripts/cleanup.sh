#!/bin/bash

# TestPark 프로젝트 정리 스크립트
# 불필요한 파일 및 캐시 제거

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}   TestPark 프로젝트 정리${NC}"
echo -e "${BLUE}========================================${NC}"

# Python 캐시 제거
echo -e "${YELLOW}Python 캐시 제거 중...${NC}"
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
find . -type f -name "*.pyo" -delete 2>/dev/null || true
find . -type f -name ".coverage" -delete 2>/dev/null || true
find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
echo -e "${GREEN}✓ Python 캐시 제거 완료${NC}"

# Node.js 캐시 제거 (있는 경우)
if [ -d "node_modules" ]; then
    echo -e "${YELLOW}Node.js 모듈 제거 옵션${NC}"
    read -p "node_modules를 삭제하시겠습니까? (y/n): " DELETE_NODE
    if [ "$DELETE_NODE" = "y" ]; then
        rm -rf node_modules
        echo -e "${GREEN}✓ node_modules 제거 완료${NC}"
    fi
fi

# 임시 파일 제거
echo -e "${YELLOW}임시 파일 제거 중...${NC}"
find . -type f -name "*.tmp" -delete 2>/dev/null || true
find . -type f -name "*.bak" -delete 2>/dev/null || true
find . -type f -name "*.swp" -delete 2>/dev/null || true
find . -type f -name ".DS_Store" -delete 2>/dev/null || true
find . -type f -name "Thumbs.db" -delete 2>/dev/null || true
echo -e "${GREEN}✓ 임시 파일 제거 완료${NC}"

# 로그 파일 정리
if [ -d "logs" ]; then
    echo -e "${YELLOW}로그 파일 정리 중...${NC}"
    find logs -type f -name "*.log" -mtime +30 -delete 2>/dev/null || true
    echo -e "${GREEN}✓ 30일 이상된 로그 제거 완료${NC}"
fi

# SQLite 데이터베이스 정리
if [ -f "db.sqlite3" ]; then
    echo -e "${YELLOW}SQLite 데이터베이스 발견${NC}"
    read -p "db.sqlite3를 삭제하시겠습니까? (y/n): " DELETE_SQLITE
    if [ "$DELETE_SQLITE" = "y" ]; then
        rm -f db.sqlite3
        echo -e "${GREEN}✓ SQLite 데이터베이스 제거 완료${NC}"
    fi
fi

# Docker 정리
echo -e "${BLUE}Docker 정리 옵션${NC}"
read -p "Docker 시스템을 정리하시겠습니까? (y/n): " CLEAN_DOCKER
if [ "$CLEAN_DOCKER" = "y" ]; then
    echo -e "${YELLOW}Docker 정리 중...${NC}"
    docker system prune -f
    echo -e "${GREEN}✓ Docker 시스템 정리 완료${NC}"
fi

# 크기 확인
echo -e "${BLUE}디렉토리 크기 확인:${NC}"
du -sh . 2>/dev/null || echo "크기 확인 불가"
echo ""

# 완료
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✨ 프로젝트 정리 완료!${NC}"
echo -e "${GREEN}========================================${NC}"