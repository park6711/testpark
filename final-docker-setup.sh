#!/bin/bash

echo "🚀 Docker Hub 최종 설정 스크립트"
echo "=================================="
echo ""
echo "새로 생성한 Access Token:"
echo "[GitHub Secrets에 설정된 토큰 사용]"
echo ""
echo "이제 GitHub Secrets에 설정해주세요:"
echo ""
echo "1. GitHub Secrets 페이지 접속"
echo "   👉 https://github.com/park6711/testpark/settings/secrets/actions"
echo ""
echo "2. DOCKER_USERNAME 수정"
echo "   - 클릭 → Update"
echo "   - 값: 7171man"
echo "   - Update secret 클릭"
echo ""
echo "3. DOCKER_PASSWORD 수정"
echo "   - 클릭 → Update"
echo "   - 값: [생성된 Docker Hub Access Token]"
echo "   - Update secret 클릭"
echo ""
echo "4. 설정 완료 후 Enter 키를 누르세요..."
read

echo ""
echo "🔄 테스트 배포 시작..."
git commit --allow-empty -m "deploy: Docker Hub token generated via API"
git push origin master

echo ""
echo "✅ 배포 시작됨!"
echo "👉 확인: https://github.com/park6711/testpark/actions"