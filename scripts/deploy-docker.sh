#!/bin/bash

# TestPark Docker Compose 배포 스크립트 (최적화된 알림 시스템)
# 웹훅 서버에서 호출되는 배포 스크립트

set -e  # 오류 시 스크립트 중단

echo "🚀 TestPark Docker Compose 배포를 시작합니다..."

# 환경 변수 설정
COMPOSE_PROJECT="testpark"
IMAGE_NAME="7171man/testpark:latest"
JANDI_WEBHOOK="https://wh.jandi.com/connect-api/webhook/15016768/83760d2c508acfed35c1944e8a199f9b"

# 배포 시작 알림 (최적화)
echo "📢 배포 시작 알림을 전송합니다..."
curl -X POST "$JANDI_WEBHOOK" \
  -H "Content-Type: application/json" \
  -d "{
    \"body\": \"🚀 TestPark Docker Compose 배포 시작!\\n이미지: $IMAGE_NAME\\n방식: Docker Compose\\n예상 시간: 1-2분\\n\\n📍 실서버에서 배포 완료 후 확인해주세요!\",
    \"connectColor\": \"#FFD700\"
  }" > /dev/null 2>&1

# 1단계: Docker Hub에서 최신 이미지 가져오기
echo "📥 최신 Docker 이미지를 가져옵니다..."
docker pull $IMAGE_NAME

# 중간 진행 알림 (간소화)
curl -X POST "$JANDI_WEBHOOK" \
  -H "Content-Type: application/json" \
  -d "{
    \"body\": \"⚡ Docker Compose 배포 진행 중...\\n✅ Docker 이미지 업데이트 완료\\n🔄 컨테이너 재시작 진행 중...\\n\\n이미지: $IMAGE_NAME\",
    \"connectColor\": \"#2196F3\"
  }" > /dev/null 2>&1

# 2단계: Docker Compose로 서비스 재시작
echo "🔄 Docker Compose 서비스를 재시작합니다..."
cd /var/www/testpark

# TestPark 서비스만 재시작 (웹훅 서버는 그대로 유지)
docker-compose pull testpark
docker-compose up -d --no-deps testpark

# 3단계: 헬스 체크
echo "🔍 애플리케이션 상태를 확인합니다..."
sleep 5

# 최대 30초 동안 헬스 체크 시도
HEALTH_CHECK_SUCCESS=false
for i in {1..6}; do
    if curl -f http://localhost:8000/ > /dev/null 2>&1; then
        echo "✅ 애플리케이션이 정상적으로 실행되고 있습니다!"
        echo "🌐 접속 주소: https://carpenterhosting.cafe24.com"
        HEALTH_CHECK_SUCCESS=true
        break
    else
        if [ $i -eq 6 ]; then
            echo "❌ 애플리케이션 시작에 실패했습니다."
            echo "🔍 컨테이너 로그를 확인합니다..."
            CONTAINER_LOGS=$(docker-compose logs testpark --tail 10 2>&1)

            curl -X POST "$JANDI_WEBHOOK" \
              -H "Content-Type: application/json" \
              -d "{
                \"body\": \"❌ TestPark Docker Compose 배포 실패!\\n\\n🔍 헬스체크 실패 - 애플리케이션 응답 없음\\n이미지: $IMAGE_NAME\\n\\n📋 최근 로그:\\n\\\`\\\`\\\`\\n${CONTAINER_LOGS}\\n\\\`\\\`\\\`\\n\\n⚠️ 수동 확인이 필요합니다!\",
                \"connectColor\": \"#FF4444\"
              }" > /dev/null 2>&1

            exit 1
        fi
        echo "⏳ 애플리케이션 시작을 기다리는 중... ($i/6)"
        sleep 5
    fi
done

# 4단계: 사용하지 않는 이미지 정리
echo "🧹 사용하지 않는 Docker 이미지를 정리합니다..."
BEFORE_CLEANUP=$(docker images --format "table {{.Repository}}\t{{.Tag}}" | wc -l)
docker image prune -f
AFTER_CLEANUP=$(docker images --format "table {{.Repository}}\t{{.Tag}}" | wc -l)
CLEANED_IMAGES=$((BEFORE_CLEANUP - AFTER_CLEANUP))

echo "🎉 TestPark Docker Compose 배포가 성공적으로 완료되었습니다!"
echo "📊 컨테이너 상태:"
docker-compose ps testpark

# 최종 배포 상태 정보 수집
CONTAINER_ID=$(docker-compose ps -q testpark)
CONTAINER_STATUS=$(docker inspect --format='{{.State.Status}}' $CONTAINER_ID)
CONTAINER_UPTIME=$(docker-compose ps testpark --format "{{.Status}}")

# 최종 배포 완료 알림 (간소화)
curl -X POST "$JANDI_WEBHOOK" \
  -H "Content-Type: application/json" \
  -d "{
    \"body\": \"🎉 TestPark Docker Compose 배포 완료!\\n\\n📊 배포 결과:\\n• 컨테이너 ID: $CONTAINER_ID\\n• 상태: $CONTAINER_STATUS\\n• 업타임: $CONTAINER_UPTIME\\n• 정리된 이미지: ${CLEANED_IMAGES}개\\n• 방식: Docker Compose\\n\\n🌐 서비스: https://carpenterhosting.cafe24.com\\n\\n🔍 **실서버에서 정상 작동 확인 완료해주세요!**\",
    \"connectColor\": \"#4CAF50\"
  }" > /dev/null 2>&1

echo "📢 잔디 알림 전송 완료!"
echo "🌐 서비스 접속: https://carpenterhosting.cafe24.com"