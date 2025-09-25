# Docker Hub 사용자명 확인 방법

## 🔎 정확한 Docker Hub 사용자명 확인하기

### 1. Docker Hub 웹사이트에서 확인
1. https://hub.docker.com 로그인
2. 우측 상단 프로필 아이콘 클릭
3. **사용자명 확인** (이메일 아래에 표시됨)
   - 보통 `@` 앞부분이 아닙니다!
   - 예: `7171man` 또는 `user7171` 등

### 2. Docker Hub 프로필 URL에서 확인
- 로그인 후 주소창 확인: `https://hub.docker.com/u/YOUR_USERNAME`

### 3. Access Token 권한 확인
1. Account Settings → Security
2. 생성한 토큰의 권한 확인:
   - ✅ Read
   - ✅ Write
   - ✅ Delete

## 일반적인 문제들:

| 문제 | 해결 방법 |
|------|-----------|
| 사용자명이 이메일과 다름 | Docker Hub에서 실제 사용자명 확인 |
| 토큰 복사 시 공백 포함 | 토큰 앞뒤 공백 제거 |
| 토큰 권한 부족 | Read, Write, Delete 모두 체크 |
| 토큰 만료 또는 삭제됨 | 새 토큰 생성 |

## 테스트 명령어

정확한 사용자명 확인 후:
```bash
# USERNAME을 실제 Docker Hub 사용자명으로 변경
echo 'YOUR_ACCESS_TOKEN' | docker login -u USERNAME --password-stdin
```