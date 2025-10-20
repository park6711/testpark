#!/bin/bash

# TestPark 복원 스크립트
# 사용법: ./scripts/restore.sh [백업_디렉토리_또는_압축파일]
#
# 이 스크립트는 백업된 데이터를 복원합니다

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 프로젝트 디렉토리
PROJECT_DIR="/var/www/testpark"

# 백업 파일/디렉토리 확인
if [ $# -eq 0 ]; then
    echo -e "${RED}사용법: $0 [백업_디렉토리_또는_압축파일]${NC}"
    echo -e "${YELLOW}예시: $0 ~/backups/testpark_20241017_120000${NC}"
    echo -e "${YELLOW}예시: $0 ~/backups/testpark_backup_20241017_120000.tar.gz${NC}"
    exit 1
fi

BACKUP_SOURCE="$1"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}TestPark 복원 시작${NC}"
echo -e "${GREEN}========================================${NC}"

# 백업 소스 처리
if [ -f "$BACKUP_SOURCE" ]; then
    # 압축 파일인 경우
    echo -e "${YELLOW}백업 압축 파일 해제 중...${NC}"
    TEMP_DIR=$(mktemp -d)
    tar -xzf "$BACKUP_SOURCE" -C "$TEMP_DIR"
    BACKUP_DIR=$(find "$TEMP_DIR" -maxdepth 1 -type d -name "testpark_*" | head -1)

    if [ -z "$BACKUP_DIR" ]; then
        echo -e "${RED}유효한 백업 디렉토리를 찾을 수 없습니다${NC}"
        rm -rf "$TEMP_DIR"
        exit 1
    fi
elif [ -d "$BACKUP_SOURCE" ]; then
    # 디렉토리인 경우
    BACKUP_DIR="$BACKUP_SOURCE"
else
    echo -e "${RED}백업 소스를 찾을 수 없습니다: $BACKUP_SOURCE${NC}"
    exit 1
fi

echo -e "${BLUE}백업 디렉토리: $BACKUP_DIR${NC}"

# 백업 정보 확인
if [ -f "$BACKUP_DIR/backup_info.txt" ]; then
    echo -e "${YELLOW}백업 정보:${NC}"
    echo "----------------------------------------"
    head -10 "$BACKUP_DIR/backup_info.txt"
    echo "----------------------------------------"
fi

# 복원 확인
echo -e "${RED}경고: 이 작업은 현재 데이터를 덮어씁니다!${NC}"
read -p "계속하시겠습니까? (yes/no): " CONFIRM
if [ "$CONFIRM" != "yes" ]; then
    echo -e "${YELLOW}복원이 취소되었습니다${NC}"
    exit 0
fi

# 현재 상태 백업 (안전을 위해)
echo -e "${YELLOW}현재 상태를 임시 백업 중...${NC}"
TEMP_BACKUP="/tmp/testpark_temp_backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$TEMP_BACKUP"

# 현재 .env 파일 백업
if [ -f "$PROJECT_DIR/.env" ]; then
    cp "$PROJECT_DIR/.env" "$TEMP_BACKUP/"
fi

# 1. Docker 컨테이너 중지
echo -e "${YELLOW}Docker 컨테이너 중지 중...${NC}"
cd "$PROJECT_DIR"
docker-compose down || true

# 2. 데이터베이스 복원
if [ -f "$BACKUP_DIR/database/testpark_db.sql" ]; then
    echo -e "${YELLOW}데이터베이스 복원 중...${NC}"

    # MariaDB 컨테이너 시작
    docker-compose up -d mariadb

    # 컨테이너가 준비될 때까지 대기
    echo -e "${YELLOW}MariaDB가 준비될 때까지 대기 중...${NC}"
    sleep 10

    # 데이터베이스 복원
    docker exec -i testpark-mariadb mariadb \
        -u root -ptestpark-root \
        testpark < "$BACKUP_DIR/database/testpark_db.sql"

    echo -e "${GREEN}✓ 데이터베이스 복원 완료${NC}"
elif [ -f "$BACKUP_DIR/database/mariadb_full_backup.sql" ]; then
    echo -e "${YELLOW}전체 데이터베이스 복원 중...${NC}"

    # MariaDB 컨테이너 시작
    docker-compose up -d mariadb

    # 컨테이너가 준비될 때까지 대기
    sleep 10

    # 전체 데이터베이스 복원
    docker exec -i testpark-mariadb mariadb \
        -u root -ptestpark-root < "$BACKUP_DIR/database/mariadb_full_backup.sql"

    echo -e "${GREEN}✓ 전체 데이터베이스 복원 완료${NC}"
else
    echo -e "${YELLOW}데이터베이스 백업을 찾을 수 없습니다${NC}"
fi

