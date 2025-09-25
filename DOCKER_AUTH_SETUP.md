# Docker Hub 인증 설정 가이드

⚠️ **중요**: Docker Hub는 CLI 로그인 시 비밀번호가 아닌 Access Token을 요구합니다!

## 🔐 Docker Hub Access Token 생성 (필수!)

### 1단계: Docker Hub 웹사이트 로그인
1. https://hub.docker.com 접속
2. 이메일: `7171man@naver.com`
3. 비밀번호: `*jeje4211`

### 2단계: Access Token 생성
1. 우측 상단 프로필 클릭 → **Account Settings**
2. 왼쪽 메뉴에서 **Security** 클릭
3. **New Access Token** 버튼 클릭
4. 설정:
   - **Token description**: `testpark-github-actions`
   - **Access permissions**: `Read, Write, Delete` 모두 체크
5. **Generate** 클릭
6. 🚨 **생성된 토큰을 반드시 복사!** (한 번만 표시됨)

### 3단계: 로컬에서 토큰으로 로그인 테스트
```bash
# 복사한 토큰으로 로그인
echo "YOUR_COPIED_TOKEN" | docker login -u 7171man --password-stdin
```

성공 시:
```
WARNING! Your password will be stored unencrypted in /root/.docker/config.json.
Login Succeeded
```

## GitHub Secrets 설정 방법

1. **GitHub 리포지토리로 이동**
   - https://github.com/park6711/testpark

2. **Settings > Secrets and variables > Actions 클릭**

3. **다음 Secret 추가/수정:**

   ### DOCKER_USERNAME
   - Name: `DOCKER_USERNAME`
   - Value: `7171man`

   ### DOCKER_PASSWORD
   - Name: `DOCKER_PASSWORD`
   - Value: Docker Hub 계정의 **액세스 토큰** (비밀번호 대신)

## Docker Hub Access Token 생성 방법

1. Docker Hub 로그인: https://hub.docker.com
2. Account Settings > Security
3. "New Access Token" 클릭
4. Token 이름: `github-actions-testpark`
5. Access permissions: `Read & Write`
6. Generate 클릭
7. 생성된 토큰을 복사하여 GitHub Secret에 저장

## 테스트 방법

```bash
# 로컬에서 토큰으로 로그인 테스트
echo "YOUR_ACCESS_TOKEN" | docker login -u 7171man --password-stdin

# 성공 시
Login Succeeded
```

## 대안: Personal Access Token 사용

Docker Hub 비밀번호 대신 Personal Access Token을 사용하면 더 안전하고 안정적입니다.

## 문제 해결

### 에러: unauthorized: authentication required
- Docker Hub 계정 확인
- Access Token 재생성
- GitHub Secrets 오타 확인

### 에러: rate limit exceeded
- Docker Hub 무료 계정: 6시간당 100 pull 제한
- 해결: Docker Hub Pro 구독 또는 캐시 활용