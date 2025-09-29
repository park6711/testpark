#!/bin/bash
# TestPark 로컬 서버 업데이트 스크립트

echo "🔄 TestPark 로컬 업데이트 시작..."

# TODO(human): 개발 모드 옵션 추가
# --dev 플래그 처리 로직을 여기에 구현하세요

# 1. GitHub에서 최신 코드 받기
echo "📥 GitHub에서 최신 코드 받기..."
git pull origin master

if [ $? -ne 0 ]; then
    echo "⚠️ Git pull 실패. 로컬 변경사항 확인 필요"
    echo "로컬 변경사항 임시 저장: git stash"
    echo "강제 업데이트: git fetch && git reset --hard origin/master"
    exit 1
fi

# 2. Docker 이미지 최신화
echo "🐳 Docker Hub에서 최신 이미지 받기..."
docker pull 7171man/testpark:latest

# 3. 컨테이너 재시작
echo "♻️ 컨테이너 재시작..."
docker-compose down
docker-compose up -d mariadb testpark

# 4. 상태 확인
echo "✅ 업데이트 완료!"
echo ""
echo "📊 실행 중인 서비스:"
docker-compose ps

echo ""
echo "🌐 접속 주소:"
echo "  - Django: http://localhost:8000"
echo "  - React Dev: http://localhost:3000 (필요시 docker-compose up -d frontend)"
echo "  - MariaDB: localhost:3306"