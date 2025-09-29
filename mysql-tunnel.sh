#!/bin/bash
# 카페24 MySQL SSH 터널링 스크립트

echo "카페24 MySQL SSH 터널링 설정"
echo "================================"
echo "카페24 SSH 계정 정보가 필요합니다."
echo ""

# 카페24 SSH 정보
CAFE24_SSH_HOST="carpenterhosting.cafe24.com"
CAFE24_SSH_USER="carpenterhosting"
LOCAL_PORT=3307  # 로컬 포트
REMOTE_HOST="localhost"  # 카페24 서버 내부에서 MySQL 호스트
REMOTE_PORT=3306  # 카페24 서버 내부 MySQL 포트

echo "SSH 터널링 시작..."
echo "로컬 포트 $LOCAL_PORT -> 카페24 MySQL"
echo ""
echo "연결 명령:"
echo "ssh -L $LOCAL_PORT:$REMOTE_HOST:$REMOTE_PORT $CAFE24_SSH_USER@$CAFE24_SSH_HOST -N"
echo ""
echo "연결 후 .env 파일에서:"
echo "MYSQL_HOST=host.docker.internal  # Docker에서 호스트 PC 접근"
echo "MYSQL_PORT=$LOCAL_PORT"
echo ""

# SSH 터널 실행
ssh -L $LOCAL_PORT:$REMOTE_HOST:$REMOTE_PORT $CAFE24_SSH_USER@$CAFE24_SSH_HOST -N