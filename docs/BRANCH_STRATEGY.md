# 🌿 TestPark 다중 로컬 환경 브랜치 전략

TestPark 프로젝트의 다중 개발 환경에서 효율적인 협업을 위한 브랜치 전략 가이드입니다.

## 🖥️ 개발 환경 구성

### 로컬 개발 환경
- **샘맥북로컬1** (`sam-macbook`) - 메인 개발자 환경
- **루크맥북로컬2** (`luke-macbook`) - 서브 개발자 환경
- **루크윈도우로컬3** (`luke-windows`) - 테스트 및 검증 환경

### 서버 환경
- **실서버** (`carpenterhosting.cafe24.com`) - 프로덕션 환경 (210.114.22.100)

## 🔀 브랜치 전략 개요

### 메인 브랜치
- `master` - 프로덕션 배포용 메인 브랜치 (자동 배포 트리거)

### 개발 브랜치 네이밍 규칙
```
{작업자}/{작업내용}
```

#### 작업자 코드
- `sam` - 샘맥북로컬1
- `luke` - 루크맥북로컬2, 루크윈도우로컬3

#### 브랜치 명 예시
```bash
sam/user-authentication
luke/payment-integration
sam/login-bug-fix
luke/dashboard-update
sam/security-patch
```

## 📋 개발 워크플로우

### 1. 새 기능 개발 시작

```bash
# 1. 최신 master 브랜치 동기화
git checkout master
git pull origin master

# 2. 새 기능 브랜치 생성
git checkout -b sam/new-dashboard

# 3. 로컬에서 개발 진행
# ... 코딩 작업 ...

# 4. 변경사항 커밋
git add .
git commit -m "feat: 새로운 대시보드 UI 구현

- 대시보드 레이아웃 추가
- 실시간 데이터 표시 기능
- 반응형 디자인 적용"

# 5. 원격 브랜치에 푸시
git push origin sam/new-dashboard
```

### 2. Pull Request 생성 및 코드 리뷰

#### GitHub에서 PR 생성
```
제목: [Feature] 새로운 대시보드 UI 구현
베이스: master ← compare: sam/new-dashboard

설명:
## 변경 사항
- 대시보드 메인 페이지 구현
- 실시간 데이터 차트 추가
- 모바일 반응형 적용

## 테스트 완료
- [x] 로컬 테스트 (Sam 맥북)
- [x] 기능 테스트
- [x] UI/UX 검증

## 체크리스트
- [x] 코드 리뷰 요청
- [x] 테스트 케이스 통과
- [x] 문서 업데이트 (필요시)
```

### 3. 코드 리뷰 및 머지

#### 리뷰어 할당
- **메인 리뷰어**: 다른 팀원
- **서브 리뷰어**: 선택사항

#### 리뷰 체크리스트
- [ ] 코드 품질 확인
- [ ] 보안 이슈 검토
- [ ] 성능 영향 평가
- [ ] 테스트 커버리지 확인

#### 머지 후 처리
```bash
# PR 머지 후 로컬 정리
git checkout master
git pull origin master
git branch -d sam/new-dashboard
git push origin --delete sam/new-dashboard
```

## 🚀 배포 프로세스

### 자동 배포 트리거
1. **PR이 master에 머지됨**
2. **GitHub Actions 자동 실행**
   - Docker 이미지 빌드
   - Docker Hub 푸시
   - 웹훅을 통한 실서버 배포
3. **Jandi 알림으로 배포 상태 확인**
4. **실서버에서 수동 확인 필요**

### 배포 확인 절차
```bash
# 실서버 접속 후 확인
curl https://carpenterhosting.cafe24.com
docker ps -f name=testpark
docker logs testpark --tail 20
```

## 🔧 환경별 로컬 설정

### 공통 초기 설정
```bash
# 저장소 클론
git clone https://github.com/park6711/testpark.git
cd testpark

# 원격 브랜치 동기화
git fetch origin
git checkout master
```

### 샘맥북로컬1 설정
```bash
# 개발 환경 세팅
npm install
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Git 설정
git config user.name "Sam"
git config user.email "sam@team.com"

# 브랜치 생성 단축 명령 설정 (선택사항)
git config alias.new-branch '!f() { git checkout -b sam/$1; }; f'
```

### 루크맥북로컬2 설정
```bash
# 개발 환경 세팅 (맥 환경)
npm install
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Git 설정
git config user.name "Luke"
git config user.email "luke@team.com"

# 브랜치 생성 단축 명령 설정
git config alias.new-branch '!f() { git checkout -b luke/$1; }; f'
```

### 루크윈도우로컬3 설정
```bash
# 개발 환경 세팅 (Windows 환경)
npm install
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# Git 설정
git config user.name "Luke-Windows"
git config user.email "luke@team.com"

# 브랜치 생성 단축 명령 설정 (PowerShell)
git config alias.new-branch '!f() { git checkout -b luke/$1; }; f'
```

## 🎯 브랜치 사용 시나리오

