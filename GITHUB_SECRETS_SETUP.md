# GitHub Secrets 설정 완료 가이드

## 🔐 설정해야 할 GitHub Secrets

1. **GitHub 리포지토리 접속**
   - https://github.com/park6711/testpark/settings/secrets/actions

2. **New repository secret 클릭**

3. **다음 두 개의 Secret 추가:**

### Secret 1: DOCKER_USERNAME
- **Name**: `DOCKER_USERNAME`
- **Secret**: `7171man`

### Secret 2: DOCKER_PASSWORD
- **Name**: `DOCKER_PASSWORD`
- **Secret**: `[Docker Hub에서 생성한 Access Token 붙여넣기]`

## ✅ 설정 확인
- 두 개의 Secrets가 Repository secrets에 표시되면 완료!

## 📝 중요 사항
- 토큰은 한 번만 표시되므로 안전한 곳에 백업
- GitHub Actions는 자동으로 이 Secrets를 사용
- 로컬과 달리 GitHub Actions에서는 정상 작동 가능