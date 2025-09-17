# 로컬 개발환경 구성 가이드

## 🖥️ 노트북에서 개발환경 설정하기

### 1단계: 필수 프로그램 설치

```bash
# 노트북에 설치 필요한 프로그램들
1. Docker Desktop
2. Git
3. VS Code (또는 선호하는 IDE)
4. GitHub Desktop (선택사항)
```

### 2단계: 프로젝트 클론

```bash
# 노트북에서 실행
git clone https://github.com/park6711/testpark.git
cd testpark
```

### 3단계: 로컬에서 Docker로 개발

```bash
# 로컬에서 Django 개발 서버 실행
docker build -t testpark-local .
docker run -d --name testpark-dev -p 8000:8000 -v $(pwd):/app testpark-local

# 로컬 접속: http://localhost:8000
```

### 4단계: 코드 수정 및 테스트

```bash
# 코드 수정 후
1. VS Code에서 Django 코드 수정
2. 로컬 브라우저에서 http://localhost:8000 확인
3. 테스트 완료 후 GitHub에 push
```

## 🔄 **개발 사이클**

```
노트북에서 코드 수정
    ↓
로컬 Docker에서 테스트
    ↓
GitHub에 push
    ↓ (자동)
GitHub Actions 실행
    ↓ (자동)
Docker Hub 업로드
    ↓ (자동)
카페24 실서버 자동 배포
    ↓
http://210.114.22.100:8000 확인
```

## 🎯 **핵심 포인트**

### ✅ **이미 완료된 것들**
- 카페24 실서버 Django 실행 ✅
- GitHub 저장소 연결 ✅
- Docker Hub 설정 ✅
- CI/CD 파이프라인 ✅

### 📝 **앞으로 해야 할 것들**
1. **노트북에 Docker Desktop 설치**
2. **프로젝트 클론**
3. **로컬 개발환경 구성**
4. **개발 → 테스트 → 배포 사이클 익히기**

## 💡 **개발 팁**

### **로컬 개발 명령어들**
```bash
# 컨테이너 상태 확인
docker ps

# 로그 확인
docker logs testpark-dev

# 컨테이너 접속 (Django 명령어 실행)
docker exec -it testpark-dev bash

# Django 관리자 생성
docker exec -it testpark-dev python manage.py createsuperuser

# 새 앱 생성
docker exec -it testpark-dev python manage.py startapp myapp
```

### **코드 동기화**
```bash
# 변경사항 GitHub에 올리기
git add .
git commit -m "기능 추가: ..."
git push origin master

# → 자동으로 실서버에 배포됨!
```

## 🎮 **다음 단계별 실습**

### **Step 1: 노트북 환경 준비**
- Docker Desktop 설치
- Git 설치
- 프로젝트 클론

### **Step 2: 첫 코드 수정 테스트**
- 간단한 페이지 추가
- 로컬에서 확인
- GitHub에 push
- 실서버 자동 배포 확인

### **Step 3: 본격적인 개발**
- Django 앱 생성
- 모델, 뷰, 템플릿 개발
- 데이터베이스 설정

이제 **노트북에서 편안하게 개발하고, GitHub에 push만 하면 자동으로 실서버에 배포**되는 환경이 완성되었습니다! 🚀