### 시나리오 1: 새 기능 개발 (샘)
```bash
# 샘맥북로컬1에서
git new-branch user-profile-edit
# 실제 명령: git checkout -b sam/user-profile-edit

# 개발 진행...
git add .
git commit -m "feat: 사용자 프로필 편집 기능 추가"
git push origin sam/user-profile-edit

# GitHub에서 PR 생성 → 리뷰 → 머지 → 자동 배포
```

### 시나리오 2: 버그 수정 (루크 맥북)
```bash
# 루크맥북로컬2에서
git new-branch login-session-timeout
# 실제 명령: git checkout -b luke/login-session-timeout

# 버그 수정...
git add .
git commit -m "fix: 로그인 세션 타임아웃 문제 해결"
git push origin luke/login-session-timeout

# GitHub에서 PR 생성 → 리뷰 → 머지 → 자동 배포
```

### 시나리오 3: 크로스 플랫폼 테스트 (루크 윈도우)
```bash
# 루크윈도우로컬3에서
git checkout sam/user-profile-edit
git pull origin sam/user-profile-edit

# Windows 환경에서 테스트 진행
# 이슈 발견 시 별도 브랜치 생성
git checkout -b luke/windows-compatibility-fix

# 수정 후 커밋
git add .
git commit -m "fix: Windows 환경 호환성 문제 해결"
git push origin luke/windows-compatibility-fix
```

## 🚨 긴급 배포 (Hotfix)

### 프로덕션 긴급 수정 시
```bash
# 긴급 수정 브랜치 생성 (master에서 직접)
git checkout master
git pull origin master
git checkout -b sam/critical-security-fix

# 긴급 수정 진행
git add .
git commit -m "hotfix: 보안 취약점 긴급 수정"
git push origin sam/critical-security-fix

# GitHub에서 긴급 PR 생성
# 제목: [HOTFIX] 보안 취약점 긴급 수정
# 라벨: hotfix, critical
```

## 📊 브랜치 관리 모니터링

### 활성 브랜치 확인
```bash
# 로컬 브랜치 목록
git branch

# 원격 브랜치 목록
git branch -r

# 모든 브랜치 목록
git branch -a
```

### 브랜치 정리
```bash
# 머지된 브랜치 정리 (로컬)
git branch --merged | grep -v master | xargs git branch -d

# 원격 브랜치 정리
git remote prune origin
```

## 🔄 동기화 및 충돌 해결

### 정기적인 master 동기화
```bash
# 개발 중인 브랜치에서 master 변경사항 반영
git checkout feature/sam/current-work
git fetch origin
git rebase origin/master

# 충돌 발생 시
git status  # 충돌 파일 확인
# 수동으로 충돌 해결
git add .
git rebase --continue
```

### 충돌 해결 가이드라인
1. **충돌 표시 이해하기**
   ```
   <<<<<<< HEAD (현재 브랜치)
   현재 브랜치의 코드
   =======
   master 브랜치의 코드
   >>>>>>> master
   ```

2. **충돌 해결 후 확인**
   ```bash
   # 테스트 실행
   npm test
   python manage.py test

   # 로컬에서 동작 확인
   npm run dev
   python manage.py runserver
   ```

## 📱 Jandi 알림 설정

### 배포 관련 알림
- **빌드 성공**: GitHub Actions 빌드 완료
- **배포 시작**: 실서버 배포 프로세스 시작
- **배포 진행**: 중간 단계 진행 상황
- **배포 완료**: 최종 배포 완료 및 확인 요청
- **배포 실패**: 오류 발생 시 상세 로그

### 실서버 확인 필수
모든 배포 완료 후 반드시 실서버에서 직접 확인:
```bash
# 서비스 접속 테스트
curl https://carpenterhosting.cafe24.com

# 주요 기능 테스트
# - 로그인/로그아웃
# - 핵심 기능 동작
# - 새로 추가된 기능
```

## 📚 참고 자료

- [Git Flow 전략](https://nvie.com/posts/a-successful-git-branching-model/)
- [GitHub Flow 가이드](https://guides.github.com/introduction/flow/)
- [코드 리뷰 베스트 프랙티스](https://google.github.io/eng-practices/review/)

## 🤝 팀 협업 규칙

### 커밋 메시지 컨벤션
```
타입: 제목 (50자 이내)

본문 (선택사항, 72자로 줄바꿈)

푸터 (선택사항)
```

#### 타입 종류
- `feat`: 새로운 기능 추가
- `fix`: 버그 수정
- `docs`: 문서 수정
- `style`: 코드 스타일 변경 (포맷팅 등)
- `refactor`: 코드 리팩토링
- `test`: 테스트 추가/수정
- `hotfix`: 긴급 수정

### PR 리뷰 규칙
- **최소 1명 이상의 승인** 필요
- **자동 배포 전 테스트** 필수
- **브랜치 삭제**는 머지 후 자동/수동 처리
- **충돌 해결**은 PR 생성자가 담당

---

이 문서는 TestPark 팀의 효율적인 협업을 위한 가이드입니다. 문의사항이나 개선사항이 있으면 팀 내에서 논의 후 업데이트해주세요.