# 🚀 TestPark 종합 배포 가이드

TestPark 프로젝트의 완전한 배포 프로세스와 환경 설정 가이드입니다.

## 📋 목차
1. [개발 환경 구성](#개발-환경-구성)
2. [브랜치 전략](#브랜치-전략)
3. [배포 프로세스](#배포-프로세스)
4. [Docker 환경 설정](#docker-환경-설정)
5. [트러블슈팅](#트러블슈팅)

---

## 🔧 개발 환경 구성

### 다중 로컬 환경
현재 3개의 로컬 개발 환경이 구성되어 있습니다:

```
🖥️ 개발 환경
├── Sam MacBook (Local1)
├── Luke MacBook (Local2)
└── Luke Windows (Local3)
```

### 환경별 설정

#### 로컬 개발 환경
```bash
# 프로젝트 클론
git clone https://github.com/park6711/testpark.git
cd testpark

# 환경 설정
cp .env.example .env.local
# 네이버 로그인 콜백: http://localhost:8001/auth/naver/callback/

# Docker 실행
docker-compose up -d
```

#### 실서버 환경 (210.114.22.100)
```bash
# 실서버 접속
ssh username@210.114.22.100

# 프로젝트 디렉토리
cd /var/www/testpark

# 서비스 확인
docker-compose ps
curl https://carpenterhosting.cafe24.com/health
```

---

## 🌿 브랜치 전략

### 브랜치 생성 규칙
```
작업자/작업내용
```

#### 예시
```bash
# Sam이 사용자 인증 기능 작업
git checkout -b sam/user-authentication

# Luke가 데이터베이스 최적화 작업
git checkout -b luke/database-optimization

# Sam이 UI 디자인 업데이트 작업
git checkout -b sam/ui-design-update
```

### 브랜치 워크플로우

```
🔄 브랜치 워크플로우
├── 1️⃣ 작업 브랜치 생성 (작업자/작업내용)
├── 2️⃣ 로컬 개발 및 테스트
├── 3️⃣ GitHub 푸시
├── 4️⃣ Pull Request 생성
├── 5️⃣ 코드 리뷰
├── 6️⃣ master 브랜치 병합
└── 7️⃣ 자동 배포 실행
```

### 브랜치 관리 명령어
```bash
# 새 작업 시작
git checkout master
git pull origin master
git checkout -b {작업자}/{작업내용}

# 작업 완료 후
git add .
git commit -m "작업 내용 설명"
git push origin {작업자}/{작업내용}

# GitHub에서 Pull Request 생성

# 작업 완료 후 브랜치 정리
git checkout master
git pull origin master
git branch -d {작업자}/{작업내용}
```

---

## 🚀 배포 프로세스

### 1. 자동 배포 (GitHub Actions)

#### 트리거 조건
- `master` 브랜치에 코드 푸시
- Pull Request가 `master`에 병합

#### 배포 과정
```
📱 GitHub Actions 워크플로우
├── 1️⃣ 코드 체크아웃
├── 2️⃣ Docker 이미지 빌드
├── 3️⃣ Docker Hub 푸시 (7171man/testpark:latest)
├── 4️⃣ 실서버 웹훅 호출
├── 5️⃣ Docker Compose 업데이트
├── 6️⃣ 헬스체크 실행
└── 7️⃣ Jandi 알림 전송
```

#### 배포 로그 확인
```bash
# GitHub Actions 로그 확인
https://github.com/park6711/testpark/actions

# 실서버 배포 로그 확인
docker-compose logs webhook --tail 20
```

### 2. 수동 배포

#### 실서버에서 직접 배포
```bash
# 실서버 접속
ssh username@210.114.22.100
cd /var/www/testpark

# 수동 배포 실행
curl -X POST https://carpenterhosting.cafe24.com/deploy
```

#### 웹 인터페이스로 배포
```
🌐 수동 배포 URL
https://carpenterhosting.cafe24.com/deploy
```

### 3. 배포 알림 시스템

#### Jandi 알림 단계 (최적화됨)
1. **🚀 배포 시작 알림** - 노란색
2. **⚡ 진행 상황 알림** - 파란색
3. **✅ 배포 완료 알림** - 초록색
4. **❌ 배포 실패 알림** - 빨간색 (오류 시에만)

---

## 🐳 Docker 환경 설정

### Docker Compose 구성

#### 파일 구조
```
/var/www/testpark/
├── docker-compose.yml      # 메인 구성 파일
├── webhook.Dockerfile      # 웹훅 서버 이미지
├── scripts/
│   ├── webhook-server-docker.js  # 웹훅 서버 코드
│   └── deploy-docker.sh          # 배포 스크립트
└── docs/                   # 문서들
```

#### 서비스 구성
```yaml
# TestPark 메인 애플리케이션
testpark:
  image: 7171man/testpark:latest
  container_name: testpark
  ports:
    - "8000:8000"
  restart: unless-stopped

# 웹훅 서버
webhook:
  build:
    context: .
    dockerfile: webhook.Dockerfile
  container_name: testpark-webhook
  ports:
    - "8080:8080"
  volumes:
    - /var/run/docker.sock:/var/run/docker.sock
    - .:/var/www/testpark
```

### Docker 명령어

#### 기본 명령어
```bash
# 서비스 시작
docker-compose up -d

# 서비스 상태 확인
docker-compose ps

# 로그 확인
docker-compose logs -f

# 서비스 재시작
docker-compose restart

# 서비스 중지
docker-compose down
```

#### 개별 서비스 관리
```bash
# TestPark만 재시작
docker-compose restart testpark

# 웹훅 서버만 재빌드
docker-compose build webhook
docker-compose up -d webhook

# 특정 서비스 로그 확인
docker-compose logs testpark --tail 20
docker-compose logs webhook --tail 20
```

---

## 🔍 모니터링 및 헬스체크

### 서비스 상태 확인

#### 자동 헬스체크
```bash
# TestPark 애플리케이션
curl -f https://carpenterhosting.cafe24.com/auth/login/

# 웹훅 서버
curl -f https://carpenterhosting.cafe24.com/health

# Docker 컨테이너 상태
docker-compose ps
```

#### 헬스체크 응답 예시
```json
# /health 엔드포인트 응답
{
  "status": "OK",
  "service": "TestPark Docker Compose Webhook Server",
  "uptime": 94.845116722,
  "version": "2.0.0"
}
```

### 로그 모니터링

#### 실시간 로그 확인
```bash
# 전체 서비스 로그
docker-compose logs -f

# 배포 관련 로그
tail -f /var/log/apache2/access.log | grep -E "(deploy|webhook)"

# Jandi 알림 로그 확인
docker-compose logs webhook | grep -i jandi
```

---

## 🚨 트러블슈팅

### 일반적인 문제 해결

#### 1. TestPark 서비스 접속 불가
```bash
# 문제 진단
docker-compose ps testpark
docker-compose logs testpark --tail 20

# 해결 방법
docker-compose restart testpark

# 이미지 업데이트가 필요한 경우
docker-compose pull testpark
docker-compose up -d testpark
```

#### 2. 웹훅 서버 오류
```bash
# 문제 진단
curl -f http://localhost:8080/health
docker-compose logs webhook --tail 20

# 해결 방법
docker-compose restart webhook

# 재빌드가 필요한 경우
docker-compose build webhook
docker-compose up -d webhook
```

#### 3. 배포 실패
```bash
# 배포 로그 확인
docker-compose logs webhook | grep -E "(배포|deploy)"

# 수동 배포 테스트
curl -X POST https://carpenterhosting.cafe24.com/deploy

# 스크립트 직접 실행
bash /var/www/testpark/scripts/deploy-docker.sh
```

#### 4. Apache 프록시 오류
```bash
# Apache 설정 테스트
sudo apache2ctl configtest

# Apache 재시작
sudo systemctl restart apache2

# 프록시 설정 확인
cat /etc/apache2/sites-available/unified-vhost.conf
```

### 응급 복구 절차

#### 전체 서비스 재시작
```bash
# 1단계: 모든 컨테이너 중지
docker-compose down

# 2단계: 최신 이미지 받기
docker-compose pull

# 3단계: 서비스 재시작
docker-compose up -d

# 4단계: 상태 확인
docker-compose ps
curl https://carpenterhosting.cafe24.com/health
```

#### 이전 버전으로 롤백
```bash
# 특정 버전으로 롤백 (예시)
docker pull 7171man/testpark:v1.0.0
docker tag 7171man/testpark:v1.0.0 7171man/testpark:latest
docker-compose up -d testpark
```

---

## 📞 연락처 및 지원

### 긴급 상황 대응
- **서버 장애**: 즉시 Jandi 채널 확인
- **배포 실패**: GitHub Actions 로그 확인 후 수동 배포
- **네트워크 문제**: Apache 및 Docker 상태 확인

### 유용한 URL
- **서비스**: https://carpenterhosting.cafe24.com
- **헬스체크**: https://carpenterhosting.cafe24.com/health
- **수동 배포**: https://carpenterhosting.cafe24.com/deploy
- **GitHub 저장소**: https://github.com/park6711/testpark
- **Docker Hub**: https://hub.docker.com/r/7171man/testpark

---

**📝 이 가이드는 시스템 변경 시 업데이트해야 합니다.**

*마지막 업데이트: 2024년 현재*