# 3. 미디어 파일 복원
if [ -f "$BACKUP_DIR/media/media_files.tar.gz" ]; then
    echo -e "${YELLOW}미디어 파일 복원 중...${NC}"

    # 기존 미디어 디렉토리 백업
    if [ -d "$PROJECT_DIR/media" ]; then
        mv "$PROJECT_DIR/media" "$PROJECT_DIR/media.old"
    fi

    # 미디어 파일 복원
    tar -xzf "$BACKUP_DIR/media/media_files.tar.gz" -C "$PROJECT_DIR"

    # 이전 미디어 디렉토리 삭제
    rm -rf "$PROJECT_DIR/media.old"

    echo -e "${GREEN}✓ 미디어 파일 복원 완료${NC}"
fi

# 4. 정적 파일 복원 (옵션)
if [ -f "$BACKUP_DIR/media/static_files.tar.gz" ]; then
    echo -e "${YELLOW}정적 파일 복원 중...${NC}"

    # 기존 static 디렉토리 백업
    if [ -d "$PROJECT_DIR/static" ]; then
        mv "$PROJECT_DIR/static" "$PROJECT_DIR/static.old"
    fi

    # 정적 파일 복원
    tar -xzf "$BACKUP_DIR/media/static_files.tar.gz" -C "$PROJECT_DIR"

    # 이전 static 디렉토리 삭제
    rm -rf "$PROJECT_DIR/static.old"

    echo -e "${GREEN}✓ 정적 파일 복원 완료${NC}"
fi

# 5. 환경 설정 파일 복원
echo -e "${YELLOW}환경 설정 파일 복원 중...${NC}"
if [ -d "$BACKUP_DIR/config" ]; then
    # .env 파일들 복원 (주의: 기존 파일 백업)
    for env_file in "$BACKUP_DIR/config"/.env*; do
        if [ -f "$env_file" ]; then
            filename=$(basename "$env_file")
            if [ -f "$PROJECT_DIR/$filename" ]; then
                cp "$PROJECT_DIR/$filename" "$PROJECT_DIR/$filename.before_restore"
            fi
            cp "$env_file" "$PROJECT_DIR/"
            echo -e "${GREEN}✓ $filename 복원 완료${NC}"
        fi
    done

    # Google Sheets 인증 파일 복원
    if [ -f "$BACKUP_DIR/config/seongdal-a900e25ac63c.json" ]; then
        cp "$BACKUP_DIR/config/seongdal-a900e25ac63c.json" "$PROJECT_DIR/"
        echo -e "${GREEN}✓ Google Sheets 인증 파일 복원 완료${NC}"
    fi
fi

# 6. Docker 설정 복원 (선택적)
echo -e "${YELLOW}Docker 설정을 복원하시겠습니까? (y/n)${NC}"
read -p "선택: " RESTORE_DOCKER
if [ "$RESTORE_DOCKER" = "y" ]; then
    if [ -d "$BACKUP_DIR/docker" ]; then
        for docker_file in "$BACKUP_DIR/docker"/*; do
            if [ -f "$docker_file" ]; then
                filename=$(basename "$docker_file")
                cp "$docker_file" "$PROJECT_DIR/"
                echo -e "${GREEN}✓ $filename 복원 완료${NC}"
            fi
        done
    fi
fi

# 7. 권한 설정
echo -e "${YELLOW}파일 권한 설정 중...${NC}"
if [ -d "$PROJECT_DIR/media" ]; then
    chmod -R 755 "$PROJECT_DIR/media"
fi
if [ -d "$PROJECT_DIR/static" ]; then
    chmod -R 755 "$PROJECT_DIR/static"
fi

# 8. Docker 컨테이너 재시작
echo -e "${YELLOW}Docker 컨테이너 재시작 중...${NC}"
cd "$PROJECT_DIR"
docker-compose up -d

# 9. 상태 확인
echo -e "${YELLOW}시스템 상태 확인 중...${NC}"
sleep 10

echo -e "${BLUE}Docker 컨테이너 상태:${NC}"
docker-compose ps

# 10. Django 마이그레이션 실행
echo -e "${YELLOW}Django 마이그레이션 실행 중...${NC}"
docker exec testpark python manage.py migrate --no-input || true

# 11. 정적 파일 수집
echo -e "${YELLOW}정적 파일 수집 중...${NC}"
docker exec testpark python manage.py collectstatic --no-input || true

# 정리
if [ -f "$BACKUP_SOURCE" ] && [ -n "$TEMP_DIR" ]; then
    rm -rf "$TEMP_DIR"
fi

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}복원 완료!${NC}"
echo -e "${GREEN}임시 백업 위치: $TEMP_BACKUP${NC}"
echo -e "${GREEN}========================================${NC}"

# 서비스 확인
echo -e "${YELLOW}서비스 상태 확인:${NC}"
curl -s http://localhost:8000/ > /dev/null && \
    echo -e "${GREEN}✓ Django 서비스 정상 작동${NC}" || \
    echo -e "${RED}✗ Django 서비스 응답 없음${NC}"

echo -e "${BLUE}복원 후 확인사항:${NC}"
echo "1. 웹사이트 접속 테스트"
echo "2. 관리자 페이지 로그인 테스트"
echo "3. 미디어 파일 표시 확인"
echo "4. 데이터베이스 연결 확인"

exit 0