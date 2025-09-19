# 🐳 TestPark Docker 기반 아키텍처 설계

현재 혼재된 실행 환경을 Docker로 통일하여 관리 효율성을 극대화하는 방안입니다.

## 🔍 현재 상황 분석

### 기존 아키텍처 (혼재형)
```
📦 현재 실서버 구성
├── 🌐 Apache (포트 80/443) - 리버스 프록시
│   ├── /intea → WSGI (Python Django)
│   ├── /PMIS → WSGI (Python Django)
│   ├── /auth → Docker:8000 (TestPark)
│   └── /deploy* → Node.js:8080 (웹훅 서버)
├── 🐳 TestPark (Docker 컨테이너)
├── 🟢 웹훅 서버 (Node.js 직접 실행)
├── 🐍 intea (Apache WSGI)
├── 🐍 PMIS (Apache WSGI)
└── 🗄️ MySQL (직접 설치)
```

### 문제점
- ❌ **관리 복잡성**: 서비스마다 다른 배포/관리 방식
- ❌ **환경 불일치**: 로컬 vs 프로덕션 환경 차이
- ❌ **스케일링 어려움**: 개별 서비스 확장 제약
- ❌ **의존성 충돌**: 시스템 레벨 패키지 충돌 가능성
- ❌ **백업/복구 복잡**: 여러 서비스의 개별 관리 필요

## 🎯 목표 아키텍처 (Docker 통일)

### 완전 컨테이너화 구성
```
🐳 Docker 기반 마이크로서비스
├── 🔄 Nginx Proxy (컨테이너) - 포트 80/443
│   ├── /testpark → testpark:8000
│   ├── /intea → intea:8001
│   ├── /pmis → pmis:8002
│   └── /webhook → webhook:8080
├── 📱 testpark (기존 컨테이너)
├── 🔗 webhook-server (신규 컨테이너)
├── 🏛️ intea (신규 컨테이너)
├── 🏢 pmis (신규 컨테이너)
└── 🗄️ mysql (컨테이너)
```

### 장점
- ✅ **통일된 관리**: Docker Compose 하나로 모든 서비스 관리
- ✅ **환경 일관성**: 로컬/스테이징/프로덕션 동일 환경
- ✅ **쉬운 스케일링**: 서비스별 독립적 확장
- ✅ **격리된 환경**: 서비스 간 의존성 충돌 방지
- ✅ **간편한 백업**: 볼륨 기반 데이터 관리

## 📋 마이그레이션 계획

### Phase 1: 웹훅 서버 컨테이너화
```dockerfile
# webhook-server/Dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY scripts/ ./scripts/
RUN chmod +x scripts/deploy.sh
EXPOSE 8080
CMD ["node", "scripts/webhook-server.js"]
```

### Phase 2: intea/PMIS 컨테이너화
```dockerfile
# intea/Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8001
CMD ["gunicorn", "--bind", "0.0.0.0:8001", "intea_project.wsgi:application"]
```

### Phase 3: Nginx 프록시 컨테이너
```nginx
# nginx/nginx.conf
upstream testpark {
    server testpark:8000;
}
upstream webhook {
    server webhook:8080;
}
upstream intea {
    server intea:8001;
}

server {
    listen 80;
    server_name carpenterhosting.cafe24.com;

    location /auth/ {
        proxy_pass http://testpark;
    }
    location /deploy {
        proxy_pass http://webhook;
    }
    location /intea/ {
        proxy_pass http://intea;
    }
}
```

### Phase 4: Docker Compose 통합
```yaml
# docker-compose.yml
version: '3.8'
services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx:/etc/nginx/conf.d
      - ./ssl:/etc/ssl
    depends_on:
      - testpark
      - webhook
      - intea

  testpark:
    image: 7171man/testpark:latest
    expose:
      - "8000"
    restart: unless-stopped

  webhook:
    build: ./webhook-server
    expose:
      - "8080"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    restart: unless-stopped

  intea:
    build: ./intea
    expose:
      - "8001"
    depends_on:
      - mysql
    restart: unless-stopped

  mysql:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD}
    volumes:
      - mysql_data:/var/lib/mysql
    restart: unless-stopped

volumes:
  mysql_data:
```

## 🚀 마이그레이션 실행 계획

