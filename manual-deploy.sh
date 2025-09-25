#!/bin/bash

# 수동 배포 스크립트
# GitHub Actions 대신 로컬에서 직접 실행

echo "🔧 TestPark 수동 배포 시작..."

# 1. 기존 이미지 사용 (이미 빌드되어 있는 경우)
echo "📦 기존 이미지 확인..."
docker images | grep testpark

# 2. 기존 이미지에 태그 추가
echo "🏷️ 태그 추가..."
docker tag 7171man/testpark:latest 7171man/testpark:manual-$(date +%Y%m%d-%H%M%S)

# 3. Docker Hub에 푸시 (인증이 되어있다면)
echo "📤 Docker Hub에 푸시 시도..."
docker push 7171man/testpark:manual-$(date +%Y%m%d-%H%M%S) || {
    echo "❌ Docker Hub 푸시 실패"
    echo "💡 대안: 서버에서 직접 빌드"
}

# 4. 서버에 배포 트리거
echo "🌐 서버에 배포 요청..."
curl -X POST "https://carpenterhosting.cafe24.com/deploy-from-github" \
  -H "Content-Type: application/json" \
  -d '{
    "project": "testpark",
    "image": "7171man/testpark:latest",
    "trigger": "manual_deploy"
  }'

echo "✅ 수동 배포 요청 완료!"