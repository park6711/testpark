# 🌐 TestPark 실서버 네트워크 환경 구성

실서버(210.114.22.100)의 네트워크 환경 및 서비스 구성을 문서화합니다.

## 📊 서버 기본 정보

```
🏢 서버 정보
├── IP 주소: 210.114.22.100
├── 도메인: carpenterhosting.cafe24.com
├── OS: Linux 5.4.0-216-generic
├── 플랫폼: linux
└── 작업 디렉토리: /var/www/testpark
```

## 🔌 포트 구성

| 서비스 | 포트 | 프로토콜 | 설명 |
|--------|------|----------|------|
| Apache HTTP | 80 | HTTP | 웹 서버 (리버스 프록시) |
| Apache HTTPS | 443 | HTTPS | SSL 웹 서버 |
| TestPark Docker | 8000 | HTTP | Django 애플리케이션 |
| Webhook Docker | 8080 | HTTP | 배포 웹훅 서버 |
| MySQL | 3306 | TCP | 데이터베이스 |

## 🔄 리버스 프록시 구성

### Apache 설정 (/etc/apache2/sites-available/unified-vhost.conf)

```apache
# HTTP → HTTPS 리다이렉트
<VirtualHost *:80>
    ServerName carpenterhosting.cafe24.com
    Redirect permanent / https://carpenterhosting.cafe24.com/
</VirtualHost>

# HTTPS 메인 설정
<VirtualHost *:443>
    ServerName carpenterhosting.cafe24.com

    # SSL 설정
    SSLEngine on
    SSLCertificateFile /etc/letsencrypt/live/carpenterhosting.cafe24.com/fullchain.pem
    SSLCertificateKeyFile /etc/letsencrypt/live/carpenterhosting.cafe24.com/privkey.pem

    # 프록시 설정
    ProxyPreserveHost On
    ProxyRequests Off

    # TestPark 라우팅 (Docker 컨테이너)
    ProxyPass /auth/ http://localhost:8000/auth/
    ProxyPassReverse /auth/ http://localhost:8000/auth/

    # 웹훅 서버 라우팅 (Docker 컨테이너)
    ProxyPass /deploy http://localhost:8080/deploy
    ProxyPass /deploy-from-github http://localhost:8080/deploy-from-github
    ProxyPass /webhook/ http://localhost:8080/webhook/
    ProxyPass /health http://localhost:8080/health

    # intea 프로젝트 (WSGI)
    WSGIScriptAlias /intea /var/www/intea/intea_project/wsgi.py

    # PMIS 프로젝트 (WSGI)
    WSGIScriptAlias /PMIS /var/www/PMIS/PMIS/wsgi.py
</VirtualHost>
```

## 🐳 Docker 컨테이너 구성

### TestPark 메인 애플리케이션
```yaml
testpark:
  image: 7171man/testpark:latest
  container_name: testpark
  ports:
    - "8000:8000"
  restart: unless-stopped
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:8000/"]
    interval: 30s
    timeout: 10s
    retries: 3
    start_period: 40s
```

### 웹훅 서버
```yaml
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
  environment:
    - NODE_ENV=production
    - WEBHOOK_PORT=8080
    - WEBHOOK_SECRET=testpark-webhook-secret
```

## 🔗 URL 라우팅 맵

| URL 경로 | 대상 서비스 | 포트 | 설명 |
|----------|-------------|------|------|
| `/auth/*` | TestPark Docker | 8000 | 사용자 인증 (네이버 로그인) |
| `/deploy` | Webhook Docker | 8080 | 수동 배포 엔드포인트 |
| `/deploy-from-github` | Webhook Docker | 8080 | GitHub Actions 배포 |
| `/webhook/dockerhub` | Webhook Docker | 8080 | Docker Hub 웹훅 |
| `/health` | Webhook Docker | 8080 | 헬스체크 |
| `/intea/*` | intea WSGI | - | intea Django 프로젝트 |
| `/PMIS/*` | PMIS WSGI | - | PMIS Django 프로젝트 |

## 🔐 SSL/TLS 구성

```
📜 SSL 인증서
├── 인증서: /etc/letsencrypt/live/carpenterhosting.cafe24.com/fullchain.pem
├── 개인키: /etc/letsencrypt/live/carpenterhosting.cafe24.com/privkey.pem
├── 발급자: Let's Encrypt
└── 자동 갱신: certbot
```

## 🗄️ 데이터베이스 구성

```
🗄️ MySQL 설정
├── 포트: 3306
├── 데이터 디렉토리: /var/lib/mysql
├── 설정 파일: /etc/mysql/mysql.conf.d/mysqld.cnf
└── 사용 프로젝트: intea, PMIS, TestPark
```

## 🔄 배포 플로우

```
📱 GitHub Actions
    ↓ (webhook)
🌐 carpenterhosting.cafe24.com/deploy-from-github
    ↓ (Docker API)
🐳 TestPark 컨테이너 재시작
    ↓ (health check)
✅ 배포 완료 알림 (Jandi)
```

## 🔍 모니터링 및 헬스체크

### 서비스 상태 확인
```bash
# Docker 컨테이너 상태
docker-compose ps

# 웹 서비스 헬스체크
curl https://carpenterhosting.cafe24.com/health
curl https://carpenterhosting.cafe24.com/auth/login/

# Apache 상태
sudo systemctl status apache2

# MySQL 상태
sudo systemctl status mysql
```

### 로그 확인
```bash
# Docker 컨테이너 로그
docker-compose logs testpark --tail 20
docker-compose logs webhook --tail 20

# Apache 로그
sudo tail -f /var/log/apache2/access.log
sudo tail -f /var/log/apache2/error.log

# MySQL 로그
sudo tail -f /var/log/mysql/error.log
```

## 🚨 트러블슈팅

### 일반적인 문제 해결

1. **TestPark 접속 불가**
   ```bash
   # 컨테이너 상태 확인
   docker-compose ps testpark

   # 재시작
   docker-compose restart testpark
   ```

2. **웹훅 서버 오류**
   ```bash
   # 로그 확인
   docker-compose logs webhook

   # 재빌드 및 재시작
   docker-compose build webhook
   docker-compose up -d webhook
   ```

3. **Apache 프록시 오류**
   ```bash
   # 설정 테스트
   sudo apache2ctl configtest

   # 재시작
   sudo systemctl restart apache2
   ```

## 🔧 설정 파일 위치

| 서비스 | 설정 파일 위치 |
|--------|---------------|
| Apache | `/etc/apache2/sites-available/unified-vhost.conf` |
| Docker Compose | `/var/www/testpark/docker-compose.yml` |
| Webhook Dockerfile | `/var/www/testpark/webhook.Dockerfile` |
| 배포 스크립트 | `/var/www/testpark/scripts/deploy-docker.sh` |
| 웹훅 서버 | `/var/www/testpark/scripts/webhook-server-docker.js` |

## 📱 네이버 로그인 콜백 URL

- **로컬 개발**: `http://localhost:8001/auth/naver/callback/`
- **실서버**: `https://carpenterhosting.cafe24.com/auth/naver/callback/`

## 🌍 외부 서비스 연동

### Jandi 웹훅
- **URL**: `https://wh.jandi.com/connect-api/webhook/15016768/83760d2c508acfed35c1944e8a199f9b`
- **용도**: 배포 상태 알림

### Docker Hub
- **이미지**: `7171man/testpark:latest`
- **웹훅**: `https://carpenterhosting.cafe24.com/webhook/dockerhub`

---

*📝 이 문서는 실서버 환경 변경 시 업데이트해야 합니다.*