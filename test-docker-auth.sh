#!/bin/bash

echo "🔧 Docker 인증 테스트 스크립트"
echo "================================"
echo ""
echo "1. Docker Hub Access Token을 생성하셨나요? (https://hub.docker.com)"
echo "   Account Settings → Security → New Access Token"
echo ""
read -p "Access Token을 입력하세요: " TOKEN

echo ""
echo "🔐 Docker Hub 로그인 시도 중..."
echo "$TOKEN" | docker login -u 7171man --password-stdin

if [ $? -eq 0 ]; then
    echo "✅ 로그인 성공!"
    echo ""
    echo "📦 테스트: hello-world 이미지 다운로드..."
    docker pull hello-world

    if [ $? -eq 0 ]; then
        echo "✅ 이미지 다운로드 성공!"
        echo ""
        echo "🏗️ TestPark 이미지 빌드 시작..."
        docker build -t testpark-test:latest . 2>&1 | tail -20

        if [ $? -eq 0 ]; then
            echo "✅ 빌드 성공!"
            echo ""
            echo "📝 GitHub Secrets에 다음 값을 설정하세요:"
            echo "   DOCKER_USERNAME: 7171man"
            echo "   DOCKER_PASSWORD: $TOKEN"
        else
            echo "❌ 빌드 실패. Dockerfile 확인 필요"
        fi
    else
        echo "❌ 이미지 다운로드 실패"
    fi
else
    echo "❌ 로그인 실패!"
    echo "   - Token이 올바른지 확인하세요"
    echo "   - Docker Hub에서 Token 권한이 Read, Write, Delete인지 확인하세요"
fi