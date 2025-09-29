# 🚀 TestPark 로컬 개발 환경 구성 가이드

## 📋 목차
1. [사전 요구사항](#사전-요구사항)
2. [프로젝트 클론](#프로젝트-클론)
3. [환경 변수 설정](#환경-변수-설정)
4. [Docker 환경 구성](#docker-환경-구성)
5. [개발 서버 실행](#개발-서버-실행)
6. [데이터베이스 초기화](#데이터베이스-초기화)
7. [문제 해결](#문제-해결)
8. [개발 워크플로우](#개발-워크플로우)

---

## 🔧 사전 요구사항

### 필수 설치 프로그램
- **Docker Desktop** (최신 버전)
  - Windows: https://www.docker.com/products/docker-desktop
  - Mac: `brew install --cask docker`
  - Linux: `sudo apt-get install docker-ce docker-ce-cli containerd.io`

- **Docker Compose** (Docker Desktop에 포함)
  - 확인: `docker-compose --version`

- **Git**
  - 확인: `git --version`

- **Python 3.8+** (선택사항, 로컬 개발 시)
  - 확인: `python3 --version`

---

## 📦 프로젝트 클론

```bash
# 프로젝트 클론
git clone https://github.com/park6711/testpark.git
cd testpark

# 브랜치 확인
git branch -a
```

---

## 🔐 환경 변수 설정

### 1. `.env` 파일 생성

```bash
# 프로젝트 루트에 .env 파일 생성
cat > .env << 'EOF'
# Django 설정
DEBUG=True
SECRET_KEY=your-secret-key-here-change-in-production
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# 데이터베이스 설정 (MariaDB)
DB_ENGINE=django.db.backends.mysql
DB_NAME=testpark_db
DB_USER=testpark_user
DB_PASSWORD=testpark_password_2024
DB_HOST=mariadb
DB_PORT=3306

# MariaDB Root 설정
MYSQL_ROOT_PASSWORD=root_password_2024
MYSQL_DATABASE=testpark_db
MYSQL_USER=testpark_user
MYSQL_PASSWORD=testpark_password_2024

# 네이버 OAuth 설정 (실제 값으로 교체 필요)
NAVER_CLIENT_ID=your_naver_client_id
NAVER_CLIENT_SECRET=your_naver_client_secret

# 잔디 웹훅 (선택사항)
JANDI_WEBHOOK_URL=https://wh.jandi.com/connect-api/webhook/...

# 타임존 설정
TZ=Asia/Seoul
EOF
```

### 2. 중요 환경 변수 설명

| 변수명 | 설명 | 예시 값 |
|--------|------|---------|
| `DEBUG` | 디버그 모드 | `True` (개발), `False` (운영) |
| `DB_HOST` | DB 호스트 | `mariadb` (Docker), `localhost` (로컬) |
| `NAVER_CLIENT_ID` | 네이버 앱 ID | 네이버 개발자센터에서 발급 |
| `NAVER_CLIENT_SECRET` | 네이버 앱 시크릿 | 네이버 개발자센터에서 발급 |

---

## 🐳 Docker 환경 구성

### 1. Docker 서비스 확인

```bash
# Docker 실행 확인
docker --version
docker-compose --version

# Docker 서비스 상태 확인
docker info
```

### 2. Docker 이미지 빌드

```bash
# 개발 환경용 빌드
docker-compose -f docker-compose.dev.yml build

# 또는 기본 docker-compose.yml 사용
docker-compose build
```

### 3. 컨테이너 실행

```bash
# 백그라운드 실행
docker-compose up -d

# 로그 확인하며 실행
docker-compose up

# 특정 서비스만 실행
docker-compose up mariadb  # DB만
docker-compose up testpark  # Django만
```

---

## 🏃 개발 서버 실행

### 방법 1: Docker Compose 사용 (권장)

```bash
# 1. 전체 스택 실행
docker-compose up -d

# 2. 서비스 상태 확인
docker-compose ps

# 3. 로그 확인
docker-compose logs -f testpark  # Django 로그
docker-compose logs -f mariadb   # DB 로그

# 4. 브라우저에서 확인
# http://localhost:8000
```

### 방법 2: 로컬 Python 환경 (선택사항)

```bash
# 1. 가상환경 생성
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. 의존성 설치
pip install -r requirements.txt

# 3. DB 마이그레이션
python manage.py migrate

# 4. 개발 서버 실행
python manage.py runserver
```

---

## 💾 데이터베이스 초기화

### 1. MariaDB 컨테이너 접속

```bash
# MariaDB 컨테이너 접속
docker-compose exec mariadb mysql -u root -p
# 비밀번호: root_password_2024 (또는 .env의 MYSQL_ROOT_PASSWORD)
```

### 2. Django 마이그레이션

```bash
# 마이그레이션 파일 생성
docker-compose exec testpark python manage.py makemigrations

# 마이그레이션 적용
docker-compose exec testpark python manage.py migrate

# 슈퍼유저 생성
docker-compose exec testpark python manage.py createsuperuser
```

### 3. 초기 데이터 로드 (있는 경우)

```bash
# fixtures 로드
docker-compose exec testpark python manage.py loaddata initial_data.json
```

---

## 🔍 문제 해결

### 포트 충돌 문제

```bash
# 8000 포트 사용 중인 프로세스 확인
lsof -i :8000  # Mac/Linux
netstat -ano | findstr :8000  # Windows

# 3306 포트 (MariaDB) 확인
lsof -i :3306
```

### Docker 컨테이너 초기화

```bash
# 모든 컨테이너 중지 및 삭제
docker-compose down

# 볼륨까지 삭제 (데이터 초기화)
docker-compose down -v

# 이미지 재빌드
docker-compose build --no-cache
```

### 데이터베이스 연결 오류

```bash
# MariaDB 컨테이너 상태 확인
docker-compose ps mariadb
docker-compose logs mariadb

# 연결 테스트
docker-compose exec testpark python manage.py dbshell
```

### 권한 문제 (Linux/Mac)

```bash
# Docker 그룹에 사용자 추가
sudo usermod -aG docker $USER
newgrp docker
```

---

## 👨‍💻 개발 워크플로우

### 1. 일일 개발 시작

```bash
# 최신 코드 받기
git pull origin master

# Docker 컨테이너 시작
docker-compose up -d

# 마이그레이션 확인
docker-compose exec testpark python manage.py migrate
```

### 2. 코드 수정 후

```bash
# Django 컨테이너 재시작 (코드 변경 시)
docker-compose restart testpark

# 전체 재시작
docker-compose down && docker-compose up -d
```

### 3. 개발 종료

```bash
# 컨테이너 중지
docker-compose down

# 또는 일시 정지만
docker-compose stop
```

---

## 📊 상태 확인 명령어

```bash
# 실행 중인 컨테이너 확인
docker-compose ps

# 컨테이너 리소스 사용량
docker stats

# Django 쉘 접속
docker-compose exec testpark python manage.py shell

# MariaDB 쉘 접속
docker-compose exec mariadb mysql -u testpark_user -p

# 로그 확인 (실시간)
docker-compose logs -f --tail=100

# 헬스체크
curl http://localhost:8000/health/  # 헬스체크 엔드포인트가 있는 경우
```

---

## 🎯 빠른 시작 (Quick Start)

### 처음부터 끝까지 한 번에 실행

```bash
#!/bin/bash
# quick-start.sh

# 1. 프로젝트 클론
git clone https://github.com/park6711/testpark.git
cd testpark

# 2. .env 파일 생성 (위 템플릿 사용)
cp .env.example .env  # 또는 직접 생성

# 3. Docker 컨테이너 빌드 및 실행
docker-compose build
docker-compose up -d

# 4. 데이터베이스 초기화
sleep 10  # MariaDB 시작 대기
docker-compose exec testpark python manage.py migrate
docker-compose exec testpark python manage.py createsuperuser

# 5. 브라우저 열기
echo "✅ 개발 환경 구성 완료!"
echo "🌐 브라우저에서 http://localhost:8000 접속"
```

---

## 📚 추가 문서

- [Docker 가이드](./DOCKER_GUIDE.md)
- [디자인 가이드](./DESIGN_GUIDE.md)
- [API 문서](./API_GUIDE.md)
- [배포 가이드](./DEPLOYMENT_GUIDE.md)

---

## 🆘 지원

문제가 발생하면:
1. `docker-compose logs` 확인
2. GitHub Issues 생성: https://github.com/park6711/testpark/issues
3. 관리자 문의

---

> **Note**: 이 문서는 2025년 1월 기준으로 작성되었습니다.
> 최신 정보는 GitHub 저장소를 확인하세요.