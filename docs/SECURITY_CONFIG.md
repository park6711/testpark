# 🔒 TestPark 보안 설정 가이드

TestPark 실서버의 네트워크 보안 및 IP 기반 접근 제어 설정 가이드입니다.

## 🔍 현재 보안 상태 분석

### 서버 정보
- **IP 주소**: 210.114.22.100
- **도메인**: carpenterhosting.cafe24.com
- **서버 유형**: 카페24 호스팅 (Ubuntu 기반)

### 현재 열린 포트
| 포트 | 서비스 | 접근 범위 | 보안 등급 |
|------|--------|-----------|-----------|
| 22 | SSH | 전체 IP | ⚠️ 위험 |
| 80 | HTTP (Apache) | 전체 IP | ✅ 필요 |
| 443 | HTTPS (Apache) | 전체 IP | ✅ 필요 |
| 8000 | TestPark Docker | 전체 IP | ⚠️ 내부용 |
| 8080 | 웹훅 서버 | 전체 IP | ⚠️ 내부용 |
| 5000 | 기타 서비스 | 전체 IP | ❌ 불필요 |
| 9000 | 기타 서비스 | 전체 IP | ❌ 불필요 |
| 5002 | 기타 서비스 | 전체 IP | ❌ 불필요 |
| 25565 | 미지 서비스 | 전체 IP | ❌ 불필요 |

## 🎯 보안 강화 계획

### 1단계: 불필요한 포트 닫기
```bash
# 불필요한 포트들 제거
sudo ufw delete allow 5000/tcp
sudo ufw delete allow 9000/tcp
sudo ufw delete allow 5002
sudo ufw delete allow 25565

# 규칙 적용
sudo ufw reload
```

### 2단계: 내부 서비스 접근 제한
```bash
# 8000, 8080 포트를 localhost만 접근 가능하도록 설정
sudo ufw delete allow 8000/tcp  # 기존 규칙 제거
sudo ufw delete allow 8080/tcp  # 기존 규칙 제거

# localhost만 접근 허용
sudo ufw allow from 127.0.0.1 to any port 8000
sudo ufw allow from 127.0.0.1 to any port 8080
```

### 3단계: SSH 접근 제한
```bash
# 특정 IP만 SSH 접근 허용 (예시)
sudo ufw delete allow 22/tcp  # 기존 규칙 제거

# 사무실/집 IP만 SSH 허용 (실제 IP로 변경 필요)
sudo ufw allow from 123.456.789.0/24 to any port 22
sudo ufw allow from 987.654.321.0/24 to any port 22
```

## 🛠️ 상세 설정 가이드

### Apache 웹서버 보안 설정

#### 1. 웹훅 엔드포인트 IP 제한
`/etc/apache2/sites-enabled/000-default.conf`에 추가:

```apache
# TestPark 웹훅 보안 설정
<Location "/deploy-from-github">
    # GitHub Actions IP 대역 허용
    Require ip 140.82.112.0/20
    Require ip 143.55.64.0/20
    Require ip 185.199.108.0/22
    Require ip 192.30.252.0/22
    Require ip 20.201.28.151/32
    # localhost 허용 (내부 테스트용)
    Require ip 127.0.0.1
    Require ip 210.114.22.100
</Location>

<Location "/webhook/dockerhub">
    # Docker Hub IP 대역 허용
    Require ip 52.1.0.0/16
    Require ip 52.5.0.0/16
    Require ip 34.192.0.0/10
    Require ip 54.0.0.0/8
    # localhost 허용
    Require ip 127.0.0.1
    Require ip 210.114.22.100
</Location>

<Location "/deploy">
    # 수동 배포는 내부에서만 허용
    Require ip 127.0.0.1
    Require ip 210.114.22.100
</Location>

# 관리자 접속 IP 제한 예시
<Location "/admin">
    # 사무실 IP만 허용 (실제 IP로 변경)
    Require ip 123.456.789.0/24
    Require ip 987.654.321.0/24
    Require ip 210.114.22.100
</Location>
```

#### 2. 일반 웹사이트 DDoS 방지
```apache
# DDoS 방지 설정
<IfModule mod_reqtimeout.c>
    RequestReadTimeout header=20-40,MinRate=500 body=20,MinRate=500
</IfModule>

<IfModule mod_limitipconn.c>
    ExtendedStatus On
    <Location />
        MaxConnPerIP 10
    </Location>
</IfModule>

# 특정 User-Agent 차단
<IfModule mod_rewrite.c>
    RewriteEngine On
    RewriteCond %{HTTP_USER_AGENT} ^.*(bot|crawler|spider).*$ [NC]
    RewriteRule .* - [F,L]
</IfModule>
```

### Fail2ban 설정 (침입 방지)

#### 설치 및 기본 설정
```bash
# Fail2ban 설치
sudo apt update
sudo apt install fail2ban

# 설정 파일 생성
sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local
```

#### 커스텀 설정
`/etc/fail2ban/jail.local`:
```ini
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 3
ignoreip = 127.0.0.1/8 210.114.22.100

[sshd]
enabled = true
port = 22
filter = sshd
logpath = /var/log/auth.log

[apache-auth]
enabled = true
port = http,https
filter = apache-auth
logpath = /var/log/apache2/error.log

[apache-badbots]
enabled = true
port = http,https
filter = apache-badbots
logpath = /var/log/apache2/access.log

[testpark-webhook]
enabled = true
port = 8080
filter = testpark-webhook
logpath = /var/log/webhook.log
maxretry = 5
bantime = 1800
```

### Docker 컨테이너 보안

