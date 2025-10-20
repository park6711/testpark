#!/bin/bash

# TestPark 데이터베이스 동기화 스크립트
# 사용법:
#   ./scripts/sync-database.sh pull  # 프로덕션 → 로컬
#   ./scripts/sync-database.sh push  # 로컬 → 프로덕션 (주의!)
#   ./scripts/sync-database.sh export # 로컬 DB 내보내기만
#   ./scripts/sync-database.sh import [파일] # 덤프 파일 가져오기

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 설정
PROJECT_DIR="/var/www/testpark"
BACKUP_DIR="$PROJECT_DIR/db-sync"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# 프로덕션 서버 정보 (필요시 수정)
PROD_HOST="carpenterhosting.cafe24.com"
PROD_USER="root"
PROD_PATH="/var/www/testpark"
PROD_DB_CONTAINER="testpark-mariadb"

# 로컬 데이터베이스 정보
LOCAL_DB_CONTAINER="testpark-mariadb"
LOCAL_DB_USER="root"
LOCAL_DB_PASS="testpark-root"
LOCAL_DB_NAME="testpark"

# 동기화 디렉토리 생성
mkdir -p "$BACKUP_DIR"

# 함수: 사용법 출력
usage() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}TestPark 데이터베이스 동기화${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
    echo -e "${YELLOW}사용법:${NC}"
    echo -e "  $0 pull              ${GREEN}# 프로덕션 → 로컬 (프로덕션 데이터를 로컬로)${NC}"
    echo -e "  $0 push              ${RED}# 로컬 → 프로덕션 (주의! 프로덕션 데이터 덮어씀)${NC}"
    echo -e "  $0 export            ${GREEN}# 로컬 DB를 파일로 내보내기${NC}"
    echo -e "  $0 import [파일]     ${GREEN}# 덤프 파일을 로컬 DB로 가져오기${NC}"
    echo -e "  $0 status            ${GREEN}# 로컬 DB 상태 확인${NC}"
    echo ""
    echo -e "${YELLOW}예시:${NC}"
    echo -e "  $0 pull"
    echo -e "  $0 import ~/backup/testpark_20241020.sql"
    echo ""
    exit 1
}

