#!/bin/bash

# TestPark 자동 배포 스크립트
# GitHub Actions에서 호출되거나 수동으로 실행 가능

set -e  # 오류 시 스크립트 중단

echo "🚀 TestPark 배포를 시작합니다..."

# 환경 변수 설정
CONTAINER_NAME="testpark"
IMAGE_NAME="7171man/testpark:latest"
PORT="3000"

# Docker Hub에서 최신 이미지 가져오기
echo "📥 최신 Docker 이미지를 가져옵니다..."
docker pull $IMAGE_NAME

# 기존 컨테이너 중지 및 제거
echo "🔄 기존 컨테이너를 중지합니다..."
if [ $(docker ps -q -f name=$CONTAINER_NAME) ]; then
    docker stop $CONTAINER_NAME
    echo "✅ 컨테이너가 중지되었습니다."
fi

if [ $(docker ps -aq -f name=$CONTAINER_NAME) ]; then
    docker rm $CONTAINER_NAME
    echo "✅ 기존 컨테이너가 제거되었습니다."
fi

# 새 컨테이너 실행
echo "🏃 새로운 컨테이너를 시작합니다..."
docker run -d \
    --name $CONTAINER_NAME \
    --restart unless-stopped \
    -p $PORT:$PORT \
    $IMAGE_NAME

# 헬스 체크
echo "🔍 애플리케이션 상태를 확인합니다..."
sleep 5

# 최대 30초 동안 헬스 체크 시도
for i in {1..6}; do
    if curl -f http://localhost:$PORT/health > /dev/null 2>&1; then
        echo "✅ 애플리케이션이 정상적으로 실행되고 있습니다!"
        echo "🌐 접속 주소: http://localhost:$PORT"
        break
    else
        if [ $i -eq 6 ]; then
            echo "❌ 애플리케이션 시작에 실패했습니다."
            docker logs $CONTAINER_NAME
            exit 1
        fi
        echo "⏳ 애플리케이션 시작을 기다리는 중... ($i/6)"
        sleep 5
    fi
done

# 사용하지 않는 이미지 정리
echo "🧹 사용하지 않는 Docker 이미지를 정리합니다..."
docker image prune -f

echo "🎉 TestPark 배포가 성공적으로 완료되었습니다!"
echo "📊 컨테이너 상태:"
docker ps -f name=$CONTAINER_NAME --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"