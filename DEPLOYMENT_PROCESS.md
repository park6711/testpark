# TestPark 배포 프로세스 가이드

## 📋 목차
1. [개요](#개요)
2. [배포 프로세스 흐름도](#배포-프로세스-흐름도)
3. [React 코드 변경 시](#react-코드-변경-시)
4. [Django 코드 변경 시](#django-코드-변경-시)
5. [정적 파일 처리](#정적-파일-처리)
6. [자동 배포 (CI/CD)](#자동-배포-cicd)
7. [수동 배포](#수동-배포)
8. [문제 해결](#문제-해결)

---

## 개요

TestPark 프로젝트는 GitHub Actions를 통한 자동 배포 시스템을 사용합니다.
코드 변경 후 Git push만 하면 자동으로 프로덕션 서버에 배포됩니다.

### 🏗️ 기술 스택
- **Frontend**: React (TypeScript)
- **Backend**: Django (Python)
- **Containerization**: Docker
- **CI/CD**: GitHub Actions
- **Production**: Docker Compose on Cafe24

---

## 배포 프로세스 흐름도

```
[로컬 개발] → [Git Push] → [GitHub Actions] → [Docker Hub] → [웹훅] → [프로덕션 서버]
     ↓           ↓              ↓                 ↓            ↓           ↓
코드 작성    커밋 & 푸시    자동 빌드       이미지 저장    배포 트리거   서비스 재시작
```

---

## React 코드 변경 시

### 1. 개발 및 테스트
```bash
# 개발 서버 실행
cd frontend
npm start

# 테스트
npm test
```

### 2. 프로덕션 빌드 테스트
```bash
# 로컬에서 빌드 테스트
npm run build

# 빌드 파일 확인
ls -la build/static/js/
```

### 3. Git 커밋 및 푸시
```bash
# 변경 파일 확인
git status

# 스테이징
git add frontend/src/

# 커밋
git commit -m "feat: React 컴포넌트 수정"

# 푸시
git push origin master
```

### ⚠️ React 빌드 주의사항
- **Chunk 파일**: 빌드할 때마다 파일명이 변경됩니다 (캐시 무효화)
- **정적 파일 경로**: `/static/js/`, `/static/css/`로 자동 복사됩니다
- **템플릿 업데이트**: react_app.html의 JS 파일명은 자동으로 처리됩니다

---

## Django 코드 변경 시

### 1. 개발 및 테스트
```bash
# 개발 서버 실행
python manage.py runserver

# 마이그레이션 (모델 변경 시)
python manage.py makemigrations
python manage.py migrate

# 테스트
python manage.py test
```

### 2. 정적 파일 수집 (필요시)
```bash
python manage.py collectstatic --noinput
```

### 3. Git 커밋 및 푸시
```bash
# 변경 파일 확인
git status

# 스테이징
git add .

# 커밋
git commit -m "fix: Django 뷰 로직 수정"

# 푸시
git push origin master
```

---

## 정적 파일 처리

### 📁 디렉토리 구조
```
/app/
├── static/           # 개발용 정적 파일
├── staticfiles/      # 프로덕션용 수집된 정적 파일
│   ├── admin/        # Django Admin 파일
│   ├── css/          # CSS 파일 (React 빌드 포함)
│   ├── js/           # JS 파일 (React chunk 파일 포함)
│   └── react/        # React 앱 전체
└── media/            # 업로드 파일
```

### 🔄 Dockerfile 처리 순서 (중요!)
1. Django 프로젝트 복사
2. `collectstatic --clear` 실행 (Django 정적 파일 수집)
3. React 빌드 파일 복사 (이후에 복사하여 삭제 방지)
4. 권한 설정

```dockerfile
# 올바른 순서
RUN python manage.py collectstatic --noinput --clear || true
COPY --from=frontend-builder /frontend/build/static /app/staticfiles/
```

---

## 자동 배포 (CI/CD)

### GitHub Actions 워크플로우

1. **트리거**: master 브랜치 push
2. **빌드**: Docker 이미지 생성
3. **푸시**: Docker Hub에 업로드
4. **배포**: 웹훅으로 실서버 트리거

### 📊 진행 상태
- 0% - 배포 시작
- 20% - Docker 빌드
- 40% - Docker Hub 푸시
- 60% - 웹훅 트리거
- 80% - 실서버 컨테이너 재시작
- 100% - 배포 완료

### 🔔 Jandi 알림
각 단계별로 Jandi 메신저에 자동 알림이 전송됩니다.

---

## 수동 배포

### 1. Docker 이미지 빌드
```bash
# 로컬에서 이미지 빌드
docker build -t 7171man/testpark:latest .
```

### 2. Docker Hub 푸시
```bash
# Docker Hub 로그인
docker login

# 이미지 푸시
docker push 7171man/testpark:latest
```

### 3. 프로덕션 서버 배포
```bash
# 배포 스크립트 실행
bash scripts/deploy-docker.sh
```

---

## 문제 해결

### ❌ React Chunk 파일 404 에러
**증상**: `Loading chunk 459 failed (404)`

**원인**: collectstatic이 React 빌드 파일을 삭제

**해결**:
1. Dockerfile에서 collectstatic 순서 확인
2. React 빌드 파일이 collectstatic 이후에 복사되는지 확인

### ❌ 화면 너비가 좁게 보임
**증상**: 의뢰리스트가 1200px로 제한됨

**원인**: Django base.html의 CSS 제약

**해결**:
```css
/* react_app.html에 추가 */
.content-wrapper {
    max-width: none !important;
}
```

### ❌ GitHub Actions 빌드 실패
**증상**: Docker 빌드 중 실패

**확인 방법**:
```bash
# GitHub Actions 로그 확인
gh run list --repo park6711/testpark
gh run view [RUN_ID] --log-failed
```

**일반적인 원인**:
- Dockerfile 문법 오류
- COPY 경로 오류
- 의존성 설치 실패

### ❌ 프로덕션 배포 후 변경사항이 반영되지 않음
**원인**: 브라우저 캐시

**해결**:
- 강제 새로고침: `Ctrl + F5` (Windows) / `Cmd + Shift + R` (Mac)
- 브라우저 개발자 도구 → Network → Disable cache

---

## 📝 체크리스트

### React 변경 시
- [ ] npm run build 성공 확인
- [ ] chunk 파일 생성 확인
- [ ] Git 커밋 메시지 작성
- [ ] Git push
- [ ] GitHub Actions 성공 확인
- [ ] 프로덕션 사이트 확인

### Django 변경 시
- [ ] 마이그레이션 필요 여부 확인
- [ ] collectstatic 필요 여부 확인
- [ ] Git 커밋 메시지 작성
- [ ] Git push
- [ ] GitHub Actions 성공 확인
- [ ] 프로덕션 사이트 확인

### Dockerfile 변경 시
- [ ] 로컬 Docker 빌드 테스트
- [ ] collectstatic 순서 확인
- [ ] COPY 경로 검증
- [ ] Git push
- [ ] GitHub Actions 모니터링

---

## 📞 문제 발생 시

1. **GitHub Actions 로그 확인**
   - https://github.com/park6711/testpark/actions

2. **Jandi 알림 확인**
   - 어느 단계에서 실패했는지 확인

3. **수동 배포 시도**
   - scripts/deploy-docker.sh 실행

4. **Docker 로그 확인**
   ```bash
   docker-compose logs testpark --tail 100
   ```

---

*마지막 업데이트: 2024-09-26*