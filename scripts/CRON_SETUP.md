# Cron 스케줄링 설정 가이드

## Company 동기화 Cron 설정 (매일 18:00)

### 1. Crontab 열기
```bash
crontab -e
```

### 2. 다음 줄 추가
```
# Company Google Sheets 동기화 (매일 18:00)
0 18 * * * /var/www/testpark/scripts/sync_companies_cron.sh
```

### 3. 저장 및 종료
- vi/vim 에디터: `:wq` 입력 후 Enter
- nano 에디터: `Ctrl+O` → Enter → `Ctrl+X`

### 4. Crontab 확인
```bash
crontab -l
```

### 5. 로그 확인
```bash
# 최신 동기화 로그 확인
tail -f /var/log/testpark/company_sync_$(date +%Y%m%d).log

# 또는 모든 로그 파일 목록 보기
ls -lh /var/log/testpark/company_sync_*.log
```

## 수동 실행 (테스트용)

```bash
# 스크립트 직접 실행
/var/www/testpark/scripts/sync_companies_cron.sh

# 또는 Django Command 직접 실행
docker exec testpark python manage.py sync_companies
```

## 타임존 확인

서버 타임존이 KST(한국 시간)인지 확인:
```bash
timedatectl
# 또는
date
```

타임존이 다르면 cron 시간을 조정해야 합니다.

## 문제 해결

### Cron이 실행되지 않을 때
1. 스크립트 실행 권한 확인:
   ```bash
   ls -l /var/www/testpark/scripts/sync_companies_cron.sh
   ```
   `-rwxr-xr-x` 같은 실행 권한(`x`)이 있어야 함

2. 로그 디렉토리 권한 확인:
   ```bash
   ls -ld /var/log/testpark
   ```

3. Cron 서비스 상태 확인:
   ```bash
   systemctl status cron
   # 또는
   service cron status
   ```

### 로그가 생성되지 않을 때
```bash
# 로그 디렉토리 생성
sudo mkdir -p /var/log/testpark
sudo chmod 755 /var/log/testpark
```
