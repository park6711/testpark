#!/bin/bash

# TestPark 백업 스크립트
# 사용법: ./scripts/backup.sh
#
# 이 스크립트는 다음을 백업합니다:
# - MariaDB 데이터베이스 전체
# - 미디어 파일들
# - 환경 설정 파일들
# - Docker 관련 설정들

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 백업 디렉토리 설정
BACKUP_DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_ROOT="$HOME/backups"
BACKUP_DIR="$BACKUP_ROOT/testpark_$BACKUP_DATE"

# 프로젝트 디렉토리
PROJECT_DIR="/var/www/testpark"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}TestPark 백업 시작${NC}"
echo -e "${GREEN}백업 날짜: $BACKUP_DATE${NC}"
echo -e "${GREEN}========================================${NC}"

# 백업 디렉토리 생성
echo -e "${YELLOW}백업 디렉토리 생성 중...${NC}"
mkdir -p "$BACKUP_DIR"
mkdir -p "$BACKUP_DIR/database"
mkdir -p "$BACKUP_DIR/media"
mkdir -p "$BACKUP_DIR/config"
mkdir -p "$BACKUP_DIR/docker"

# 1. 데이터베이스 백업
echo -e "${YELLOW}데이터베이스 백업 중...${NC}"
if docker ps --format "table {{.Names}}" | grep -q "testpark-mariadb"; then
    docker exec testpark-mariadb mariadb-dump \
        -u root -ptestpark-root \
        --all-databases \
        --single-transaction \
        --routines \
        --triggers \
        --events \
        > "$BACKUP_DIR/database/mariadb_full_backup.sql"

    # 개별 데이터베이스 백업
    docker exec testpark-mariadb mariadb-dump \
        -u root -ptestpark-root \
        testpark \
        --single-transaction \
        > "$BACKUP_DIR/database/testpark_db.sql"

    echo -e "${GREEN}✓ 데이터베이스 백업 완료${NC}"
else
    echo -e "${RED}경고: MariaDB 컨테이너가 실행 중이지 않습니다${NC}"
fi

# 2. 미디어 파일 백업
echo -e "${YELLOW}미디어 파일 백업 중...${NC}"
if [ -d "$PROJECT_DIR/media" ]; then
    tar -czf "$BACKUP_DIR/media/media_files.tar.gz" \
        -C "$PROJECT_DIR" \
        media/
    echo -e "${GREEN}✓ 미디어 파일 백업 완료${NC}"
else
    echo -e "${YELLOW}미디어 디렉토리가 없습니다${NC}"
fi

# 3. 정적 파일 백업 (옵션)
if [ -d "$PROJECT_DIR/static" ]; then
    echo -e "${YELLOW}정적 파일 백업 중...${NC}"
    tar -czf "$BACKUP_DIR/media/static_files.tar.gz" \
        -C "$PROJECT_DIR" \
        static/
    echo -e "${GREEN}✓ 정적 파일 백업 완료${NC}"
fi

# 4. 환경 설정 파일 백업
echo -e "${YELLOW}환경 설정 파일 백업 중...${NC}"
cd "$PROJECT_DIR"

# 환경 변수 파일들
for env_file in .env .env.production .env.local .env.development; do
    if [ -f "$env_file" ]; then
        cp "$env_file" "$BACKUP_DIR/config/"
        echo -e "${GREEN}✓ $env_file 백업 완료${NC}"
    fi
done

# Google Sheets 인증 파일
if [ -f "seongdal-a900e25ac63c.json" ]; then
    cp "seongdal-a900e25ac63c.json" "$BACKUP_DIR/config/"
    echo -e "${GREEN}✓ Google Sheets 인증 파일 백업 완료${NC}"
fi

# 5. Docker 설정 백업
echo -e "${YELLOW}Docker 설정 백업 중...${NC}"
for docker_file in docker-compose*.yml Dockerfile*; do
    if [ -f "$docker_file" ]; then
        cp "$docker_file" "$BACKUP_DIR/docker/"
        echo -e "${GREEN}✓ $docker_file 백업 완료${NC}"
    fi
done

# nginx 설정이 있다면 백업
if [ -f "nginx.conf" ]; then
    cp "nginx.conf" "$BACKUP_DIR/docker/"
fi

# 6. Apache 가상호스트 설정 백업
echo -e "${YELLOW}Apache 설정 백업 중...${NC}"
mkdir -p "$BACKUP_DIR/apache"
if [ -d "/etc/apache2/sites-available" ]; then
    for conf in carpenterhosting-integrated.conf testsite.conf; do
        if [ -f "/etc/apache2/sites-available/$conf" ]; then
            sudo cp "/etc/apache2/sites-available/$conf" "$BACKUP_DIR/apache/"
            echo -e "${GREEN}✓ $conf 백업 완료${NC}"
        fi
    done
fi

# 7. 백업 정보 파일 생성
echo -e "${YELLOW}백업 정보 생성 중...${NC}"
cat > "$BACKUP_DIR/backup_info.txt" << EOF
TestPark 백업 정보
==================
백업 날짜: $BACKUP_DATE
백업 호스트: $(hostname)
백업 사용자: $(whoami)
프로젝트 경로: $PROJECT_DIR

Docker 컨테이너 상태:
$(docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}")

디스크 사용량:
$(df -h "$PROJECT_DIR" | tail -1)

백업 내용:
- 데이터베이스: MariaDB 전체 + testpark DB
- 미디어 파일: $(du -sh "$PROJECT_DIR/media" 2>/dev/null | cut -f1 || echo "N/A")
- 정적 파일: $(du -sh "$PROJECT_DIR/static" 2>/dev/null | cut -f1 || echo "N/A")
- 환경 설정: .env 파일들
- Docker 설정: docker-compose.yml, Dockerfile
- Apache 설정: 가상호스트 설정 파일들

복원 명령:
./scripts/restore.sh $BACKUP_DIR
EOF

# 8. 전체 백업 압축
echo -e "${YELLOW}전체 백업 압축 중...${NC}"
cd "$BACKUP_ROOT"
tar -czf "testpark_backup_$BACKUP_DATE.tar.gz" "testpark_$BACKUP_DATE"

# 9. 백업 크기 확인
BACKUP_SIZE=$(du -sh "$BACKUP_ROOT/testpark_backup_$BACKUP_DATE.tar.gz" | cut -f1)

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}백업 완료!${NC}"
echo -e "${GREEN}백업 위치: $BACKUP_DIR${NC}"
echo -e "${GREEN}압축 파일: $BACKUP_ROOT/testpark_backup_$BACKUP_DATE.tar.gz${NC}"
echo -e "${GREEN}백업 크기: $BACKUP_SIZE${NC}"
echo -e "${GREEN}========================================${NC}"

# 10. 오래된 백업 삭제 (30일 이상)
echo -e "${YELLOW}30일 이상 된 백업 삭제 중...${NC}"
find "$BACKUP_ROOT" -name "testpark_backup_*.tar.gz" -mtime +30 -delete
echo -e "${GREEN}✓ 오래된 백업 정리 완료${NC}"

# 백업 목록 표시
echo -e "${YELLOW}현재 백업 목록:${NC}"
ls -lh "$BACKUP_ROOT"/testpark_backup_*.tar.gz 2>/dev/null || echo "백업 파일이 없습니다"

exit 0