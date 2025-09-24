#!/bin/bash
# Google Sheets 자동 동기화를 위한 Cron 설정

echo "📅 TestPark 자동 동기화 Cron 설정"
echo "================================="

# Cron 작업 추가
CRON_JOB="*/5 * * * * docker exec testpark python manage.py auto_sync >> /var/log/testpark_sync.log 2>&1"

# 기존 cron 확인
if crontab -l 2>/dev/null | grep -q "auto_sync"; then
    echo "✅ 이미 동기화 작업이 등록되어 있습니다."
else
    # Cron 작업 추가
    (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
    echo "✅ 5분마다 자동 동기화 작업이 등록되었습니다."
fi

# 로그 파일 생성
touch /var/log/testpark_sync.log
chmod 644 /var/log/testpark_sync.log

echo ""
echo "📝 동기화 로그 확인:"
echo "   tail -f /var/log/testpark_sync.log"
echo ""
echo "📋 Cron 작업 확인:"
echo "   crontab -l"
echo ""
echo "✨ 설정 완료!"