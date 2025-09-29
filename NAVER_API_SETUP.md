# 네이버 카페 자동 게시 설정 가이드

## 🚀 빠른 시작 (이미 API 등록된 경우)

### 1. 액세스 토큰 설정

이미 네이버 로그인과 카페 API가 등록되어 있고 토큰을 보유하고 있다면:

```bash
# Docker 컨테이너 접속
docker-compose exec testpark bash

# 액세스 토큰 설정
python manage.py naver_token --set "YOUR_ACCESS_TOKEN"

# 토큰 확인
python manage.py naver_token --show

# 테스트 게시
python manage.py naver_token --test
```

### 2. 환경 변수 설정 (선택사항)

`docker-compose.yml` 파일에 추가:

```yaml
services:
  testpark:
    environment:
      - NAVER_CLIENT_ID=YOUR_CLIENT_ID
      - NAVER_CLIENT_SECRET=YOUR_CLIENT_SECRET
```

또는 `.env` 파일 생성:

```
NAVER_CLIENT_ID=YOUR_CLIENT_ID
NAVER_CLIENT_SECRET=YOUR_CLIENT_SECRET
```

## 📋 전체 설정 프로세스

### 1. 네이버 개발자센터 설정

1. [네이버 개발자센터](https://developers.naver.com/apps/) 접속
2. **애플리케이션 등록** 또는 기존 앱 선택
3. **사용 API** 설정:
   - ✅ 네이버 로그인
   - ✅ 카페

### 2. API 권한 설정

**네이버 로그인 설정:**
- 서비스 URL: `https://your-domain.com`
- 네이버 로그인 Callback URL: `https://your-domain.com/api/naver/callback`

**카페 API 설정:**
- 카페 가입 및 글쓰기 권한 필요

### 3. 토큰 획득

#### 방법 1: 수동으로 토큰 획득

1. 로그인 URL 생성:
```bash
python manage.py naver_token --auth-url
```

2. 생성된 URL로 브라우저에서 접속
3. 네이버 로그인 및 권한 동의
4. 리다이렉트 URL에서 `code` 파라미터 복사
5. 코드로 토큰 교환 (별도 구현 필요)

#### 방법 2: 기존 토큰 사용

이미 다른 서비스에서 사용 중인 토큰이 있다면:

```bash
python manage.py naver_token --set "액세스토큰"
python manage.py naver_token --set-refresh "리프레시토큰"
```

### 4. 토큰 테스트

```bash
# 테스트 게시글 작성
python manage.py naver_token --test
```

성공 시 실제 카페에 테스트 글이 작성됩니다.

## 🔧 문제 해결

### 토큰이 없는 경우

```
❌ 게시 실패!
에러: NO_TOKEN
메시지: 네이버 로그인이 필요합니다
```

**해결:** 토큰을 설정하세요
```bash
python manage.py naver_token --set "YOUR_TOKEN"
```

### 토큰이 만료된 경우

```
❌ 게시 실패!
에러: AUTH_FAILED
메시지: 인증이 만료되었습니다
```

**해결:** 리프레시 토큰으로 갱신하거나 새 토큰 획득

### 권한이 없는 경우

```
❌ 게시 실패!
에러: API_ERROR
status_code: 403
```

**해결:** 네이버 개발자센터에서 카페 API 권한 확인

## 📌 카페 정보

- **카페 URL:** https://cafe.naver.com/f-e
- **카페 ID:** 29829680
- **게시판 ID:** 26 (메뉴 ID)
- **게시판 URL:** https://cafe.naver.com/f-e/cafes/29829680/menus/26

## 🛠️ 관리 명령어

```bash
# 토큰 설정
python manage.py naver_token --set TOKEN

# 리프레시 토큰 설정
python manage.py naver_token --set-refresh TOKEN

# 토큰 상태 확인
python manage.py naver_token --show

# 테스트 게시
python manage.py naver_token --test

# 로그인 URL 생성
python manage.py naver_token --auth-url

# 환경 변수 가이드
python manage.py naver_token --set-env
```

## ✅ 자동 게시 작동 확인

1. 의뢰리스트 페이지 접속
2. 게시글이 없는 항목에서 "게시하기" 버튼 클릭
3. 모달에서 제목과 내용 확인
4. "링크 업데이트" 버튼 클릭
5. 자동 게시 성공 시 실제 게시글 링크 생성
6. 실패 시 수동 모드로 자동 전환

## 📝 주의사항

- 토큰은 보안상 중요한 정보이므로 안전하게 관리
- 프로덕션 환경에서는 환경 변수 사용 권장
- 토큰 파일은 `/var/www/testpark/.naver_token.json`에 저장됨
- 파일 권한은 600으로 자동 설정됨

## 💡 팁

- 토큰은 캐시와 파일에 이중으로 저장되어 안정성 향상
- 자동으로 토큰 갱신 시도 (리프레시 토큰 필요)
- 실패 시 자동으로 수동 모드로 전환되어 서비스 중단 없음