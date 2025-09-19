#!/bin/bash

# TestPark Docker Compose 배포 스크립트 (최적화된 알림 시스템)
# 웹훅 서버에서 호출되는 배포 스크립트

set -e  # 오류 시 스크립트 중단

# 에러 발생 시 잔디 알림 발송하는 트랩 함수
send_error_notification() {
    local exit_code=$?
    local line_number=$1
    local command="$2"

    echo "❌ 배포 중 오류 발생! (Line: $line_number, Exit Code: $exit_code)"

    # 에러 상세 정보 수집
    local error_details="라인 $line_number에서 오류 발생\\n명령어: $command\\n종료 코드: $exit_code"

    # 컨테이너 상태 확인
    local container_status=""
    if docker-compose ps testpark &>/dev/null; then
        container_status="\\n\\n📊 현재 컨테이너 상태:\\n$(docker-compose ps testpark 2>&1 || echo '컨테이너 상태 확인 불가')"
    fi

    # 최근 로그 확인
    local recent_logs=""
    if docker-compose logs testpark --tail 5 &>/dev/null; then
        recent_logs="\\n\\n📋 최근 로그:\\n\\\`\\\`\\\`\\n$(docker-compose logs testpark --tail 5 2>&1 || echo '로그 확인 불가')\\n\\\`\\\`\\\`"
    fi

    curl -X POST "$JANDI_WEBHOOK" \
      -H "Content-Type: application/json" \
      -d "{
        \"body\": \"❌ TestPark Docker Compose 배포 실패!\\n\\n🔍 오류 정보:\\n$error_details$container_status$recent_logs\\n\\n⚠️ 수동 확인이 필요합니다!\",
        \"connectColor\": \"#FF4444\"
      }" > /dev/null 2>&1

    echo "📢 에러 알림 전송 완료!"
    exit $exit_code
}

# 에러 발생 시 트랩 설정
trap 'send_error_notification $LINENO "$BASH_COMMAND"' ERR

echo "🚀 TestPark Docker Compose 배포를 시작합니다..."

# 환경 변수 설정
COMPOSE_PROJECT="testpark"
IMAGE_NAME="7171man/testpark:latest"
JANDI_WEBHOOK="https://wh.jandi.com/connect-api/webhook/15016768/2ee8d5e97543e5fe885aba1f419a9265"

# 배포 시작 알림 (최적화)
echo "📢 배포 시작 알림을 전송합니다..."
curl -X POST "$JANDI_WEBHOOK" \
  -H "Content-Type: application/json" \
  -d "{
    \"body\": \"🚀 TestPark Docker Compose 배포 시작!\\n이미지: $IMAGE_NAME\\n방식: Docker Compose\\n예상 시간: 1-2분\\n\\n📍 실서버에서 배포 완료 후 확인해주세요!\",
    \"connectColor\": \"#FFD700\"
  }" > /dev/null 2>&1

# 1단계: 실서버용 .env 파일 생성 및 검증
echo "⚙️ 실서버용 환경변수 파일을 생성합니다..."
cd /var/www/testpark

# 기존 .env 파일이 있다면 백업
if [ -f .env ]; then
    echo "📋 기존 .env 파일 백업 중..."
    cp .env .env.backup
fi

# 실서버용 .env 파일 생성
echo "📝 새로운 .env 파일 생성 중..."
cat > .env << 'EOF'
# Django 실서버 환경 설정
DEBUG=False
SECRET_KEY="django-insecure-nlk5agkjp1+7+sp168_46gy#h0gdmh%#5ano(r196@c+p7m-ny"

# 네이버 소셜 로그인 설정 (실서버용)
NAVER_CLIENT_ID=_mw6kojqJVXoWEBqYBKv
NAVER_CLIENT_SECRET=hHKrIfKoMA
NAVER_REDIRECT_URI=https://carpenterhosting.cafe24.com/auth/naver/callback/

# CSRF 설정 (실서버용)
CSRF_TRUSTED_ORIGINS=https://carpenterhosting.cafe24.com,http://210.114.22.100:8000,http://localhost:8000,http://127.0.0.1:8000

# 잔디 웹훅 설정
JANDI_WEBHOOK_URL=https://wh.jandi.com/connect-api/webhook/15016768/2ee8d5e97543e5fe885aba1f419a9265

# Docker Hub 자격증명 (배포용)
DOCKER_USERNAME=7171man
DOCKER_PASSWORD=*jeje4211
EOF

# .env 파일 생성 검증
if [ -f .env ]; then
    echo "✅ .env 파일 생성 완료"
    echo "📊 .env 파일 정보:"
    ls -la .env
    echo "📝 .env 파일 내용 미리보기:"
    echo "--- .env 파일 ---"
    head -10 .env
    echo "--- 끝 ---"

    # 파일 권한 설정 (Docker가 읽을 수 있도록)
    chmod 644 .env
    echo "🔒 파일 권한 설정 완료 (644)"
