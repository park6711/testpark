# TestPark 데이터베이스 동기화 가이드

## 📊 현재 MariaDB 상태

### 데이터베이스 정보
- **MariaDB 버전**: 11.2.6-MariaDB-ubu2204
- **컨테이너**: testpark-mariadb (포트 3306)
- **데이터베이스명**: testpark
- **볼륨**: testpark-mariadb-data (영구 저장)

### 접속 정보
```
호스트: localhost (또는 mariadb - Docker 네트워크 내부)
포트: 3306
사용자: testpark / root
비밀번호: testpark123 / testpark-root
데이터베이스: testpark
```

## 🔧 사용 가능한 스크립트

### 1. 데이터베이스 동기화 스크립트 (`scripts/sync-database.sh`)

주요 기능:
- 프로덕션 ↔ 로컬 간 데이터베이스 동기화
- 데이터베이스 백업 및 복원
- 데이터베이스 상태 확인

#### 사용법

```bash
# 데이터베이스 상태 확인
./scripts/sync-database.sh status

# 로컬 DB를 파일로 내보내기
./scripts/sync-database.sh export

# 덤프 파일을 로컬 DB로 가져오기
./scripts/sync-database.sh import ~/backup/testpark.sql

# 프로덕션 → 로컬 동기화 (프로덕션 데이터를 로컬로)
./scripts/sync-database.sh pull

# 로컬 → 프로덕션 동기화 (주의! 프로덕션 덮어씀)
./scripts/sync-database.sh push
```

### 2. 전체 백업 스크립트 (`scripts/backup.sh`)

데이터베이스뿐만 아니라 미디어 파일, 설정 파일 등 전체 백업

```bash
# 전체 백업 실행
./scripts/backup.sh

# 백업 위치: ~/backups/testpark_YYYYMMDD_HHMMSS/
```

### 3. 복원 스크립트 (`scripts/restore.sh`)

백업된 데이터 복원

```bash
# 백업 디렉토리로부터 복원
./scripts/restore.sh ~/backups/testpark_20241020_120000

# 압축 파일로부터 복원
./scripts/restore.sh ~/backups/testpark_backup_20241020_120000.tar.gz
```

### 4. DB 직접 접속 스크립트 (`scripts/db-connect.sh`)

MariaDB 콘솔로 직접 접속

```bash
# MariaDB 콘솔 접속
./scripts/db-connect.sh

# SQL 쿼리 직접 실행 예시
MariaDB [testpark]> SELECT COUNT(*) FROM `order`;
MariaDB [testpark]> SHOW TABLES;
MariaDB [testpark]> exit
```

## 📁 디렉토리 구조

```
/var/www/testpark/
├── scripts/
│   ├── sync-database.sh    # DB 동기화 전용
│   ├── backup.sh           # 전체 백업
│   ├── restore.sh          # 백업 복원
│   └── db-connect.sh       # DB 콘솔 접속
├── db-sync/               # 데이터베이스 덤프 파일 저장
│   └── testpark_local_*.sql
└── ~/backups/             # 전체 백업 저장
    └── testpark_backup_*.tar.gz
```

## 🔄 일반적인 작업 시나리오

### 시나리오 1: 로컬 개발 환경 설정

```bash
# 1. 프로덕션 데이터를 로컬로 가져오기
./scripts/sync-database.sh pull

# 2. 로컬에서 개발/테스트

# 3. 로컬 데이터 백업
./scripts/sync-database.sh export
```

### 시나리오 2: 데이터베이스 백업

```bash
# 빠른 DB만 백업
./scripts/sync-database.sh export

# 전체 백업 (미디어 파일 포함)
./scripts/backup.sh
```

### 시나리오 3: 문제 발생 시 복원

```bash
# 최근 백업으로 복원
./scripts/restore.sh ~/backups/testpark_backup_최신날짜.tar.gz

# 특정 DB 덤프로 복원
./scripts/sync-database.sh import /var/www/testpark/db-sync/testpark_local_특정날짜.sql
```

### 시나리오 4: 다른 개발자와 데이터 공유

```bash
# 1. 로컬 DB 내보내기
./scripts/sync-database.sh export

# 2. 생성된 파일 공유
# /var/www/testpark/db-sync/testpark_local_*.sql

# 3. 다른 개발자가 가져오기
./scripts/sync-database.sh import 받은파일.sql
```

## ⚠️ 주의사항

### 보안 관련
1. **프로덕션 데이터 취급 주의**: 실제 사용자 데이터가 포함될 수 있음
2. **백업 파일 보안**: 백업 파일에 민감한 정보 포함
3. **SSH 키 관리**: 프로덕션 서버 접근 시 SSH 키 필요

### Docker 관련
1. **컨테이너 실행 확인**: 작업 전 `docker ps` 로 상태 확인
2. **볼륨 관리**: `testpark-mariadb-data` 볼륨이 데이터 저장
3. **네트워크**: `testpark-network` 내에서 통신

### 동기화 관련
1. **push 명령 주의**: 프로덕션 데이터가 완전히 덮어씌워짐
2. **백업 우선**: 중요한 작업 전 항상 백업
3. **마이그레이션**: 동기화 후 Django 마이그레이션 자동 실행

## 🛠 문제 해결

### MariaDB 컨테이너가 실행되지 않을 때

```bash
# 컨테이너 시작
docker-compose up -d mariadb

# 로그 확인
docker-compose logs mariadb
```

### 동기화 실패 시

```bash
# 1. 컨테이너 상태 확인
docker ps

# 2. MariaDB 연결 테스트
docker exec testpark-mariadb mariadb -uroot -ptestpark-root -e "SELECT 1"

# 3. 볼륨 확인
docker volume ls | grep mariadb
```

### 백업 복원 실패 시

```bash
# 임시 백업 확인
ls -la /tmp/testpark_temp_backup_*

# 수동 복원
docker exec -i testpark-mariadb mariadb -uroot -ptestpark-root testpark < 백업파일.sql
```

## 📚 추가 명령어 참고

### Docker 관련

```bash
# 컨테이너 재시작
docker-compose restart mariadb

# 볼륨 정보 확인
docker volume inspect testpark-mariadb-data

# 컨테이너 내부 접속
docker exec -it testpark-mariadb bash
```

### MariaDB 관련

```bash
# 데이터베이스 크기 확인
docker exec testpark-mariadb mariadb -uroot -ptestpark-root -e "
SELECT table_schema AS 'Database',
       ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) AS 'Size (MB)'
FROM information_schema.tables
WHERE table_schema = 'testpark'
GROUP BY table_schema;"

# 테이블별 레코드 수 확인
docker exec testpark-mariadb mariadb -uroot -ptestpark-root testpark -e "
SELECT table_name, table_rows
FROM information_schema.tables
WHERE table_schema = 'testpark'
ORDER BY table_rows DESC;"
```

## 📞 지원

문제가 발생하거나 추가 도움이 필요한 경우:

1. 로그 확인: `docker-compose logs -f mariadb`
2. 스크립트 디버그 모드: `bash -x scripts/sync-database.sh status`
3. GitHub Issues에 문제 보고

---

*최종 업데이트: 2024년 10월 20일*