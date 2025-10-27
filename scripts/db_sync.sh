#!/bin/bash

# ===============================================
# PMIS 2.0 Database 동기화 스크립트
# ===============================================
# 용도: 로컬과 프로덕션 DB 간 데이터 동기화
# 작성일: 2025-10-20
# ===============================================

set -e  # 에러 발생시 즉시 중단

# 색상 코드 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 설정 변수
LOCAL_CONTAINER="testpark-mariadb"
LOCAL_DB="testpark"
LOCAL_USER="testpark"
LOCAL_PASSWORD="**jeje4211"

# 프로덕션 설정 (실제 값으로 변경 필요)
PROD_HOST="210.114.22.100"
PROD_CONTAINER="testpark-mariadb"
PROD_DB="testpark"
PROD_USER="testpark"
PROD_PASSWORD="실제_프로덕션_패스워드"

# 백업 디렉토리
BACKUP_DIR="./backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# 함수 정의
print_header() {
    echo -e "${BLUE}================================================${NC}"
    echo -e "${BLUE}  PMIS 2.0 Database Synchronization Tool${NC}"
    echo -e "${BLUE}================================================${NC}"
    echo ""
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# 백업 디렉토리 생성
create_backup_dir() {
    if [ ! -d "$BACKUP_DIR" ]; then
        mkdir -p "$BACKUP_DIR"
        print_success "백업 디렉토리 생성됨: $BACKUP_DIR"
    fi
}

# 로컬 DB 백업
backup_local() {
    echo -e "${BLUE}[1/5] 로컬 데이터베이스 백업 중...${NC}"

    local backup_file="$BACKUP_DIR/local_backup_${TIMESTAMP}.sql"

    docker exec "$LOCAL_CONTAINER" mariadb-dump \
        -u "$LOCAL_USER" \
        -p"$LOCAL_PASSWORD" \
        "$LOCAL_DB" > "$backup_file"

    if [ $? -eq 0 ]; then
        print_success "로컬 DB 백업 완료: $backup_file"
        echo "  파일 크기: $(du -h $backup_file | cut -f1)"
    else
        print_error "로컬 DB 백업 실패"
        exit 1
    fi
}

# 프로덕션 DB 백업 (SSH 통해)
backup_production() {
    echo -e "${BLUE}[2/5] 프로덕션 데이터베이스 백업 중...${NC}"

    local backup_file="$BACKUP_DIR/prod_backup_${TIMESTAMP}.sql"

    # SSH를 통한 원격 백업
    ssh "root@$PROD_HOST" "docker exec $PROD_CONTAINER mariadb-dump -u $PROD_USER -p'$PROD_PASSWORD' $PROD_DB" > "$backup_file"

    if [ $? -eq 0 ]; then
        print_success "프로덕션 DB 백업 완료: $backup_file"
        echo "  파일 크기: $(du -h $backup_file | cut -f1)"
    else
        print_error "프로덕션 DB 백업 실패"
        print_warning "SSH 연결 또는 권한 문제일 수 있습니다"
        exit 1
    fi
}

# 데이터 정제 (민감한 정보 제거)
sanitize_data() {
    echo -e "${BLUE}[3/5] 데이터 정제 중...${NC}"

    local input_file="$1"
    local output_file="$BACKUP_DIR/sanitized_${TIMESTAMP}.sql"

    cp "$input_file" "$output_file"

    # 민감한 데이터 마스킹 (예시)
    # 실제 환경에 맞게 수정 필요
    sed -i '' "s/[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/****@****.com/g" "$output_file"

    print_success "데이터 정제 완료: $output_file"
    echo "$output_file"
}

# 로컬 DB에 데이터 임포트
import_to_local() {
    echo -e "${BLUE}[4/5] 로컬 데이터베이스에 임포트 중...${NC}"

    local import_file="$1"

    # 기존 데이터 삭제 경고
    print_warning "기존 로컬 DB 데이터가 모두 삭제됩니다!"
    read -p "계속하시겠습니까? (y/N): " confirm

    if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
        print_warning "임포트 취소됨"
        return
    fi

    # 데이터 임포트
    docker exec -i "$LOCAL_CONTAINER" mariadb \
        -u "$LOCAL_USER" \
        -p"$LOCAL_PASSWORD" \
        "$LOCAL_DB" < "$import_file"

    if [ $? -eq 0 ]; then
        print_success "데이터 임포트 완료"
    else
        print_error "데이터 임포트 실패"
        exit 1
    fi
}

# 데이터 검증
verify_sync() {
    echo -e "${BLUE}[5/5] 동기화 검증 중...${NC}"

    # 테이블 수 확인
    local table_count=$(docker exec "$LOCAL_CONTAINER" mariadb \
        -u "$LOCAL_USER" \
        -p"$LOCAL_PASSWORD" \
        -e "USE $LOCAL_DB; SHOW TABLES;" | wc -l)

    echo "  총 테이블 수: $((table_count - 1))"

    # 주요 테이블 레코드 수 확인
    for table in member company staff order; do
        local count=$(docker exec "$LOCAL_CONTAINER" mariadb \
            -u "$LOCAL_USER" \
            -p"$LOCAL_PASSWORD" \
            -e "USE $LOCAL_DB; SELECT COUNT(*) FROM $table;" 2>/dev/null | tail -1)
        echo "  - $table 테이블: ${count:-0} 레코드"
    done

    print_success "동기화 검증 완료"
}

# 메인 메뉴
show_menu() {
    print_header
    echo "작업을 선택하세요:"
    echo ""
    echo "  1) 프로덕션 → 로컬 동기화 (전체 데이터)"
    echo "  2) 프로덕션 → 로컬 동기화 (정제된 데이터)"
    echo "  3) 로컬 DB 백업만"
    echo "  4) 프로덕션 DB 백업만"
    echo "  5) 백업 파일 목록 보기"
    echo "  6) 수동 임포트 (백업 파일 선택)"
    echo "  0) 종료"
    echo ""
    read -p "선택 [0-6]: " choice

    case $choice in
        1)
            create_backup_dir
            backup_local
            backup_production
            import_to_local "$BACKUP_DIR/prod_backup_${TIMESTAMP}.sql"
            verify_sync
            ;;
        2)
            create_backup_dir
            backup_local
            backup_production
            sanitized_file=$(sanitize_data "$BACKUP_DIR/prod_backup_${TIMESTAMP}.sql")
            import_to_local "$sanitized_file"
            verify_sync
            ;;
        3)
            create_backup_dir
            backup_local
            ;;
        4)
            create_backup_dir
            backup_production
            ;;
        5)
            echo -e "${BLUE}백업 파일 목록:${NC}"
            ls -lh "$BACKUP_DIR"/*.sql 2>/dev/null || echo "백업 파일이 없습니다"
            ;;
        6)
            echo -e "${BLUE}백업 파일 선택:${NC}"
            select file in "$BACKUP_DIR"/*.sql; do
                if [ -n "$file" ]; then
                    import_to_local "$file"
                    verify_sync
                    break
                fi
            done
            ;;
        0)
            echo "종료합니다."
            exit 0
            ;;
        *)
            print_error "잘못된 선택입니다"
            ;;
    esac
}

# 스크립트 실행
if [ "$1" == "--help" ] || [ "$1" == "-h" ]; then
    print_header
    echo "사용법: ./db_sync.sh [옵션]"
    echo ""
    echo "옵션:"
    echo "  --backup-local    로컬 DB만 백업"
    echo "  --backup-prod     프로덕션 DB만 백업"
    echo "  --sync            프로덕션 → 로컬 전체 동기화"
    echo "  --sync-sanitized  프로덕션 → 로컬 정제 동기화"
    echo "  -h, --help        도움말 표시"
    echo ""
    echo "옵션 없이 실행하면 대화형 메뉴가 표시됩니다."
    exit 0
fi

# 명령줄 옵션 처리
case "$1" in
    --backup-local)
        create_backup_dir
        backup_local
        ;;
    --backup-prod)
        create_backup_dir
        backup_production
        ;;
    --sync)
        create_backup_dir
        backup_local
        backup_production
        import_to_local "$BACKUP_DIR/prod_backup_${TIMESTAMP}.sql"
        verify_sync
        ;;
    --sync-sanitized)
        create_backup_dir
        backup_local
        backup_production
        sanitized_file=$(sanitize_data "$BACKUP_DIR/prod_backup_${TIMESTAMP}.sql")
        import_to_local "$sanitized_file"
        verify_sync
        ;;
    *)
        show_menu
        ;;
esac

echo ""
print_success "작업 완료!"