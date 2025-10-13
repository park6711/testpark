#!/bin/bash
# Company Google Sheets 동기화 Cron 스크립트
# 매일 18:00에 실행

# 로그 디렉토리 생성
LOG_DIR="/var/log/testpark"
mkdir -p "$LOG_DIR"

LOG_FILE="$LOG_DIR/company_sync_$(date +\%Y\%m\%d).log"

echo "========================================" >> "$LOG_FILE"
echo "Company 동기화 시작: $(date)" >> "$LOG_FILE"
echo "========================================" >> "$LOG_FILE"

# Docker 컨테이너에서 Django Management Command 실행
docker exec testpark python manage.py sync_companies >> "$LOG_FILE" 2>&1

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ Company 동기화 성공: $(date)" >> "$LOG_FILE"
else
    echo "❌ Company 동기화 실패 (Exit Code: $EXIT_CODE): $(date)" >> "$LOG_FILE"
fi

echo "" >> "$LOG_FILE"

# 30일 이상 된 로그 파일 삭제
find "$LOG_DIR" -name "company_sync_*.log" -type f -mtime +30 -delete

exit $EXIT_CODE
