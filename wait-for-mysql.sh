#!/bin/bash
# MySQL이 준비될 때까지 대기하는 스크립트

set -e

host="$1"
shift
cmd="$@"

echo "MySQL 서버 대기 중... (호스트: $host)"

# MySQL이 준비될 때까지 최대 60초 대기
timeout=60
counter=0

until python -c "
import sys
import MySQLdb
try:
    conn = MySQLdb.connect(
        host='${MYSQL_HOST:-mysql}',
        port=int('${MYSQL_PORT:-3306}'),
        user='${MYSQL_USER:-testpark_user}',
        passwd='${MYSQL_PASSWORD:-testpark_pass_2024}',
        db='${MYSQL_DATABASE:-testpark_db}'
    )
    conn.close()
    sys.exit(0)
except Exception as e:
    print(f'연결 실패: {e}')
    sys.exit(1)
" > /dev/null 2>&1; do
    counter=$((counter+1))
    if [ $counter -gt $timeout ]; then
        echo "❌ MySQL 연결 시간 초과 (${timeout}초)"
        exit 1
    fi
    echo "⏳ MySQL 대기 중... ($counter/$timeout)"
    sleep 1
done

echo "✅ MySQL이 준비되었습니다!"
exec $cmd