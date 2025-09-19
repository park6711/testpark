"""
네이버 소셜 로그인 API 연동 유틸리티
"""

import urllib.parse
import requests
import secrets
import string
from django.conf import settings
from django.core.cache import cache
from typing import Dict, Optional, Tuple


class NaverAuthManager:
    """네이버 인증 관리 클래스"""

    def __init__(self):
        self.client_id = settings.NAVER_CLIENT_ID
        self.client_secret = settings.NAVER_CLIENT_SECRET
        self.redirect_uri = settings.NAVER_REDIRECT_URI

    def generate_state(self) -> str:
        """CSRF 방지용 state 값 생성"""
        state = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))
        # 캐시에 5분간 저장
        cache.set(f"naver_state_{state}", True, 300)
        return state

    def verify_state(self, state: str) -> bool:
        """state 값 검증"""
        cache_key = f"naver_state_{state}"
        if cache.get(cache_key):
            cache.delete(cache_key)  # 일회용으로 사용
            return True
        return False

    def get_login_url(self) -> Tuple[str, str]:
        """
        네이버 로그인 URL 생성
        Returns:
            (login_url, state): 로그인 URL과 state 값
        """
        state = self.generate_state()

        params = {
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'state': state
        }

        base_url = 'https://nid.naver.com/oauth2.0/authorize'
        login_url = f"{base_url}?{urllib.parse.urlencode(params)}"

        return login_url, state

    def get_access_token(self, code: str, state: str) -> Optional[Dict]:
        """
        인증 코드로 액세스 토큰 획득
        Args:
            code: 네이버에서 받은 인증 코드
            state: CSRF 검증용 state 값
        Returns:
            토큰 정보 딕셔너리 또는 None
        """
        if not self.verify_state(state):
            return None

        token_url = 'https://nid.naver.com/oauth2.0/token'
        data = {
            'grant_type': 'authorization_code',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': code,
            'state': state
        }

        try:
            response = requests.post(token_url, data=data, timeout=10)
            response.raise_for_status()
            token_data = response.json()

            if 'access_token' in token_data:
                return token_data
            else:
                print(f"토큰 획득 실패: {token_data}")
                return None

        except requests.RequestException as e:
            print(f"네이버 토큰 요청 에러: {e}")
            return None

    def get_user_info(self, access_token: str) -> Optional[Dict]:
        """
        액세스 토큰으로 사용자 정보 조회
        Args:
            access_token: 네이버 액세스 토큰
        Returns:
            사용자 정보 딕셔너리 또는 None
        """
        headers = {'Authorization': f'Bearer {access_token}'}

        try:
            response = requests.get(
                'https://openapi.naver.com/v1/nid/me',
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            user_data = response.json()

            if user_data.get('resultcode') == '00':
                return user_data.get('response')
            else:
                print(f"사용자 정보 조회 실패: {user_data}")
                return None

        except requests.RequestException as e:
            print(f"네이버 사용자 정보 요청 에러: {e}")
            return None

    def process_naver_login(self, code: str, state: str, skip_state_verification: bool = False) -> Tuple[bool, Optional[Dict], Optional[str]]:
        """
        네이버 로그인 전체 프로세스 처리
        Args:
            code: 네이버 인증 코드
            state: CSRF 검증용 state
            skip_state_verification: state 검증 건너뛰기 (이미 검증된 경우)
        Returns:
            (성공 여부, 사용자 정보, 에러 메시지)
        """
        try:
            print(f"[DEBUG] 네이버 로그인 처리 시작 - code: {code[:10]}..., state: {state}")

            # 1. 액세스 토큰 획득 (state 검증 포함 또는 제외)
            if skip_state_verification:
                # state 검증을 건너뛰고 토큰 요청
                token_url = 'https://nid.naver.com/oauth2.0/token'
                data = {
                    'grant_type': 'authorization_code',
                    'client_id': self.client_id,
                    'client_secret': self.client_secret,
                    'code': code,
                    'state': state
                }

                response = requests.post(token_url, data=data, timeout=10)
                response.raise_for_status()
                token_data = response.json()

                if 'access_token' not in token_data:
                    print(f"[ERROR] 토큰 획득 실패: {token_data}")
                    return False, None, f"토큰 획득 실패: {token_data.get('error_description', '알 수 없는 오류')}"
            else:
                token_data = self.get_access_token(code, state)
                if not token_data:
                    return False, None, "액세스 토큰 획득에 실패했습니다."

            print(f"[DEBUG] 토큰 획득 성공")

            # 2. 사용자 정보 조회
            access_token = token_data.get('access_token')
            user_info = self.get_user_info(access_token)
            if not user_info:
                return False, None, "사용자 정보 조회에 실패했습니다."

            print(f"[DEBUG] 사용자 정보 조회 성공: {user_info.get('email', 'NO_EMAIL')}")

            # 3. 필수 필드 검증 (email만 필수)
            if not user_info.get('email'):
                return False, None, "네이버에서 email 정보를 제공하지 않습니다."

            # 4. id 필드 처리 (선택사항)
            if not user_info.get('id'):
                # email에서 @ 앞부분을 id로 사용
                email_prefix = user_info['email'].split('@')[0]
                user_info['id'] = email_prefix
                print(f"[DEBUG] id 필드 없음, 이메일 prefix 사용: {user_info['id']}")

            # 5. name 필드 처리 (선택사항)
            if not user_info.get('name'):
                if user_info.get('nickname'):
                    user_info['name'] = user_info['nickname']
                    print(f"[DEBUG] name 필드 없음, nickname 사용: {user_info['name']}")
                else:
                    # 이메일에서 @ 앞부분을 name으로 사용
                    email_prefix = user_info['email'].split('@')[0]
                    user_info['name'] = email_prefix
                    print(f"[DEBUG] name/nickname 필드 없음, 이메일 prefix 사용: {user_info['name']}")

            print(f"[DEBUG] 네이버 로그인 처리 완료 성공")
            return True, user_info, None

        except Exception as e:
            print(f"[ERROR] 네이버 로그인 처리 중 예외 발생: {str(e)}")
            return False, None, f"로그인 처리 중 오류 발생: {str(e)}"


class JandiWebhookManager:
    """잔디 웹훅 관리 클래스"""

    def __init__(self):
        self.webhook_url = settings.JANDI_WEBHOOK_URL

    def send_auth_code(self, user_email: str, auth_code: str) -> bool:
        """
        잔디로 인증번호 발송
        Args:
            user_email: 사용자 이메일
            auth_code: 6자리 인증번호
        Returns:
            발송 성공 여부
        """
        message = {
            "body": "🔐 TestPark 인증번호",
            "connectColor": "#0066CC",
            "connectInfo": [
                {
                    "title": "인증번호",
                    "description": f"**{auth_code}**"
                },
                {
                    "title": "이메일",
                    "description": user_email
                },
                {
                    "title": "유효시간",
                    "description": "5분"
                },
                {
                    "title": "안내",
                    "description": "이 인증번호를 로그인 페이지에 입력해주세요."
                }
            ]
        }

        try:
            response = requests.post(
                self.webhook_url,
                json=message,
                timeout=10
            )
            response.raise_for_status()
            return True

        except requests.RequestException as e:
            print(f"잔디 웹훅 발송 에러: {e}")
            return False

    def send_login_success(self, user_name: str, user_email: str) -> bool:
        """
        로그인 성공 알림 발송
        Args:
            user_name: 사용자 이름
            user_email: 사용자 이메일
        Returns:
            발송 성공 여부
        """
        message = {
            "body": "✅ TestPark 로그인 성공",
            "connectColor": "#00CC66",
            "connectInfo": [
                {
                    "title": "사용자",
                    "description": f"**{user_name}** ({user_email})"
                },
                {
                    "title": "시간",
                    "description": "지금"
                },
                {
                    "title": "상태",
                    "description": "네이버 계정 연동 완료"
                }
            ]
        }

        try:
            response = requests.post(
                self.webhook_url,
                json=message,
                timeout=10
            )
            response.raise_for_status()
            return True

        except requests.RequestException as e:
            print(f"잔디 웹훅 발송 에러: {e}")
            return False


# 전역 인스턴스 생성
naver_auth = NaverAuthManager()
jandi_webhook = JandiWebhookManager()