# TestPark

TestPark 프로젝트 - Docker와 CI/CD가 구성된 Node.js Express 애플리케이션입니다.

## 🏗️ 프로젝트 구조

```
testpark/
├── README.md
├── DEPLOYMENT.md              # 🚀 배포 가이드
├── Dockerfile
├── docker-compose.yml
├── package.json
├── src/
│   └── index.js                 # Express 애플리케이션
├── scripts/
│   ├── deploy.sh               # 배포 스크립트
│   ├── webhook-server.js       # Webhook 서버
│   └── webhook.service         # Systemd 서비스
├── docs/
│   └── CICD-SETUP.md          # CI/CD 설정 가이드
├── .github/
│   └── workflows/
│       └── ci-cd.yml          # GitHub Actions 워크플로우
└── .gitignore
```

## 🚀 시작하기

### 로컬 개발 환경

```bash
# 의존성 설치
npm install

# 개발 서버 실행
npm run dev

# 접속
curl http://localhost:3000
```

### Docker로 실행

```bash
# Docker Compose로 실행
docker-compose up -d

# 또는 개별 실행
docker build -t testpark .
docker run -p 3000:3000 testpark
```

## 🔄 CI/CD 자동 배포

이 프로젝트는 완전 자동화된 CI/CD 파이프라인을 포함합니다:

### 자동 배포 플로우
1. **코드 Push** → GitHub master 브랜치
2. **GitHub Actions** → Docker 이미지 빌드 & Docker Hub 푸시
3. **Webhook** → 실서버 자동 배포
4. **헬스 체크** → 배포 완료 확인

### 설정 방법
- **🚀 [배포 가이드](DEPLOYMENT.md)** - 전체 배포 시스템 설명 및 설정 방법
- **⚙️ [CI/CD 설정 가이드](docs/CICD-SETUP.md)** - GitHub Actions 상세 설정

## 📊 API 엔드포인트

- `GET /` - 메인 페이지
- `GET /health` - 헬스 체크

## 📚 문서

- **🚀 [배포 가이드](DEPLOYMENT.md)** - 자동화 배포 시스템 완전 가이드
- **⚙️ [CI/CD 설정](docs/CICD-SETUP.md)** - GitHub Actions 상세 설정

## 🔗 링크

- **GitHub**: https://github.com/park6711/testpark
- **Docker Hub**: 7171man/testpark
- **Production**: http://your-server:3000

## 🛠️ 개발

### 로컬 테스트
```bash
# 애플리케이션 헬스 체크
curl http://localhost:3000/health

# Docker 컨테이너 상태
docker ps -f name=testpark
```

### 수동 배포
```bash
# 배포 스크립트 실행
bash scripts/deploy.sh

# 또는 Webhook 호출
curl -X POST http://localhost:8080/deploy
```

## 🚨 문제 해결

로그 확인:
```bash
# 애플리케이션 로그
docker logs testpark

# Webhook 서버 로그 (실서버)
sudo journalctl -u testpark-webhook -f
```

## 📈 향후 계획

- [ ] 데이터베이스 연동
- [ ] 사용자 인증 시스템
- [ ] API 문서화 (Swagger)
- [ ] 모니터링 대시보드
- [ ] 성능 최적화