### 1단계: 준비 작업 (무중단)
```bash
# 1. 현재 상태 백업
sudo systemctl stop webhook
sudo systemctl stop apache2
sudo mysqldump --all-databases > backup.sql

# 2. Docker Compose 환경 구성
mkdir -p /var/www/testpark-docker/{nginx,webhook-server,intea,pmis}
cd /var/www/testpark-docker
```

### 2단계: 웹훅 서버 컨테이너화
```bash
# 웹훅 서버 Docker 이미지 빌드
docker build -t testpark-webhook ./webhook-server

# 테스트 실행
docker run -d --name webhook-test -p 8081:8080 testpark-webhook

# 기능 테스트 후 기존 서비스 교체
sudo systemctl stop webhook
docker run -d --name webhook -p 8080:8080 testpark-webhook
```

### 3단계: Django 서비스 컨테이너화
```bash
# intea 컨테이너화
docker build -t testpark-intea ./intea
docker run -d --name intea -p 8001:8001 testpark-intea

# PMIS 컨테이너화
docker build -t testpark-pmis ./pmis
docker run -d --name pmis -p 8002:8002 testpark-pmis
```

### 4단계: Nginx 프록시 교체
```bash
# Nginx 컨테이너 실행
docker run -d --name nginx \
  -p 80:80 -p 443:443 \
  -v ./nginx:/etc/nginx/conf.d \
  -v ./ssl:/etc/ssl \
  nginx:alpine

# Apache 중지
sudo systemctl stop apache2
sudo systemctl disable apache2
```

### 5단계: 최종 검증 및 정리
```bash
# 서비스 상태 확인
curl https://carpenterhosting.cafe24.com/auth/login/
curl https://carpenterhosting.cafe24.com/health
curl https://carpenterhosting.cafe24.com/intea/
curl https://carpenterhosting.cafe24.com/pmis/

# 네이버 로그인 테스트
curl -I https://carpenterhosting.cafe24.com/auth/naver/callback/

# 배포 테스트
curl -X POST https://carpenterhosting.cafe24.com/deploy
```

## 📊 성능 및 리소스 최적화

### 컨테이너 리소스 제한
```yaml
services:
  testpark:
    image: 7171man/testpark:latest
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: '0.5'
        reservations:
          memory: 256M
          cpus: '0.25'
```

### 모니터링 추가
```yaml
  monitoring:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring:/etc/prometheus

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
```

## 🔒 보안 강화

### 네트워크 분리
```yaml
networks:
  frontend:
    driver: bridge
  backend:
    driver: bridge
    internal: true

services:
  nginx:
    networks:
      - frontend

  testpark:
    networks:
      - frontend
      - backend

  mysql:
    networks:
      - backend
```

### 시크릿 관리
```yaml
secrets:
  mysql_root_password:
    file: ./secrets/mysql_root_password.txt
  naver_client_secret:
    file: ./secrets/naver_client_secret.txt

services:
  mysql:
    secrets:
      - mysql_root_password
    environment:
      MYSQL_ROOT_PASSWORD_FILE: /run/secrets/mysql_root_password
```

## 🎯 예상 효과

### 운영 효율성
- **배포 시간**: 5-10분 → **2-3분**
- **롤백 시간**: 10-15분 → **30초**
- **스케일링**: 수동 설정 → **자동화**
- **모니터링**: 개별 확인 → **통합 대시보드**

### 개발 생산성
- **로컬 환경 구성**: 1-2시간 → **5분**
- **환경 일관성**: 70% → **100%**
- **디버깅**: 복잡 → **단순화**

## 🚨 리스크 및 대응

### 잠재적 위험
- **다운타임**: 마이그레이션 중 일시적 서비스 중단
- **설정 누락**: 기존 환경 변수/설정 누락
- **성능 차이**: 컨테이너 오버헤드

### 대응 방안
- **블루-그린 배포**: 새 환경 구성 후 트래픽 전환
- **설정 체크리스트**: 모든 환경변수/설정 문서화
- **성능 테스트**: 부하 테스트로 성능 검증

---

**🤔 Docker 통일 마이그레이션을 진행하시겠습니까?**

현재 Apache 설정이 잘 동작하고 있으니, 단계적으로 마이그레이션하거나 현재 상태를 유지하는 것도 좋은 선택입니다.