else
    echo "❌ .env 파일 생성 실패!"
    exit 1
fi

# 2단계: Docker Hub 로그인 및 최신 이미지 가져오기
echo "🔐 Docker Hub 로그인 중..."

# .env 파일에서 Docker Hub 자격증명 로드
if [ -f .env ]; then
    source .env
fi

# Docker Hub 로그인 (환경변수에서 자격증명 가져오기, fallback to direct login)
if [ -n "$DOCKER_USERNAME" ] && [ -n "$DOCKER_PASSWORD" ] && [ "$DOCKER_PASSWORD" != "YOUR_DOCKER_HUB_TOKEN_HERE" ]; then
    echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin
    echo "✅ Docker Hub 로그인 완료 (.env 파일 사용)"
else
    echo "🔐 Direct Docker Hub 로그인 시도..."
    echo "*jeje4211" | docker login -u "7171man" --password-stdin
    echo "✅ Docker Hub 로그인 완료 (직접 로그인)"
fi

echo "📥 최신 Docker 이미지를 가져옵니다..."
if docker pull $IMAGE_NAME; then
    echo "✅ Docker 이미지 업데이트 완료!"

    # Docker pull 성공 알림
    curl -X POST "$JANDI_WEBHOOK" \
      -H "Content-Type: application/json" \
      -d "{
        \"body\": \"⚡ Docker Compose 배포 진행 중...\\n✅ .env 파일 생성 완료\\n✅ Docker 이미지 업데이트 완료\\n🔄 컨테이너 재시작 진행 중...\\n\\n이미지: $IMAGE_NAME\",
        \"connectColor\": \"#2196F3\"
      }" > /dev/null 2>&1
else
    echo "❌ Docker 이미지 가져오기 실패!"
    exit 1
fi

# 3단계: Docker Compose로 서비스 재시작
echo "🔄 Docker Compose 서비스를 재시작합니다..."

# TestPark 서비스만 재시작 (웹훅 서버는 그대로 유지)
if docker-compose pull testpark && docker-compose up -d --no-deps testpark; then
    echo "✅ 컨테이너 재시작 완료!"

    # 컨테이너 재시작 성공 알림
    curl -X POST "$JANDI_WEBHOOK" \
      -H "Content-Type: application/json" \
      -d "{
        \"body\": \"⚡ Docker Compose 배포 진행 중...\\n✅ .env 파일 생성 완료\\n✅ 컨테이너 재시작 완료\\n🔍 헬스체크 진행 중...\\n\\n이미지: $IMAGE_NAME\",
        \"connectColor\": \"#2196F3\"
      }" > /dev/null 2>&1
else
    echo "❌ 컨테이너 재시작 실패!"
    exit 1
fi

# 컨테이너 시작 후 잠시 대기
echo "⏳ 컨테이너 시작 대기 중..."
sleep 3

# 환경변수 로딩 검증
echo "🔍 환경변수 로딩 상태 확인 중..."
DJANGO_DEBUG=$(docker-compose exec -T testpark python -c "import os; from django.conf import settings; print(f'DEBUG={settings.DEBUG}')" 2>/dev/null || echo "DEBUG=확인불가")
CSRF_ORIGINS=$(docker-compose exec -T testpark python -c "import os; from django.conf import settings; print(f'CSRF_ORIGINS={len(settings.CSRF_TRUSTED_ORIGINS)} items')" 2>/dev/null || echo "CSRF_ORIGINS=확인불가")

echo "📊 환경변수 확인 결과:"
echo "  - $DJANGO_DEBUG"
echo "  - $CSRF_ORIGINS"

if echo "$DJANGO_DEBUG" | grep -q "DEBUG=False"; then
    echo "✅ 환경변수가 올바르게 로드되었습니다."
else
    echo "⚠️ 환경변수 로딩에 문제가 있을 수 있습니다."
    echo "🔍 컨테이너 로그 확인:"
    CONTAINER_LOGS=$(docker-compose logs testpark --tail 5 2>&1)
    echo "$CONTAINER_LOGS"

    # 환경변수 로딩 경고 알림
    curl -X POST "$JANDI_WEBHOOK" \
      -H "Content-Type: application/json" \
      -d "{
        \"body\": \"⚠️ TestPark 환경변수 로딩 경고!\\n\\n🔍 확인 결과:\\n• $DJANGO_DEBUG\\n• $CSRF_ORIGINS\\n\\n📋 컨테이너 로그:\\n\\\`\\\`\\\`\\n$CONTAINER_LOGS\\n\\\`\\\`\\\`\\n\\n💡 배포는 계속 진행하지만 확인이 필요합니다.\",
        \"connectColor\": \"#FF9800\"
      }" > /dev/null 2>&1
fi

# 4단계: 헬스 체크
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

# 5단계: 사용하지 않는 이미지 정리
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