# 함수: 로컬 DB 상태 확인
check_status() {
    echo -e "${BLUE}로컬 데이터베이스 상태 확인${NC}"
    echo "----------------------------------------"

    # 컨테이너 상태
    if docker ps --format "table {{.Names}}" | grep -q "$LOCAL_DB_CONTAINER"; then
        echo -e "${GREEN}✓ MariaDB 컨테이너 실행 중${NC}"
    else
        echo -e "${RED}✗ MariaDB 컨테이너가 실행되지 않음${NC}"
        echo -e "${YELLOW}다음 명령으로 시작하세요: docker-compose up -d mariadb${NC}"
        exit 1
    fi

    # 데이터베이스 연결 테스트
    docker exec $LOCAL_DB_CONTAINER mariadb -u$LOCAL_DB_USER -p$LOCAL_DB_PASS -e "SELECT VERSION();" > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ 데이터베이스 연결 가능${NC}"
    else
        echo -e "${RED}✗ 데이터베이스 연결 실패${NC}"
        exit 1
    fi

    # 테이블 수와 레코드 수 확인
    echo ""
    echo -e "${YELLOW}데이터베이스 통계:${NC}"
    docker exec $LOCAL_DB_CONTAINER mariadb -u$LOCAL_DB_USER -p$LOCAL_DB_PASS $LOCAL_DB_NAME -e "
        SELECT 'auth_user' as '테이블', COUNT(*) as '레코드 수' FROM auth_user
        UNION SELECT 'company', COUNT(*) FROM company
        UNION SELECT 'order', COUNT(*) FROM \`order\`
        UNION SELECT 'member', COUNT(*) FROM member
        UNION SELECT 'staff', COUNT(*) FROM staff;
    " 2>/dev/null | column -t

    echo ""
}

# 함수: 로컬 DB 내보내기
export_local() {
    echo -e "${BLUE}로컬 데이터베이스 내보내기${NC}"
    echo "----------------------------------------"

    check_status

    EXPORT_FILE="$BACKUP_DIR/testpark_local_$TIMESTAMP.sql"

    echo -e "${YELLOW}내보내기 중: $EXPORT_FILE${NC}"

    docker exec $LOCAL_DB_CONTAINER mariadb-dump \
        -u$LOCAL_DB_USER -p$LOCAL_DB_PASS \
        --single-transaction \
        --routines \
        --triggers \
        --events \
        --add-drop-database \
        --databases $LOCAL_DB_NAME > "$EXPORT_FILE"

    if [ $? -eq 0 ]; then
        EXPORT_SIZE=$(du -sh "$EXPORT_FILE" | cut -f1)
        echo -e "${GREEN}✓ 내보내기 완료!${NC}"
        echo -e "${GREEN}파일: $EXPORT_FILE${NC}"
        echo -e "${GREEN}크기: $EXPORT_SIZE${NC}"

        # 압축 옵션
        echo ""
        read -p "파일을 압축하시겠습니까? (y/n): " COMPRESS
        if [ "$COMPRESS" = "y" ]; then
            gzip -c "$EXPORT_FILE" > "$EXPORT_FILE.gz"
            COMPRESSED_SIZE=$(du -sh "$EXPORT_FILE.gz" | cut -f1)
            echo -e "${GREEN}✓ 압축 완료: $EXPORT_FILE.gz ($COMPRESSED_SIZE)${NC}"
        fi
    else
        echo -e "${RED}✗ 내보내기 실패${NC}"
        exit 1
    fi
}

# 함수: 덤프 파일 가져오기
import_dump() {
    local DUMP_FILE="$1"

    echo -e "${BLUE}데이터베이스 가져오기${NC}"
    echo "----------------------------------------"

    if [ ! -f "$DUMP_FILE" ]; then
        echo -e "${RED}파일을 찾을 수 없습니다: $DUMP_FILE${NC}"
        exit 1
    fi

    check_status

    # 백업 생성
    echo -e "${YELLOW}현재 데이터베이스 백업 중...${NC}"
    BACKUP_FILE="$BACKUP_DIR/testpark_before_import_$TIMESTAMP.sql"
    docker exec $LOCAL_DB_CONTAINER mariadb-dump \
        -u$LOCAL_DB_USER -p$LOCAL_DB_PASS \
        --single-transaction \
        $LOCAL_DB_NAME > "$BACKUP_FILE"
    echo -e "${GREEN}✓ 백업 완료: $BACKUP_FILE${NC}"

    # 확인
    echo -e "${RED}경고: 현재 로컬 데이터베이스가 덮어씌워집니다!${NC}"
    read -p "계속하시겠습니까? (yes/no): " CONFIRM
    if [ "$CONFIRM" != "yes" ]; then
        echo -e "${YELLOW}가져오기 취소됨${NC}"
        exit 0
    fi

    # 가져오기
    echo -e "${YELLOW}데이터베이스 가져오는 중...${NC}"

    # 압축 파일 처리
    if [[ "$DUMP_FILE" == *.gz ]]; then
        gunzip -c "$DUMP_FILE" | docker exec -i $LOCAL_DB_CONTAINER mariadb \
            -u$LOCAL_DB_USER -p$LOCAL_DB_PASS
    else
        docker exec -i $LOCAL_DB_CONTAINER mariadb \
            -u$LOCAL_DB_USER -p$LOCAL_DB_PASS < "$DUMP_FILE"
    fi

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ 가져오기 완료!${NC}"

        # Django 마이그레이션 실행
        echo -e "${YELLOW}Django 마이그레이션 실행 중...${NC}"
        docker exec testpark python manage.py migrate --no-input

        # 통계 표시
        echo ""
        check_status
    else
        echo -e "${RED}✗ 가져오기 실패${NC}"
        echo -e "${YELLOW}복원하려면: $0 import $BACKUP_FILE${NC}"
        exit 1
    fi
}

# 함수: 프로덕션에서 로컬로 동기화
pull_from_production() {
    echo -e "${BLUE}프로덕션 → 로컬 데이터베이스 동기화${NC}"
    echo "----------------------------------------"

    check_status

    # SSH 연결 테스트
    echo -e "${YELLOW}프로덕션 서버 연결 테스트 중...${NC}"
    ssh -o ConnectTimeout=5 $PROD_USER@$PROD_HOST "echo '연결 성공'" > /dev/null 2>&1
    if [ $? -ne 0 ]; then
        echo -e "${RED}✗ 프로덕션 서버에 연결할 수 없습니다${NC}"
        echo -e "${YELLOW}SSH 설정을 확인하세요: $PROD_USER@$PROD_HOST${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ 프로덕션 서버 연결 성공${NC}"

    # 프로덕션에서 덤프 생성
    REMOTE_DUMP="/tmp/testpark_prod_dump_$TIMESTAMP.sql"
    LOCAL_DUMP="$BACKUP_DIR/testpark_prod_$TIMESTAMP.sql"

    echo -e "${YELLOW}프로덕션 데이터베이스 덤프 생성 중...${NC}"
    ssh $PROD_USER@$PROD_HOST "
        docker exec $PROD_DB_CONTAINER mariadb-dump \
            -uroot -ptestpark-root \
            --single-transaction \
            --routines \
            --triggers \
            --events \
            --add-drop-database \
            --databases testpark > $REMOTE_DUMP && \
        gzip $REMOTE_DUMP
    "

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ 프로덕션 덤프 생성 완료${NC}"
    else
        echo -e "${RED}✗ 프로덕션 덤프 생성 실패${NC}"
        exit 1
    fi

    # 덤프 파일 다운로드
    echo -e "${YELLOW}덤프 파일 다운로드 중...${NC}"
    scp $PROD_USER@$PROD_HOST:$REMOTE_DUMP.gz $LOCAL_DUMP.gz

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ 다운로드 완료${NC}"

        # 원격 임시 파일 삭제
        ssh $PROD_USER@$PROD_HOST "rm -f $REMOTE_DUMP.gz"

        # 로컬로 가져오기
        import_dump "$LOCAL_DUMP.gz"
    else
        echo -e "${RED}✗ 다운로드 실패${NC}"
        exit 1
    fi
}

# 함수: 로컬에서 프로덕션으로 동기화 (위험!)
push_to_production() {
    echo -e "${RED}========================================${NC}"
    echo -e "${RED}경고: 로컬 → 프로덕션 데이터베이스 동기화${NC}"
    echo -e "${RED}프로덕션 데이터가 완전히 덮어씌워집니다!${NC}"
    echo -e "${RED}========================================${NC}"

    echo ""
    echo -e "${YELLOW}정말로 프로덕션 데이터베이스를 덮어쓰시겠습니까?${NC}"
    echo -e "${YELLOW}이 작업은 되돌릴 수 없습니다!${NC}"
    read -p "계속하려면 'PRODUCTION_OVERWRITE'를 입력하세요: " CONFIRM

    if [ "$CONFIRM" != "PRODUCTION_OVERWRITE" ]; then
        echo -e "${GREEN}작업이 취소되었습니다${NC}"
        exit 0
    fi

    check_status

    # 로컬 데이터베이스 내보내기
    export_local

    # 최근 생성된 덤프 파일 찾기
    LATEST_DUMP=$(ls -t $BACKUP_DIR/testpark_local_*.sql 2>/dev/null | head -1)

    if [ -z "$LATEST_DUMP" ]; then
        echo -e "${RED}내보낸 덤프 파일을 찾을 수 없습니다${NC}"
        exit 1
    fi

    # 압축
    gzip -c "$LATEST_DUMP" > "$LATEST_DUMP.gz"

    # 프로덕션으로 업로드
    echo -e "${YELLOW}프로덕션으로 업로드 중...${NC}"
    REMOTE_DUMP="/tmp/testpark_local_upload_$TIMESTAMP.sql.gz"
    scp "$LATEST_DUMP.gz" $PROD_USER@$PROD_HOST:$REMOTE_DUMP

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ 업로드 완료${NC}"

        # 프로덕션에서 가져오기
        echo -e "${YELLOW}프로덕션 데이터베이스 업데이트 중...${NC}"
        ssh $PROD_USER@$PROD_HOST "
            # 백업 생성
            docker exec $PROD_DB_CONTAINER mariadb-dump \
                -uroot -ptestpark-root \
                --single-transaction \
                testpark > /tmp/testpark_prod_backup_$TIMESTAMP.sql

            # 새 데이터 가져오기
            gunzip -c $REMOTE_DUMP | docker exec -i $PROD_DB_CONTAINER mariadb \
                -uroot -ptestpark-root

            # 마이그레이션 실행
            docker exec testpark python manage.py migrate --no-input

            # 임시 파일 삭제
            rm -f $REMOTE_DUMP
        "

        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓ 프로덕션 데이터베이스 업데이트 완료${NC}"
        else
            echo -e "${RED}✗ 프로덕션 업데이트 실패${NC}"
            echo -e "${YELLOW}프로덕션 백업: /tmp/testpark_prod_backup_$TIMESTAMP.sql${NC}"
        fi
    else
        echo -e "${RED}✗ 업로드 실패${NC}"
        exit 1
    fi
}

# 메인 로직
case "${1:-}" in
    pull)
        pull_from_production
        ;;
    push)
        push_to_production
        ;;
    export)
        export_local
        ;;
    import)
        if [ -z "${2:-}" ]; then
            echo -e "${RED}덤프 파일을 지정하세요${NC}"
            echo -e "${YELLOW}사용법: $0 import [파일]${NC}"
            exit 1
        fi
        import_dump "$2"
        ;;
    status)
        check_status
        ;;
    *)
        usage
        ;;
esac

echo ""
echo -e "${GREEN}작업 완료!${NC}"
exit 0