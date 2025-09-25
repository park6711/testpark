#!/bin/bash

echo "🔐 Docker Hub 새 토큰 테스트"
echo "=============================="
echo ""
echo "Docker Hub에서 새 토큰을 생성하셨나요?"
echo "(https://hub.docker.com/settings/security)"
echo ""
read -p "새 토큰을 입력하세요 (dckr_pat_...): " NEW_TOKEN

echo ""
echo "🔄 로그아웃 후 새 토큰으로 로그인 시도..."
docker logout 2>/dev/null

echo "$NEW_TOKEN" | docker login -u 7171man --password-stdin

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ 로그인 성공! 토큰이 올바릅니다."
    echo ""
    echo "📦 테스트: hello-world 이미지 다운로드..."
    docker pull hello-world

    if [ $? -eq 0 ]; then
        echo "✅ 이미지 다운로드 성공!"
        echo ""
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "🎯 GitHub Secrets에 설정할 값:"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "DOCKER_USERNAME: 7171man"
        echo "DOCKER_PASSWORD: $NEW_TOKEN"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""
        echo "👉 https://github.com/park6711/testpark/settings/secrets/actions"
    fi
else
    echo ""
    echo "❌ 로그인 실패!"
    echo "다음을 확인하세요:"
    echo "1. 토큰이 완전히 복사되었는지 (dckr_pat_로 시작)"
    echo "2. Docker Hub 사용자명이 7171man이 맞는지"
    echo "3. 토큰 권한이 Read, Write, Delete 모두 체크되었는지"
fi