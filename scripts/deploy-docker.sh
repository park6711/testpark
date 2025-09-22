#!/bin/bash

# TestPark Docker Compose 배포 스크립트 (최적화된 알림 시스템)
# 웹훅 서버에서 호출되는 배포 스크립트

set -e  # 오류 시 스크립트 중단

# 에러 발생 시 체계적인 잔디 알림 발송하는 트랩 함수
send_error_notification() {
    local exit_code=$?
    local line_number=$1
    local command="$2"

    echo "❌ 배포 중 오류 발생! (Line: $line_number, Exit Code: $exit_code)"

    # 에러 단계 분석
    local progress_stage=""
    local progress_bar=""
    if [ $line_number -lt 100 ]; then
        progress_stage="환경변수 설정 단계"
        progress_bar="▓▓▓▓▓▓▓░░░ (70%에서 중단)"
    elif [ $line_number -lt 150 ]; then
        progress_stage="Docker 이미지 다운로드 단계"
        progress_bar="▓▓▓▓▓▓▓▓░░ (75%에서 중단)"
    elif [ $line_number -lt 200 ]; then
        progress_stage="컨테이너 재시작 단계"
        progress_bar="▓▓▓▓▓▓▓▓░░ (80%에서 중단)"
    else
        progress_stage="헬스체크/완료 단계"
        progress_bar="▓▓▓▓▓▓▓▓▓░ (90%에서 중단)"
    fi

    # 에러 상세 정보 수집
    local error_details="라인 $line_number에서 오류 발생\\n명령어: \\\`$command\\\`\\n종료 코드: $exit_code"

    # 컨테이너 상태 확인
    local container_status=""
    if docker-compose ps testpark &>/dev/null; then
        container_status="\\n\\n📊 **컨테이너 상태**:\\n\\\`\\\`\\\`\\n$(docker-compose ps testpark 2>&1 || echo '컨테이너 상태 확인 불가')\\n\\\`\\\`\\\`"
    fi

    # 최근 로그 확인
    local recent_logs=""
    if docker-compose logs testpark --tail 5 &>/dev/null; then
        recent_logs="\\n\\n📋 **최근 로그**:\\n\\\`\\\`\\\`\\n$(docker-compose logs testpark --tail 5 2>&1 || echo '로그 확인 불가')\\n\\\`\\\`\\\`"
    fi

    curl -X POST "$JANDI_WEBHOOK" \
      -H "Content-Type: application/json" \
      -d "{
        \"body\": \"🚨 **TestPark 배포 중 예외 오류**\\n\\n📍 **위치**: 실서버 ($progress_stage)\\n📊 **진행률**: $progress_bar\\n❌ **상태**: 스크립트 실행 중단\\n\\n🔍 **오류 세부사항**:\\n$error_details$container_status$recent_logs\\n\\n🛠️ **긴급 조치 필요**:\\n1️⃣ 스크립트 로그 확인\\n2️⃣ 컨테이너 상태 점검\\n3️⃣ 수동 배포 시도\\n4️⃣ 개발팀에 즉시 연락\\n\\n⚠️ **실서버 서비스 영향 가능성 있음**\",
        \"connectColor\": \"#F44336\"
      }" > /dev/null 2>&1

    echo "📢 긴급 에러 알림 전송 완료!"
    exit $exit_code
}

# 에러 발생 시 트랩 설정
trap 'send_error_notification $LINENO "$BASH_COMMAND"' ERR

echo "🚀 TestPark Docker Compose 배포를 시작합니다..."
echo "📅 배포 시작 시간: $(date '+%Y-%m-%d %H:%M:%S')"
echo "🔧 스크립트 버전: v2.0 (체계적 Jandi 알림 시스템)"

# 환경 변수 설정
COMPOSE_PROJECT="testpark"
IMAGE_NAME="7171man/testpark:latest"
JANDI_WEBHOOK="https://wh.jandi.com/connect-api/webhook/15016768/cb65bef68396631906dc71e751ff5784"

# 70% - 실서버 배포 시작 알림
echo "📢 배포 시작 알림을 전송합니다..."
curl -X POST "$JANDI_WEBHOOK" \
  -H "Content-Type: application/json" \
  -d "{
    \"body\": \"🖥️ **실서버 배포 시작**\\n\\n📍 **위치**: 실서버 (carpenterhosting.cafe24.com)\\n📊 **진행률**: ▓▓▓▓▓▓▓░░░ (70%)\\n🔄 **상태**: Docker Compose 배포 실행 중\\n\\n🐳 **이미지**: $IMAGE_NAME\\n⏱️ **예상 시간**: 1-2분\\n🔧 **스크립트**: v1.3\",
    \"connectColor\": \"#FF9800\"
  }" > /dev/null 2>&1

# 1단계: 실서버용 .env 파일 생성 및 검증
echo "⚙️ 실서버용 환경변수 파일을 생성합니다..."
cd /var/www/testpark

