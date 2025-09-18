#!/bin/bash

# TestPark 자동 배포 스크립트
# GitHub Actions에서 호출되거나 수동으로 실행 가능

set -e  # 오류 시 스크립트 중단

echo "🚀 TestPark 배포를 시작합니다..."

# 환경 변수 설정
CONTAINER_NAME="testpark"
IMAGE_NAME="7171man/testpark:latest"
PORT="8000"
JANDI_WEBHOOK="https://wh.jandi.com/connect-api/webhook/15016768/83760d2c508acfed35c1944e8a199f9b"

# 배포 시작 알림
echo "📢 배포 시작 알림을 전송합니다..."
curl -X POST "$JANDI_WEBHOOK" \
  -H "Content-Type: application/json" \
  -d "{
    \"body\": \"🚀 TestPark 배포 시작!\\n\\n📋 배포 단계:\\n ⏳ 1. Docker 이미지 풀\\n ⏳ 2. 기존 컨테이너 중지\\n ⏳ 3. 새 컨테이너 시작\\n ⏳ 4. 헬스체크\\n ⏳ 5. 정리 작업\\n\\n🕐 예상 소요 시간: 1-2분\",
    \"connectColor\": \"#FFD700\"
  }" > /dev/null 2>&1

# 1단계: Docker Hub에서 최신 이미지 가져오기
echo "📥 최신 Docker 이미지를 가져옵니다..."
curl -X POST "$JANDI_WEBHOOK" \
  -H "Content-Type: application/json" \
  -d "{
    \"body\": \"📥 1단계: Docker 이미지 다운로드 중...\\n\\n📋 배포 진행상황:\\n ⏳ 1. Docker 이미지 풀\\n ⬜ 2. 기존 컨테이너 중지\\n ⬜ 3. 새 컨테이너 시작\\n ⬜ 4. 헬스체크\\n ⬜ 5. 정리 작업\",
    \"connectColor\": \"#2196F3\"
  }" > /dev/null 2>&1

docker pull $IMAGE_NAME

curl -X POST "$JANDI_WEBHOOK" \
  -H "Content-Type: application/json" \
  -d "{
    \"body\": \"✅ 1단계 완료: Docker 이미지 다운로드\\n이미지: $IMAGE_NAME\\n\\n📋 배포 진행상황:\\n ✅ 1. Docker 이미지 풀\\n ⏳ 2. 기존 컨테이너 중지\\n ⬜ 3. 새 컨테이너 시작\\n ⬜ 4. 헬스체크\\n ⬜ 5. 정리 작업\",
    \"connectColor\": \"#4CAF50\"
  }" > /dev/null 2>&1

# 2단계: 기존 컨테이너 중지 및 제거
echo "🔄 기존 컨테이너를 중지합니다..."
curl -X POST "$JANDI_WEBHOOK" \
  -H "Content-Type: application/json" \
  -d "{
    \"body\": \"🔄 2단계: 기존 컨테이너 중지 중...\\n\\n📋 배포 진행상황:\\n ✅ 1. Docker 이미지 풀\\n ⏳ 2. 기존 컨테이너 중지\\n ⬜ 3. 새 컨테이너 시작\\n ⬜ 4. 헬스체크\\n ⬜ 5. 정리 작업\",
    \"connectColor\": \"#FF9800\"
  }" > /dev/null 2>&1

if [ $(docker ps -q -f name=$CONTAINER_NAME) ]; then
    docker stop $CONTAINER_NAME
    echo "✅ 컨테이너가 중지되었습니다."
fi

if [ $(docker ps -aq -f name=$CONTAINER_NAME) ]; then
    docker rm $CONTAINER_NAME
    echo "✅ 기존 컨테이너가 제거되었습니다."
fi

curl -X POST "$JANDI_WEBHOOK" \
  -H "Content-Type: application/json" \
  -d "{
    \"body\": \"✅ 2단계 완료: 기존 컨테이너 정리\\n\\n📋 배포 진행상황:\\n ✅ 1. Docker 이미지 풀\\n ✅ 2. 기존 컨테이너 중지\\n ⏳ 3. 새 컨테이너 시작\\n ⬜ 4. 헬스체크\\n ⬜ 5. 정리 작업\",
    \"connectColor\": \"#4CAF50\"
  }" > /dev/null 2>&1