#### 1. 네트워크 분리
```bash
# TestPark 전용 Docker 네트워크 생성
docker network create --driver bridge testpark-net

# 기존 컨테이너 중지 및 제거
docker stop testpark
docker rm testpark

# 보안 강화된 컨테이너 실행
docker run -d \
    --name testpark \
    --network testpark-net \
    --restart unless-stopped \
    -p 127.0.0.1:8000:8000 \
    --security-opt no-new-privileges:true \
    --read-only \
    --tmpfs /tmp \
    --tmpfs /var/tmp \
    7171man/testpark:latest
```

#### 2. 웹훅 서버 보안
`/var/www/testpark/scripts/webhook-server.js` 수정:
```javascript
// IP 화이트리스트 추가
const ALLOWED_IPS = [
    '127.0.0.1',           // localhost
    '210.114.22.100',      // 자기 자신
    '140.82.112.0/20',     // GitHub Actions
    '143.55.64.0/20',      // GitHub Actions
    '185.199.108.0/22',    // GitHub Actions
    '192.30.252.0/22',     // GitHub Actions
];

// IP 검증 미들웨어
app.use((req, res, next) => {
    const clientIP = req.ip || req.connection.remoteAddress;

    // IP 화이트리스트 체크 (간단한 예시)
    if (req.path.startsWith('/deploy') || req.path.startsWith('/webhook')) {
        // 실제 환경에서는 더 정교한 IP 검증 로직 필요
        console.log(`🔍 Webhook request from IP: ${clientIP}`);
    }
    next();
});
```

## 🚨 모니터링 및 알림 설정

### 1. 로그 모니터링
```bash
# 실시간 보안 로그 모니터링
sudo tail -f /var/log/auth.log | grep -E "(Failed|Invalid|BREAK-IN)"

# Apache 에러 로그 모니터링
sudo tail -f /var/log/apache2/error.log

# Fail2ban 상태 확인
sudo fail2ban-client status
```

### 2. 자동 알림 설정
```bash
#!/bin/bash
# /var/www/testpark/scripts/security-monitor.sh

# 의심스러운 접근 감지 시 Jandi 알림
JANDI_WEBHOOK="https://wh.jandi.com/connect-api/webhook/15016768/83760d2c508acfed35c1944e8a199f9b"

# SSH 무차별 대입 공격 감지
if [ $(grep "Failed password" /var/log/auth.log | grep "$(date '+%b %d')" | wc -l) -gt 10 ]; then
    curl -X POST "$JANDI_WEBHOOK" \
      -H "Content-Type: application/json" \
      -d '{
        "body": "🚨 보안 경고!\n\nSSH 무차별 대입 공격 감지\n서버: carpenterhosting.cafe24.com\n시간: '"$(date)"'\n\n즉시 확인이 필요합니다!",
        "connectColor": "#FF0000"
      }'
fi
```

### 3. cron 작업 등록
```bash
# crontab -e
# 매 10분마다 보안 모니터링
*/10 * * * * /var/www/testpark/scripts/security-monitor.sh
```

## 📋 IP 화이트리스트 관리

### 개발팀 IP 주소 관리
```bash
# 현재 등록된 IP 확인
sudo ufw status numbered

# 새 개발자 IP 추가
sudo ufw allow from 새로운IP주소 to any port 22 comment "개발자명-SSH"

# IP 제거
sudo ufw delete [번호]
```

### 외부 서비스 IP 대역
| 서비스 | IP 대역 | 용도 |
|--------|---------|------|
| GitHub Actions | 140.82.112.0/20, 143.55.64.0/20 등 | 자동 배포 |
| Docker Hub | 52.1.0.0/16, 34.192.0.0/10 등 | 웹훅 |
| 카페24 내부 | 210.114.22.0/24 | 내부 통신 |

## 🔧 정기 보안 점검

### 주간 점검 항목
- [ ] 방화벽 규칙 확인
- [ ] Fail2ban 로그 검토
- [ ] SSH 접근 로그 분석
- [ ] Docker 컨테이너 상태 점검
- [ ] 웹훅 접근 로그 검토

### 월간 점검 항목
- [ ] 불필요한 서비스 제거
- [ ] 시스템 업데이트 적용
- [ ] SSL 인증서 만료일 확인
- [ ] 백업 시스템 점검
- [ ] 비밀번호/키 교체

## ⚠️ 비상 대응 절차

### 1. 의심스러운 접근 감지 시
```bash
# 즉시 해당 IP 차단
sudo ufw insert 1 deny from 의심스러운IP

# 로그 확인
sudo grep "의심스러운IP" /var/log/apache2/access.log
sudo grep "의심스러운IP" /var/log/auth.log
```

### 2. 서비스 중단 시
```bash
# 웹훅 서버 중지
sudo systemctl stop webhook

# TestPark 컨테이너 중지
docker stop testpark

# Apache 중지 (최후 수단)
sudo systemctl stop apache2
```

### 3. 복구 절차
```bash
# 서비스 재시작
sudo systemctl start apache2
sudo systemctl start webhook
docker start testpark

# 정상 동작 확인
curl https://carpenterhosting.cafe24.com/health
```

## 📞 보안 연락처

- **긴급 상황**: 팀 내 보안 담당자
- **카페24 지원**: 카페24 고객센터
- **GitHub 보안**: GitHub Security Advisory

---

**⚠️ 중요**: 이 문서의 IP 주소와 보안 설정은 실제 환경에 맞게 수정해야 합니다. 설정 변경 전 반드시 백업을 생성하고, 단계적으로 적용하여 서비스 중단을 방지하세요.