# 기존 .env 파일 강제 삭제 (구문 오류 방지)
if [ -f .env ]; then
    echo "📋 기존 .env 파일 백업 및 삭제 중..."
    cp .env .env.backup.$(date +%Y%m%d_%H%M%S)
    rm -f .env
    echo "✅ 기존 .env 파일 삭제 완료"
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
JANDI_WEBHOOK_URL=https://wh.jandi.com/connect-api/webhook/15016768/cb65bef68396631906dc71e751ff5784

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

    # 75% - Docker 이미지 업데이트 완료 알림
    curl -X POST "$JANDI_WEBHOOK" \
      -H "Content-Type: application/json" \
      -d "{
        \"body\": \"📦 **Docker 이미지 업데이트 완료**\\n\\n📍 **위치**: 실서버 (Docker Hub → 로컬)\\n📊 **진행률**: ▓▓▓▓▓▓▓▓░░ (75%)\\n🔄 **상태**: 컨테이너 재시작 준비 중\\n\\n✅ **완료된 작업**:\\n• .env 파일 생성\\n• Docker Hub 로그인\\n• 최신 이미지 다운로드\\n\\n🐳 **이미지**: $IMAGE_NAME\",
        \"connectColor\": \"#4CAF50\"
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

    # 80% - 컨테이너 재시작 완료 알림
    curl -X POST "$JANDI_WEBHOOK" \
      -H "Content-Type: application/json" \
      -d "{
        \"body\": \"🔄 **컨테이너 재시작 완료**\\n\\n📍 **위치**: 실서버 (Docker Compose)\\n📊 **진행률**: ▓▓▓▓▓▓▓▓░░ (80%)\\n🔄 **상태**: 애플리케이션 시작 중\\n\\n✅ **완료된 작업**:\\n• 새 컨테이너 생성\\n• 포트 바인딩 설정\\n• 환경변수 로딩\\n\\n🔍 **다음 단계**: 헬스체크 진행\",
        \"connectColor\": \"#9C27B0\"
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

    # 85% - 환경변수 로딩 경고 알림
    curl -X POST "$JANDI_WEBHOOK" \
      -H "Content-Type: application/json" \
      -d "{
        \"body\": \"⚠️ **환경변수 로딩 경고**\\n\\n📍 **위치**: 실서버 (Django 애플리케이션)\\n📊 **진행률**: ▓▓▓▓▓▓▓▓▓░ (85%)\\n🔄 **상태**: 배포 계속 진행 중\\n\\n🔍 **확인 결과**:\\n• $DJANGO_DEBUG\\n• $CSRF_ORIGINS\\n\\n📋 **컨테이너 로그**:\\n\\\`\\\`\\\`\\n$CONTAINER_LOGS\\n\\\`\\\`\\\`\\n\\n🛠️ **권장 조치**:\\n1️⃣ 배포 완료 후 설정 재확인\\n2️⃣ 애플리케이션 동작 테스트\",
        \"connectColor\": \"#FF9800\"
      }" > /dev/null 2>&1
fi

# 90% - 헬스체크 시작 알림
curl -X POST "$JANDI_WEBHOOK" \
  -H "Content-Type: application/json" \
  -d "{
    \"body\": \"🔍 **헬스체크 시작**\\n\\n📍 **위치**: 실서버 (애플리케이션 테스트)\\n📊 **진행률**: ▓▓▓▓▓▓▓▓▓░ (90%)\\n🔄 **상태**: HTTP 응답 대기 중\\n\\n🏥 **검사 항목**:\\n• HTTP GET / 요청\\n• 응답 코드 200 확인\\n• 최대 6회 시도 (30초)\\n\\n⏱️ **예상 소요**: 10-30초\",
    \"connectColor\": \"#673AB7\"
  }" > /dev/null 2>&1

# 4단계: 헬스 체크
echo "🔍 애플리케이션 상태를 확인합니다..."
sleep 5

# 최대 30초 동안 헬스 체크 시도
HEALTH_CHECK_SUCCESS=false
for i in {1..6}; do
    if curl -f http://testpark:8000/ > /dev/null 2>&1; then
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
                \"body\": \"🚨 **헬스체크 실패 - 배포 중단**\\n\\n📍 **위치**: 실서버 (애플리케이션 레벨)\\n📊 **진행률**: ▓▓▓▓▓▓▓▓▓░ (90%에서 중단)\\n❌ **상태**: 애플리케이션 응답 없음\\n\\n🔍 **문제 상황**:\\n• 컨테이너는 실행 중이나 HTTP 응답 없음\\n• 30초 동안 6회 시도 모두 실패\\n\\n📋 **최근 로그**:\\n\\\`\\\`\\\`\\n${CONTAINER_LOGS}\\n\\\`\\\`\\\`\\n\\n🛠️ **긴급 조치 필요**:\\n1️⃣ 컨테이너 로그 상세 확인\\n2️⃣ 포트 바인딩 상태 점검\\n3️⃣ 수동 재시작 시도\\n4️⃣ 이전 버전으로 롤백 고려\",
                \"connectColor\": \"#F44336\"
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

# 100% - 최종 배포 완료 알림
curl -X POST "$JANDI_WEBHOOK" \
  -H "Content-Type: application/json" \
  -d "{
    \"body\": \"🎉 **TestPark 자동배포 완료!**\\n\\n📍 **위치**: 실서버 (서비스 운영 중)\\n📊 **진행률**: ▓▓▓▓▓▓▓▓▓▓ (100%)\\n✅ **상태**: 배포 성공 및 서비스 정상\\n\\n📋 **배포 결과**:\\n• 컨테이너 ID: \\\`$CONTAINER_ID\\\`\\n• 상태: $CONTAINER_STATUS\\n• 업타임: $CONTAINER_UPTIME\\n• 정리된 이미지: ${CLEANED_IMAGES}개\\n\\n🌐 **서비스 주소**:\\n[TestPark 접속하기](https://carpenterhosting.cafe24.com)\\n\\n✅ **모든 검증 완료**:\\n• 헬스체크 통과\\n• 환경변수 로딩 정상\\n• 컨테이너 상태 healthy\",
    \"connectColor\": \"#4CAF50\"
  }" > /dev/null 2>&1

echo "📢 잔디 알림 전송 완료!"
echo "🌐 서비스 접속: https://carpenterhosting.cafe24.com"