# 3단계: 새 컨테이너 실행
echo "🏃 새로운 컨테이너를 시작합니다..."
curl -X POST "$JANDI_WEBHOOK" \
  -H "Content-Type: application/json" \
  -d "{
    \"body\": \"🏃 3단계: 새 컨테이너 시작 중...\\n이미지: $IMAGE_NAME\\n포트: $PORT\\n\\n📋 배포 진행상황:\\n ✅ 1. Docker 이미지 풀\\n ✅ 2. 기존 컨테이너 중지\\n ⏳ 3. 새 컨테이너 시작\\n ⬜ 4. 헬스체크\\n ⬜ 5. 정리 작업\",
    \"connectColor\": \"#9C27B0\"
  }" > /dev/null 2>&1

docker run -d \
    --name $CONTAINER_NAME \
    --restart unless-stopped \
    -p $PORT:8000 \
    $IMAGE_NAME

# 컨테이너 ID 확인
CONTAINER_ID=$(docker ps -q -f name=$CONTAINER_NAME)
echo "✅ 새 컨테이너가 시작되었습니다. ID: $CONTAINER_ID"

curl -X POST "$JANDI_WEBHOOK" \
  -H "Content-Type: application/json" \
  -d "{
    \"body\": \"✅ 3단계 완료: 새 컨테이너 시작\\n컨테이너 ID: $CONTAINER_ID\\n포트: $PORT\\n\\n📋 배포 진행상황:\\n ✅ 1. Docker 이미지 풀\\n ✅ 2. 기존 컨테이너 중지\\n ✅ 3. 새 컨테이너 시작\\n ⏳ 4. 헬스체크\\n ⬜ 5. 정리 작업\",
    \"connectColor\": \"#4CAF50\"
  }" > /dev/null 2>&1

# 4단계: 헬스 체크
echo "🔍 애플리케이션 상태를 확인합니다..."
curl -X POST "$JANDI_WEBHOOK" \
  -H "Content-Type: application/json" \
  -d "{
    \"body\": \"🔍 4단계: 헬스체크 진행 중...\\n대상: http://localhost:$PORT\\n최대 대기시간: 30초\\n\\n📋 배포 진행상황:\\n ✅ 1. Docker 이미지 풀\\n ✅ 2. 기존 컨테이너 중지\\n ✅ 3. 새 컨테이너 시작\\n ⏳ 4. 헬스체크\\n ⬜ 5. 정리 작업\",
    \"connectColor\": \"#00BCD4\"
  }" > /dev/null 2>&1

sleep 5

# 최대 30초 동안 헬스 체크 시도
for i in {1..6}; do
    if curl -f http://localhost:$PORT/ > /dev/null 2>&1; then
        echo "✅ 애플리케이션이 정상적으로 실행되고 있습니다!"
        echo "🌐 접속 주소: http://localhost:$PORT"

        # 헬스체크 성공 알림
        CONTAINER_ID=$(docker ps -q -f name=$CONTAINER_NAME)
        IMAGE_ID=$(docker inspect --format='{{.Image}}' $CONTAINER_NAME | cut -c8-19)

        curl -X POST "$JANDI_WEBHOOK" \
          -H "Content-Type: application/json" \
          -d "{
            \"body\": \"✅ 4단계 완료: 헬스체크 성공!\\n🌐 서비스 URL: http://localhost:$PORT\\n컨테이너 ID: $CONTAINER_ID\\n이미지 ID: $IMAGE_ID\\n\\n📋 배포 진행상황:\\n ✅ 1. Docker 이미지 풀\\n ✅ 2. 기존 컨테이너 중지\\n ✅ 3. 새 컨테이너 시작\\n ✅ 4. 헬스체크\\n ⏳ 5. 정리 작업\",
            \"connectColor\": \"#4CAF50\"
          }" > /dev/null 2>&1

        break
    else
        if [ $i -eq 6 ]; then
            echo "❌ 애플리케이션 시작에 실패했습니다."
            echo "🔍 컨테이너 로그를 확인합니다..."
            CONTAINER_LOGS=$(docker logs $CONTAINER_NAME --tail 10 2>&1)

            curl -X POST "$JANDI_WEBHOOK" \
              -H "Content-Type: application/json" \
              -d "{
                \"body\": \"❌ 4단계 실패: 헬스체크 실패!\\n프로젝트: testpark\\n이미지: $IMAGE_NAME\\n포트: $PORT\\n오류: 애플리케이션 응답 없음\\n\\n🔍 최근 로그 (마지막 10줄):\\n\\\`\\\`\\\`\\n${CONTAINER_LOGS}\\n\\\`\\\`\\\`\\n\\n📋 배포 상태:\\n ✅ 1. Docker 이미지 풀\\n ✅ 2. 기존 컨테이너 중지\\n ✅ 3. 새 컨테이너 시작\\n ❌ 4. 헬스체크\\n ⛔ 5. 정리 작업 (중단)\",
                \"connectColor\": \"#FF4444\"
              }" > /dev/null 2>&1

            exit 1
        fi
        echo "⏳ 애플리케이션 시작을 기다리는 중... ($i/6)"
        curl -X POST "$JANDI_WEBHOOK" \
          -H "Content-Type: application/json" \
          -d "{
            \"body\": \"⏳ 헬스체크 대기 중... ($i/6)\\n대상: http://localhost:$PORT\\n상태: 응답 대기 중\\n다음 시도: 5초 후\",
            \"connectColor\": \"#FFC107\"
          }" > /dev/null 2>&1
        sleep 5
    fi
