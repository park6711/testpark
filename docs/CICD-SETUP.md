# CI/CD 설정 가이드

TestPark 프로젝트의 자동 배포 시스템 설정 방법을 안내합니다.

## 🔧 설정 단계

### 1. GitHub Actions Secrets 설정

GitHub 저장소 Settings > Secrets and variables > Actions에서 다음 secrets을 추가하세요:

```
DOCKER_USERNAME=7171man
DOCKER_PASSWORD=your_docker_hub_password
PROD_HOST=your_production_server_ip
PROD_USER=your_server_username
PROD_SSH_KEY=your_private_ssh_key
```

### 2. 실서버 Docker 설치

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install docker.io docker-compose
sudo systemctl start docker
sudo systemctl enable docker

# 사용자를 docker 그룹에 추가 (선택사항)
sudo usermod -aG docker $USER
```

### 3. Webhook 서버 설정

실서버에서 webhook 서버를 systemd 서비스로 등록:

```bash
# 서비스 파일 복사
sudo cp /var/www/testpark/scripts/webhook.service /etc/systemd/system/

# 서비스 활성화 및 시작
sudo systemctl daemon-reload
sudo systemctl enable testpark-webhook
sudo systemctl start testpark-webhook

# 상태 확인
sudo systemctl status testpark-webhook
```

### 4. GitHub Webhook 설정

1. GitHub 저장소 Settings > Webhooks > Add webhook
2. Payload URL: `http://your-server-ip:8080/webhook/github`
3. Content type: `application/json`
4. Secret: `testpark-webhook-secret`
5. Events: `Just the push event`

### 5. Docker Hub Webhook 설정 (선택사항)

1. Docker Hub 저장소 > Webhooks
2. Webhook name: `testpark-auto-deploy`
3. Webhook URL: `http://your-server-ip:8080/webhook/dockerhub`

## 🚀 배포 방법

### 자동 배포
- `master` 브랜치에 push하면 자동으로 배포됩니다
- GitHub Actions가 Docker 이미지를 빌드하고 배포합니다

### 수동 배포

```bash
# 실서버에서 직접 실행
bash /var/www/testpark/scripts/deploy.sh

# 또는 웹 엔드포인트 호출
curl -X POST http://localhost:8080/deploy
```

## 📊 모니터링

### 애플리케이션 상태 확인
```bash
# 컨테이너 상태
docker ps -f name=testpark

# 애플리케이션 헬스 체크
curl http://localhost:3000/health

# Webhook 서버 상태
curl http://localhost:8080/health
```

### 로그 확인
```bash
# 애플리케이션 로그
docker logs testpark

# Webhook 서버 로그
sudo journalctl -u testpark-webhook -f

# GitHub Actions 로그
GitHub Actions 탭에서 확인
```

## 🔒 보안 고려사항

1. **SSH 키 보안**: GitHub Secrets에 저장된 SSH 키는 읽기 전용으로 설정
2. **Webhook Secret**: 강력한 secret 사용
3. **방화벽**: webhook 포트(8080)는 GitHub/Docker Hub IP만 허용
4. **HTTPS**: 프로덕션에서는 HTTPS 사용 권장

## 🛠️ 트러블슈팅

### 일반적인 문제들

1. **배포 실패**
   ```bash
   # 로그 확인
   docker logs testpark
   sudo journalctl -u testpark-webhook -f
   ```

2. **Webhook 응답 없음**
   ```bash
   # 서비스 재시작
   sudo systemctl restart testpark-webhook

   # 포트 확인
   netstat -tlnp | grep 8080
   ```

3. **Docker 권한 오류**
   ```bash
   # Docker 그룹 추가
   sudo usermod -aG docker $USER
   newgrp docker
   ```

## 📈 추가 개선사항

- [ ] 블루-그린 배포 구현
- [ ] 롤백 기능 추가
- [ ] 모니터링 대시보드 구축
- [ ] 자동 백업 시스템
- [ ] 성능 테스트 자동화