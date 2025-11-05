# 🏗️ TestPark - (주)박목수의 열린 견적서

> 인테리어 업체와 고객을 연결하는 스마트 플랫폼

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-3.2+-green.svg)](https://www.djangoproject.com/)
[![MariaDB](https://img.shields.io/badge/MariaDB-11.2-orange.svg)](https://mariadb.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)

## ⚡ Quick Start (로컬 개발자용)

```bash
# 1. 저장소 클론
git clone https://github.com/park6711/testpark.git
cd testpark

# 2. Docker 컨테이너 시작
docker-compose up -d

# 3. 실서버 백업 복원 (선택사항)
./sync-db.sh  # 2번 선택하여 백업 파일 임포트

# 4. 접속
http://localhost:8000
```

**🔗 실서버 관련 작업은 [DEPLOYMENT.md](DEPLOYMENT.md) 참조**

## 🏗️ 프로젝트 구조

### 디렉토리 구조
```
testpark/
├── README.md
├── DEPLOYMENT.md              # 🚀 완전한 배포 가이드
├── Dockerfile
├── docker-compose.yml
├── manage.py                  # Django 관리 스크립트
├── requirements.txt           # Python 의존성
│
├── testpark_project/          # 🎯 Django 메인 설정
│   ├── settings.py           # Django 설정
│   ├── urls.py               # URL 라우팅
│   ├── constants.py          # ⭐ 프로젝트 전역 상수
│   └── utils.py              # ⭐ 프로젝트 전역 유틸리티
│
├── order/                     # 📦 의뢰 관리 앱
│   ├── models.py             # 데이터 모델
│   ├── views.py              # 뷰 로직
│   ├── api_views.py          # REST API
│   ├── constants.py          # ⭐ Order 앱 상수
│   └── utils.py              # ⭐ Order 앱 유틸리티
│
├── accounts/                  # 사용자 인증 앱
├── company/                   # 업체 관리 앱
├── member/                    # 회원 관리 앱
│
├── static/                    # 정적 파일
│   ├── js/                   # 🌐 전역 JavaScript
│   │   ├── constants.js      # ⭐ JS 전역 상수
│   │   ├── utils.js          # ⭐ JS 전역 유틸리티
│   │   └── main.js           # ⭐ 메인 앱 (TestPark 네임스페이스)
│   └── order/js/             # Order 앱 JavaScript
│       ├── constants.js      # ⭐ Order 앱 상수
│       ├── utils.js          # ⭐ Order 앱 유틸리티
│       ├── order-list.js     # 의뢰 리스트
│       ├── order-assign.js   # 업체 할당
│       ├── order-memo.js     # 메모 관리
│       └── order-estimate.js # 견적서 관리
│
├── scripts/
│   ├── deploy.sh             # 5단계 스마트 배포 스크립트
│   ├── webhook-server.js     # 웹훅 서버 (Express.js)
│   └── webhook.service       # Systemd 서비스 설정
│
├── docs/
│   ├── CICD-SETUP.md        # CI/CD 설정 가이드
│   ├── LOCAL-SETUP.md       # 로컬 개발 환경 설정
│   └── NAVER_LOGIN_GUIDE.md # 네이버 로그인 연동 가이드
│
├── .github/
│   └── workflows/
│       └── ci-cd.yml        # 완전 자동화 GitHub Actions
└── .gitignore
```

### ⭐ Django 표준 구조 (v1.1.0+)

이 프로젝트는 Django 커뮤니티 베스트 프랙티스를 따릅니다:

**Python 계층 구조**
```python
# 프로젝트 전역 (모든 앱에서 사용)
from testpark_project.constants import OrderStatus, PAGINATION
from testpark_project.utils import format_date, is_urgent

# 앱별 (해당 앱 전용)
from order.constants import AssignStatus
from order.utils import calculate_assign_priority
```

**JavaScript 계층 구조**
```javascript
// 전역 상수
TestParkConstants.OrderStatus.WAITING  // '대기중'
TestParkConstants.BadgeType.SUCCESS    // 'success'

// 전역 유틸리티
TestPark.utils.formatDate(date)
TestPark.api.call(url, 'GET')

// Order 앱
OrderConstants.AssignStatus.PENDING
OrderUtils.getOrderDisplayName(order)
```

**구조의 장점**
- ✅ **일관성**: 표준 패턴으로 코드 위치 즉시 파악
- ✅ **확장성**: 새 앱 추가 시 동일한 패턴 적용
- ✅ **유지보수**: 상수/유틸리티가 명확히 분리
- ✅ **재사용성**: 프로젝트 전역/앱별 구분으로 코드 재사용 극대화
- ✅ **테스트**: 독립적인 함수로 유닛 테스트 용이

## 🚀 로컬 개발 환경 구축

### TODO(human): Docker 기반 개발 환경 설정을 작성해주세요
# 아래 내용을 포함해서 작성:
# 1. docker-compose.override.yml을 사용한 로컬 코드 마운트
# 2. MariaDB 컨테이너 접속 방법
# 3. sync-db.sh를 사용한 실서버 백업 복원
# 4. Docker 컨테이너 로그 확인 방법

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

**인증 & 사용자 관리**
- ✅ **네이버 소셜 로그인** - OAuth 2.0 연동
- ✅ **사용자 인증 시스템** - Django 기본 인증 + 소셜 로그인
- ✅ **사용자 프로필** - 회원 정보 관리

**의뢰 & 업체 관리 (Order 앱)**
- ✅ **의뢰 리스트 관리** - 검색, 필터링, 페이지네이션
- ✅ **업체 할당 시스템** - 지정/공동구매 방식 지원
- ✅ **견적서 관리** - 견적서 등록, 조회, 삭제
- ✅ **메모 시스템** - 의뢰별 메모 작성 및 관리
- ✅ **의뢰 상세보기** - 모달 기반 상세 정보 표시
- ✅ **의뢰 복사 기능** - 기존 의뢰 복제

**개발 & 배포**
- ✅ **완전 자동화 배포** - GitHub Actions + 5단계 알림 시스템
- ✅ **Django 표준 구조** - constants/utils 패턴 적용
- ✅ **전역 네임스페이스** - 함수 충돌 방지 시스템
- ✅ **REST API** - Django REST framework 기반

### API 엔드포인트

**웹 페이지**
```
GET  /                      # 메인 홈페이지
GET  /accounts/login/       # 로그인 페이지
GET  /accounts/logout/      # 로그아웃
GET  /accounts/profile/     # 사용자 프로필
GET  /auth/naver/           # 네이버 로그인 시작
GET  /auth/naver/callback/  # 네이버 로그인 콜백
GET  /order/                # 의뢰 리스트
GET  /admin/                # Django 관리자 페이지
```

**REST API (Order)**
```
GET    /order/api/orders/                    # 의뢰 목록
GET    /order/api/orders/{id}/               # 의뢰 상세
POST   /order/api/orders/{id}/copy/          # 의뢰 복사
POST   /order/api/orders/assign_companies/   # 업체 할당
GET    /order/api/companies/                 # 업체 목록
GET    /order/api/estimates/                 # 견적서 목록
POST   /order/api/estimates/                 # 견적서 생성
DELETE /order/api/estimates/{id}/            # 견적서 삭제
GET    /order/api/memos/                     # 메모 목록
POST   /order/api/memos/                     # 메모 생성
GET    /order/api/group-purchases/           # 공동구매 목록
```

## 🛠️ 로컬 개발 가이드

### 데이터베이스 관리
```bash
# MariaDB 컨테이너 직접 접속
docker exec -it testpark-mariadb mariadb -u testpark -p'**jeje4211' testpark

# 또는 헬퍼 스크립트 사용
./scripts/db-connect.sh

# Django 마이그레이션 (컨테이너 내에서)
docker exec testpark python manage.py makemigrations
docker exec testpark python manage.py migrate

# 데이터베이스 백업/복원
./sync-db.sh  # 대화형 메뉴
```

### 테스트 및 디버깅
```bash
# Django 셸 접속 (컨테이너 내)
docker exec -it testpark python manage.py shell

# 컨테이너 로그 확인
docker-compose logs -f testpark
docker-compose logs -f mariadb

# 테스트 실행
docker exec testpark python manage.py test

# 정적 파일 수집 (배포 시)
docker exec testpark python manage.py collectstatic
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
- [ ] **데이터베이스 최적화** - MariaDB 인덱싱 및 쿼리 최적화
- [ ] **모니터링 시스템** - 로그 분석 및 알림
- [ ] **성능 최적화** - 캐싱, CDN 적용
- [ ] **백업 자동화** - 정기적인 DB 백업 시스템

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
# Docker 컨테이너 상태 확인
docker ps -a
docker-compose ps

# 컨테이너 재시작
docker-compose down && docker-compose up -d

# 포트 충돌 문제
lsof -i :8000  # 8000번 포트 사용 프로세스 확인
docker-compose stop && docker-compose up -d

# DB 연결 문제
docker exec testpark-mariadb mariadb -u root -ptestpark-root -e "SELECT 1"

# 볼륨 권한 문제
docker-compose down -v  # 볼륨 삭제 후 재생성
docker-compose up -d
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
