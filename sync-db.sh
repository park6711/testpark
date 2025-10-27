#!/bin/bash

# ================================================
# PMIS 2.0 Quick DB Sync
# ================================================
# 빠른 DB 동기화를 위한 간편 스크립트

set -e

# 색상 코드
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}   PMIS 2.0 Database Quick Sync${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""

# 작업 선택
echo "동기화 방법을 선택하세요:"
echo ""
echo "  1) 테스트 데이터로 초기화 (개발용)"
echo "  2) 프로덕션 백업 파일 임포트"
echo "  3) 현재 DB 상태 확인"
echo "  4) DB 컨테이너 재시작"
echo "  5) phpMyAdmin 실행 (웹 UI)"
echo ""
read -p "선택 [1-5]: " choice

case $choice in
    1)
        echo -e "${YELLOW}⚠️  경고: 기존 데이터가 모두 삭제됩니다!${NC}"
        read -p "계속하시겠습니까? (y/N): " confirm
        if [ "$confirm" == "y" ] || [ "$confirm" == "Y" ]; then
            echo -e "${BLUE}테스트 데이터 로드 중...${NC}"

            # DB 초기화
            docker exec testpark-mariadb mariadb -u root -pdev-root-password -e "DROP DATABASE IF EXISTS testpark; CREATE DATABASE testpark;"

            # 스키마 생성 (Django 마이그레이션)
            docker exec testpark python manage.py migrate --no-input

            # 테스트 데이터 임포트
            docker exec -i testpark-mariadb mariadb -u testpark -p'**jeje4211' testpark < scripts/test-data.sql

            echo -e "${GREEN}✓ 테스트 데이터 로드 완료!${NC}"

            # 데이터 확인
            echo -e "${BLUE}데이터 확인:${NC}"
            docker exec testpark-mariadb mariadb -u testpark -p'**jeje4211' -e "USE testpark; SELECT 'Company' as 'Table', COUNT(*) as 'Count' FROM company UNION SELECT 'Member', COUNT(*) FROM member UNION SELECT 'Order', COUNT(*) FROM \`order\`;"
        fi
        ;;

    2)
        echo -e "${BLUE}사용 가능한 백업 파일:${NC}"
        ls -lh backups/*.sql 2>/dev/null || echo "백업 파일이 없습니다"
        echo ""
        read -p "백업 파일 경로 입력: " backup_file

        if [ -f "$backup_file" ]; then
            echo -e "${YELLOW}⚠️  경고: 기존 데이터가 모두 삭제됩니다!${NC}"
            read -p "계속하시겠습니까? (y/N): " confirm

            if [ "$confirm" == "y" ] || [ "$confirm" == "Y" ]; then
                echo -e "${BLUE}백업 파일 임포트 중...${NC}"
                docker exec -i testpark-mariadb mariadb -u testpark -p'**jeje4211' testpark < "$backup_file"
                echo -e "${GREEN}✓ 백업 파일 임포트 완료!${NC}"
            fi
        else
            echo -e "${RED}✗ 파일을 찾을 수 없습니다: $backup_file${NC}"
        fi
        ;;

    3)
        echo -e "${BLUE}현재 DB 상태:${NC}"
        echo ""

        # 컨테이너 상태
        echo "컨테이너 상태:"
        docker ps | grep mariadb || echo "MariaDB 컨테이너가 실행 중이 아닙니다"
        echo ""

        # DB 연결 테스트
        echo "DB 연결 테스트:"
        docker exec testpark-mariadb mariadb -u testpark -p'**jeje4211' -e "SELECT 'Connection OK' as Status;" 2>/dev/null || echo "연결 실패"
        echo ""

        # 테이블 및 레코드 수
        echo "주요 테이블 상태:"
        docker exec testpark-mariadb mariadb -u testpark -p'**jeje4211' -e "
            USE testpark;
            SELECT
                TABLE_NAME as 'Table',
                TABLE_ROWS as 'Rows'
            FROM information_schema.TABLES
            WHERE TABLE_SCHEMA='testpark'
            AND TABLE_NAME IN ('member', 'company', 'staff', 'order', 'assign')
            ORDER BY TABLE_ROWS DESC;" 2>/dev/null || echo "테이블 정보를 가져올 수 없습니다"
        ;;

    4)
        echo -e "${BLUE}DB 컨테이너 재시작 중...${NC}"
        docker-compose restart mariadb
        echo -e "${GREEN}✓ MariaDB 컨테이너 재시작 완료!${NC}"

        # 헬스체크 대기
        echo -e "${BLUE}DB가 준비될 때까지 대기 중...${NC}"
        sleep 5

        # 연결 테스트
        docker exec testpark-mariadb mariadb -u testpark -p'**jeje4211' -e "SELECT 'DB Ready' as Status;" 2>/dev/null && \
            echo -e "${GREEN}✓ DB가 준비되었습니다!${NC}" || \
            echo -e "${RED}✗ DB 연결 실패${NC}"
        ;;

    5)
        echo -e "${BLUE}phpMyAdmin 실행 중...${NC}"

        # phpMyAdmin 컨테이너 확인
        if docker ps | grep -q phpmyadmin; then
            echo -e "${GREEN}✓ phpMyAdmin이 이미 실행 중입니다${NC}"
        else
            echo "phpMyAdmin 시작 중..."
            docker-compose --profile dev-tools up -d phpmyadmin
        fi

        echo ""
        echo -e "${GREEN}phpMyAdmin 접속 정보:${NC}"
        echo "  URL: http://localhost:8080"
        echo "  사용자: testpark"
        echo "  비밀번호: **jeje4211"
        echo ""
        echo -e "${YELLOW}브라우저에서 http://localhost:8080 을 열어주세요${NC}"

        # macOS인 경우 자동으로 브라우저 열기
        if [[ "$OSTYPE" == "darwin"* ]]; then
            open http://localhost:8080
        fi
        ;;

    *)
        echo -e "${RED}잘못된 선택입니다${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}작업 완료!${NC}"