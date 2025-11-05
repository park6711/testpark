#!/bin/bash

# 수동 배포 스크립트
# GitHub Actions 대신 로컬에서 직접 실행

echo "🔧 TestPark 수동 배포 시작..."

# 배포 요청자 정보 입력 받기
read -p "👤 배포 요청자 이름을 입력하세요 (기본값: $(whoami)): " DEPLOY_USER
DEPLOY_USER=${DEPLOY_USER:-$(whoami)}

echo ""
echo "📋 배포 정보:"
echo "  - 요청자: $DEPLOY_USER"
echo "  - 시각: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 확인 메시지
read -p "⚠️  수동 배포를 진행하시겠습니까? (y/N): " CONFIRM
if [[ ! "$CONFIRM" =~ ^[Yy]$ ]]; then
    echo "❌ 배포가 취소되었습니다."
    exit 0
fi

echo ""
echo "🌐 서버에 수동 배포 요청..."
curl -X POST "https://carpenterhosting.cafe24.com/deploy" \
  -H "Content-Type: application/json" \
  -d "{
    \"user\": \"$DEPLOY_USER\",
    \"timestamp\": \"$(date '+%Y-%m-%d %H:%M:%S')\"
  }"

echo ""
echo "✅ 수동 배포 요청 완료!"
echo "📊 배포 진행 상황은 잔디(Jandi)에서 확인하세요."
echo "🔍 배포 로그: https://carpenterhosting.cafe24.com/deploy-logs"