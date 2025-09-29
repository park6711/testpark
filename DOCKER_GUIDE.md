# TestPark Docker 구성 가이드

## 🎯 상황별 실행 방법

### 1. 일반 개발 (백엔드 작업)
```bash
# MariaDB + Django만 실행 (가장 가벼움)
docker-compose up -d mariadb testpark
```

### 2. React 개발 (프론트엔드 작업)
```bash
# Hot-reload가 필요한 경우
docker-compose up -d mariadb testpark frontend

# React 개발서버: http://localhost:3000
# Django API: http://localhost:8000
```

### 3. 프로덕션 배포
```bash
# 모든 서비스 실행
docker-compose -f docker-compose.prod.yml up -d
```

## 📊 리소스 사용량

| 구성 | RAM 사용 | CPU 사용 | 설명 |
|-----|---------|---------|------|
| 최소 (DB+Django) | ~800MB | 낮음 | 일반 개발용 |
| 개발 (DB+Django+React) | ~1.5GB | 보통 | React 개발용 |
| 전체 (모든 서비스) | ~2GB | 보통 | 프로덕션용 |

## 🛠️ 유용한 명령어

```bash
# 실행 중인 컨테이너 확인
docker-compose ps

# 특정 서비스만 재시작
docker-compose restart testpark

# 로그 확인
docker-compose logs -f testpark

# 모든 컨테이너 중지
docker-compose down

# 컨테이너와 볼륨 모두 삭제 (주의!)
docker-compose down -v
```

## 💭 자주 묻는 질문

**Q: 왜 여러 컨테이너를 사용하나요?**
- A: 각 서비스를 독립적으로 관리하고 확장할 수 있습니다.

**Q: 개발 시 frontend 컨테이너가 꼭 필요한가요?**
- A: 아니요. React 빌드 파일이 Django에 포함되어 있어 선택사항입니다.

**Q: webhook 컨테이너는 언제 필요한가요?**
- A: GitHub 푸시 시 자동 배포가 필요한 프로덕션 환경에서만 필요합니다.