done

# 5단계: 사용하지 않는 이미지 정리
echo "🧹 사용하지 않는 Docker 이미지를 정리합니다..."
curl -X POST "$JANDI_WEBHOOK" \
  -H "Content-Type: application/json" \
  -d "{
    \"body\": \"🧹 5단계: 정리 작업 진행 중...\\n작업: 사용하지 않는 Docker 이미지 제거\\n\\n📋 배포 진행상황:\\n ✅ 1. Docker 이미지 풀\\n ✅ 2. 기존 컨테이너 중지\\n ✅ 3. 새 컨테이너 시작\\n ✅ 4. 헬스체크\\n ⏳ 5. 정리 작업\",
    \"connectColor\": \"#607D8B\"
  }" > /dev/null 2>&1

# 정리 전 이미지 개수 확인
BEFORE_CLEANUP=$(docker images --format "table {{.Repository}}\t{{.Tag}}" | wc -l)
docker image prune -f
AFTER_CLEANUP=$(docker images --format "table {{.Repository}}\t{{.Tag}}" | wc -l)
CLEANED_IMAGES=$((BEFORE_CLEANUP - AFTER_CLEANUP))

echo "🎉 TestPark 배포가 성공적으로 완료되었습니다!"
echo "📊 컨테이너 상태:"
docker ps -f name=$CONTAINER_NAME --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# 최종 배포 상태 정보 수집
CONTAINER_ID=$(docker ps -q -f name=$CONTAINER_NAME)
IMAGE_ID=$(docker inspect --format='{{.Image}}' $CONTAINER_NAME | cut -c8-19)
CONTAINER_STATUS=$(docker inspect --format='{{.State.Status}}' $CONTAINER_NAME)
START_TIME=$(docker inspect --format='{{.State.StartedAt}}' $CONTAINER_NAME)
CONTAINER_UPTIME=$(docker ps -f name=$CONTAINER_NAME --format "{{.Status}}")

# 최종 배포 완료 알림 (상세 정보 포함)
curl -X POST "$JANDI_WEBHOOK" \
  -H "Content-Type: application/json" \
  -d "{
    \"body\": \"🎉 TestPark 배포 완료!\\n\\n📊 배포 결과 요약:\\n• 프로젝트: testpark\\n• 이미지: $IMAGE_NAME\\n• 컨테이너 ID: $CONTAINER_ID\\n• 이미지 ID: $IMAGE_ID\\n• 상태: $CONTAINER_STATUS\\n• 시작 시간: $START_TIME\\n• 업타임: $CONTAINER_UPTIME\\n• 포트: $PORT\\n• 정리된 이미지: ${CLEANED_IMAGES}개\\n\\n✅ 완료된 배포 단계:\\n ✅ 1. Docker 이미지 풀\\n ✅ 2. 기존 컨테이너 중지\\n ✅ 3. 새 컨테이너 시작\\n ✅ 4. 헬스체크\\n ✅ 5. 정리 작업\\n\\n🌐 서비스: http://localhost:$PORT\\n\\n🎯 배포 작업이 모두 성공적으로 완료되었습니다!\",
    \"connectColor\": \"#4A90E2\"
  }" > /dev/null 2>&1

echo "📢 잔디 알림 전송 완료!"
echo "🌐 서비스 접속: http://localhost:$PORT"