# 🏗️ TestPark - (주)박목수의 열린 견적서

> 인테리어 업체와 고객을 연결하는 스마트 플랫폼

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-3.2+-green.svg)](https://www.djangoproject.com/)
[![MariaDB](https://img.shields.io/badge/MariaDB-11.2-orange.svg)](https://mariadb.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)

## ⚡ Quick Start (로컬 개발자용)

```bash
# 🚀 자동 설정 (권장)
./setup-local-dev.sh

# 또는 Docker Compose 직접 실행
docker-compose up -d

# 접속: http://localhost:8000
```

**🔗 실서버 관련 작업은 [DEPLOYMENT.md](DEPLOYMENT.md) 참조**

## 🏗️ 프로젝트 구조

```
testpark/
├── README.md
├── DEPLOYMENT.md              # 🚀 완전한 배포 가이드
├── Dockerfile
├── docker-compose.yml
├── manage.py                  # Django 관리 스크립트
├── requirements.txt           # Python 의존성
├── accounts/                  # 사용자 인증 앱
├── testpark_project/          # Django 메인 설정
├── scripts/
│   ├── deploy.sh             # 🆕 5단계 스마트 배포 스크립트
│   ├── webhook-server.js     # 웹훅 서버 (Express.js)
│   └── webhook.service       # Systemd 서비스 설정
├── docs/
│   ├── CICD-SETUP.md        # CI/CD 설정 가이드
│   ├── LOCAL-SETUP.md       # 로컬 개발 환경 설정
│   └── NAVER_LOGIN_GUIDE.md # 네이버 로그인 연동 가이드
├── .github/
│   └── workflows/
│       └── ci-cd.yml        # 🆕 완전 자동화 GitHub Actions
└── .gitignore
```

## 🚀 로컬 개발 환경 구축

### Python 가상환경 설정

```bash
# 1. 저장소 클론
git clone https://github.com/park6711/testpark.git
cd testpark

# 2. Python 가상환경 생성
python -m venv venv

# 3. 가상환경 활성화
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 4. 의존성 설치
pip install -r requirements.txt
```

### Django 개발 서버 실행

```bash
# 1. 데이터베이스 마이그레이션
python manage.py migrate

# 2. 슈퍼유저 생성 (선택사항)
python manage.py createsuperuser

# 3. 개발 서버 시작
python manage.py runserver

# 4. 브라우저에서 접속
# http://localhost:8000/
```

### Docker로 로컬 테스트

```bash
# Docker Compose로 실행 (개발용)
docker-compose up -d

# 또는 개별 빌드 및 실행
docker build -t testpark-local .
docker run -p 8001:8000 testpark-local

# 로컬 Docker 테스트 접속
curl http://localhost:8001/
```

## 🔄 자동 배포 시스템

이 프로젝트는 **완전 자동화된 CI/CD 파이프라인**을 갖추고 있습니다:

### 🚀 개발자 워크플로우
```bash
# 1. 로컬에서 개발
python manage.py runserver

# 2. 변경사항 커밋
git add .
git commit -m "feat: 새 기능 추가"

# 3. GitHub에 푸시 → 자동 배포 시작!
git push origin master
```

### 📡 자동 배포 과정
1. **GitHub Actions** 자동 트리거
2. **Docker 이미지** 빌드 & 푸시
3. **실서버 SSH 배포** 자동 실행
4. **5단계 상세 알림** (잔디 웹훅)
5. **헬스체크 완료** ✅

### 📚 상세 가이드
- **🚀 [실서버 배포 가이드](DEPLOYMENT.md)** - 실서버 운영 및 배포 관리
- **⚙️ [CI/CD 설정](docs/CICD-SETUP.md)** - GitHub Actions 설정
- **🏠 [로컬 환경 설정](docs/LOCAL-SETUP.md)** - 로컬 개발 환경 구축
- **🔐 [네이버 로그인](docs/NAVER_LOGIN_GUIDE.md)** - 소셜 로그인 연동

## 🌟 주요 기능

### 현재 구현된 기능
- ✅ **네이버 소셜 로그인** - OAuth 2.0 연동
- ✅ **사용자 인증 시스템** - Django 기본 인증 + 소셜 로그인
- ✅ **홈페이지** - 로그인/로그아웃 기능
- ✅ **완전 자동화 배포** - GitHub Actions + 5단계 알림 시스템

### API 엔드포인트
```
Django URLs:
- GET  /                    # 메인 홈페이지
- GET  /accounts/login/     # 로그인 페이지
- GET  /accounts/logout/    # 로그아웃
- GET  /accounts/profile/   # 사용자 프로필
- GET  /auth/naver/         # 네이버 로그인 시작
- GET  /auth/naver/callback/ # 네이버 로그인 콜백

Admin URLs:
- GET  /admin/              # Django 관리자 페이지
```

## 🛠️ 로컬 개발 가이드

### 데이터베이스 관리
```bash
# 마이그레이션 파일 생성
python manage.py makemigrations

# 마이그레이션 적용
python manage.py migrate

# SQLite 데이터베이스 위치
# db.sqlite3 (프로젝트 루트)
```

### 테스트 및 디버깅
```bash
# Django 셸 접속
python manage.py shell

# 테스트 실행 (추가 예정)
python manage.py test

# 정적 파일 수집 (배포 시)
python manage.py collectstatic

# 로그 확인 (개발 서버)
python manage.py runserver --verbosity=2
```

### 코드 스타일 및 품질
```bash
# Python 코드 포맷팅 (추가 권장)
pip install black flake8
black .
flake8 .

# requirements.txt 업데이트
pip freeze > requirements.txt
```

## 🤝 기여하기

### 개발 프로세스
1. **Fork** 후 로컬에 클론
2. **새 브랜치** 생성: `git checkout -b feature/새기능`
3. **로컬 테스트**: `python manage.py runserver`
4. **변경사항 커밋**: `git commit -m "feat: 새 기능 추가"`
5. **푸시**: `git push origin feature/새기능`
6. **Pull Request** 생성

### 커밋 메시지 규칙
```
feat: 새 기능 추가
fix: 버그 수정
docs: 문서 업데이트
style: 코드 스타일 변경
refactor: 코드 리팩토링
test: 테스트 추가/수정
chore: 빌드 관련 작업
```

## 🔗 링크

- **GitHub Repository**: https://github.com/park6711/testpark
- **Docker Hub**: https://hub.docker.com/r/7171man/testpark
- **Production Server**: https://carpenterhosting.cafe24.com

## 📈 향후 계획

### 개발 로드맵
- [ ] **테스트 코드 작성** - Unit/Integration 테스트
- [ ] **API 문서화** - Django REST framework + Swagger
- [ ] **데이터베이스 최적화** - PostgreSQL 연동
- [ ] **프론트엔드 개선** - React/Vue.js 연동
- [ ] **모니터링 시스템** - 로그 분석 및 알림
- [ ] **성능 최적화** - 캐싱, CDN 적용

### 기술 스택 확장
- [ ] **Redis** - 세션 스토어 및 캐싱
- [ ] **Celery** - 비동기 작업 처리
- [ ] **Elasticsearch** - 검색 기능
- [ ] **Grafana** - 모니터링 대시보드

## 🆘 개발 지원

### 문제 해결
- **Issues**: https://github.com/park6711/testpark/issues
- **Discussions**: 기술 토론 및 질문
- **Wiki**: 상세 개발 가이드 (예정)

### 로컬 개발 문제 해결
```bash
# 가상환경 문제
deactivate && source venv/bin/activate

# 패키지 의존성 문제
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall

# Django 설정 문제
python manage.py check
python manage.py check --deploy

# 포트 충돌 문제
python manage.py runserver 8001  # 다른 포트 사용
```

## 🧪 자동 배포 테스트

### 최근 배포 테스트 기록
- **테스트 일시**: 2025-09-18 13:00:00 (KST)
- **테스트 목적**: 웹훅 기반 완전 자동화 배포 시스템 검증
- **테스트 방법**: GitHub 커밋 → GitHub Actions → 웹훅 API → Docker 배포
- **예상 결과**: SSH 없이 웹훅만으로 자동 배포 완료

### 배포 시스템 아키텍처
```
GitHub Push → GitHub Actions → Webhook API → Docker Deployment → Jandi Notification
             (CI/CD Pipeline)   (Port 8080)    (TestPark Service)     (팀 알림)
```# TestPark v2.0 알림 시스템 테스트 Mon 22 Sep 2025 01:27:19 PM KST
