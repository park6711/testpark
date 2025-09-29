"""
네이버 OAuth 및 카페 실제 글쓰기 구현
"""

import os
import json
import requests
import urllib.parse
from datetime import datetime, timedelta
from django.conf import settings
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)


class NaverOAuthManager:
    """네이버 OAuth 토큰 관리 클래스"""

    def __init__(self):
        # 네이버 앱 정보 (settings.py 또는 환경변수에서 가져오기)
        self.client_id = getattr(settings, 'NAVER_CLIENT_ID', os.environ.get('NAVER_CLIENT_ID'))
        self.client_secret = getattr(settings, 'NAVER_CLIENT_SECRET', os.environ.get('NAVER_CLIENT_SECRET'))
        self.redirect_uri = getattr(settings, 'NAVER_REDIRECT_URI', 'http://localhost:8000/naver/callback')

        # API URL
        self.auth_url = "https://nid.naver.com/oauth2.0/authorize"
        self.token_url = "https://nid.naver.com/oauth2.0/token"
        self.cafe_api_url = "https://openapi.naver.com/v1/cafe"

    def get_authorization_url(self, state=None):
        """네이버 로그인 URL 생성"""
        params = {
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'state': state or 'testpark_cafe_posting',
        }
        return f"{self.auth_url}?{urllib.parse.urlencode(params)}"

    def get_access_token(self, code, state):
        """인증 코드로 액세스 토큰 획득"""
        params = {
            'grant_type': 'authorization_code',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'redirect_uri': self.redirect_uri,
            'code': code,
            'state': state,
        }

        response = requests.post(self.token_url, params=params)

        if response.status_code == 200:
            token_data = response.json()

            # 토큰 캐시에 저장 (만료시간 고려)
            expires_in = int(token_data.get('expires_in', 3600))
            cache.set('naver_access_token', token_data['access_token'], expires_in - 60)
            cache.set('naver_refresh_token', token_data.get('refresh_token'), 30 * 24 * 3600)  # 30일

            return token_data
        else:
            logger.error(f"토큰 획득 실패: {response.text}")
            return None

    def refresh_access_token(self):
        """리프레시 토큰으로 액세스 토큰 갱신"""
        refresh_token = cache.get('naver_refresh_token')
        if not refresh_token:
            return None

        params = {
            'grant_type': 'refresh_token',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'refresh_token': refresh_token,
        }

        response = requests.post(self.token_url, params=params)

        if response.status_code == 200:
            token_data = response.json()

            # 새 토큰 캐시에 저장
            expires_in = int(token_data.get('expires_in', 3600))
            cache.set('naver_access_token', token_data['access_token'], expires_in - 60)

            return token_data['access_token']
        else:
            logger.error(f"토큰 갱신 실패: {response.text}")
            return None

    def get_valid_token(self):
        """유효한 액세스 토큰 반환 (필요시 갱신)"""
        token = cache.get('naver_access_token')

        if not token:
            # 토큰이 없으면 갱신 시도
            token = self.refresh_access_token()

        return token

    def save_token_to_file(self, token):
        """토큰을 파일에 저장 (백업용)"""
        token_file = '/var/www/testpark/.naver_token.json'
        try:
            with open(token_file, 'w') as f:
                json.dump({
                    'access_token': token,
                    'saved_at': datetime.now().isoformat()
                }, f)
            os.chmod(token_file, 0o600)  # 보안을 위해 권한 설정
        except Exception as e:
            logger.error(f"토큰 파일 저장 실패: {e}")

    def load_token_from_file(self):
        """파일에서 토큰 로드"""
        token_file = '/var/www/testpark/.naver_token.json'
        try:
            if os.path.exists(token_file):
                with open(token_file, 'r') as f:
                    data = json.load(f)
                    return data.get('access_token')
        except Exception as e:
            logger.error(f"토큰 파일 로드 실패: {e}")
        return None


class NaverCafeRealAPI:
    """네이버 카페 실제 API 호출 클래스"""

    def __init__(self):
        self.oauth_manager = NaverOAuthManager()
        self.cafe_api_url = "https://openapi.naver.com/v1/cafe"

    def post_article(self, cafe_id, menu_id, subject, content, session_token=None):
        """
        네이버 카페에 실제로 글 작성

        Args:
            cafe_id: 카페 ID (29829680)
            menu_id: 메뉴 ID (26)
            subject: 제목
            content: 내용
            session_token: 세션에 저장된 사용자 토큰 (우선 사용)

        Returns:
            성공 시 게시글 정보, 실패 시 None
        """
        # 토큰 획득 우선순위:
        # 1. 세션 토큰 (로그인한 사용자 토큰)
        # 2. 직접 설정된 토큰
        # 3. 캐시된 토큰
        # 4. 파일에서 로드

        token = None

        # 1. 세션 토큰 우선 사용
        if session_token:
            token = session_token
            logger.info("세션에 저장된 사용자 토큰 사용")
        # 2. 이미 설정된 access_token이 있으면 사용
        elif hasattr(self.oauth_manager, 'access_token') and self.oauth_manager.access_token:
            token = self.oauth_manager.access_token
        # 3. 캐시에서 토큰 가져오기
        else:
            token = self.oauth_manager.get_valid_token()

        # 4. 파일에서 토큰 로드 시도 (캐시에 없는 경우)
        if not token:
            token = self.oauth_manager.load_token_from_file()
            if token:
                cache.set('naver_access_token', token, 3600)

        if not token:
            logger.error("유효한 액세스 토큰이 없습니다")
            return {'success': False, 'error': 'NO_TOKEN', 'message': '네이버 로그인이 필요합니다'}

        # API 엔드포인트
        url = f"{self.cafe_api_url}/{cafe_id}/menu/{menu_id}/articles"

        # 헤더 설정
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
        }

        # 한글 인코딩 처리
        try:
            # MS949로 먼저 시도
            encoded_subject = urllib.parse.quote(subject.encode('ms949'))
            encoded_content = urllib.parse.quote(content.encode('ms949'))
        except UnicodeEncodeError:
            # UTF-8로 폴백
            encoded_subject = urllib.parse.quote(subject.encode('utf-8'))
            encoded_content = urllib.parse.quote(content.encode('utf-8'))

        # 데이터 준비
        data = f"subject={encoded_subject}&content={encoded_content}&openyn=true"

        try:
            # API 호출
            response = requests.post(url, headers=headers, data=data)
            response_data = response.json()

            if response.status_code == 200:
                # 성공적으로 게시됨
                article_id = response_data.get('message', {}).get('result', {}).get('articleId')

                if article_id:
                    article_url = f"https://cafe.naver.com/f-e/{article_id}"
                    logger.info(f"카페 글 작성 성공: {article_url}")

                    return {
                        'success': True,
                        'article_id': article_id,
                        'article_url': article_url,
                        'cafe_id': cafe_id,
                        'menu_id': menu_id
                    }
                else:
                    logger.error(f"글 작성 응답에 article_id 없음: {response_data}")
                    return {'success': False, 'error': 'NO_ARTICLE_ID', 'response': response_data}

            elif response.status_code == 401:
                # 토큰 만료 - 갱신 시도
                logger.info("토큰 만료, 갱신 시도")
                new_token = self.oauth_manager.refresh_access_token()

                if new_token:
                    # 새 토큰으로 재시도
                    headers['Authorization'] = f'Bearer {new_token}'
                    response = requests.post(url, headers=headers, data=data)

                    if response.status_code == 200:
                        response_data = response.json()
                        article_id = response_data.get('message', {}).get('result', {}).get('articleId')

                        if article_id:
                            article_url = f"https://cafe.naver.com/f-e/{article_id}"
                            return {
                                'success': True,
                                'article_id': article_id,
                                'article_url': article_url
                            }

                return {'success': False, 'error': 'AUTH_FAILED', 'message': '인증 실패 - 재로그인 필요'}

            else:
                logger.error(f"카페 API 오류: {response.status_code} - {response.text}")
                return {
                    'success': False,
                    'error': 'API_ERROR',
                    'status_code': response.status_code,
                    'message': response_data.get('message', response.text)
                }

        except requests.exceptions.RequestException as e:
            logger.error(f"네트워크 오류: {e}")
            return {'success': False, 'error': 'NETWORK_ERROR', 'message': str(e)}
        except json.JSONDecodeError as e:
            logger.error(f"JSON 파싱 오류: {e}")
            return {'success': False, 'error': 'PARSE_ERROR', 'message': str(e)}


# 간편 함수
def post_to_naver_cafe(order_data, session_token=None):
    """
    주문 데이터로 네이버 카페에 게시

    Args:
        order_data: 주문 정보 딕셔너리
        session_token: 세션에 저장된 사용자 토큰 (선택)

    Returns:
        게시 결과 딕셔너리
    """
    from .naver_cafe import NaverCafeSimplePost

    # 게시글 포맷팅
    simple_post = NaverCafeSimplePost()
    title, content = simple_post.format_post_content(order_data)

    # 실제 게시
    api = NaverCafeRealAPI()
    result = api.post_article(
        cafe_id="29829680",
        menu_id="26",
        subject=title,
        content=content,
        session_token=session_token
    )

    return result


# 테스트 함수
def test_real_posting():
    """실제 게시 테스트"""
    test_order = {
        'no': 9999,
        'sName': '테스트고객',
        'sPhone': '010-0000-0000',
        'sNaverID': 'test_user',
        'sNick': '테스트',
        'sArea': '서울시 테스트구',
        'dateSchedule': '2024년 12월',
        'designation': '테스트업체',
        'sConstruction': '테스트 게시글입니다.\n실제 게시 테스트'
    }

    result = post_to_naver_cafe(test_order)

    if result['success']:
        print(f"✅ 게시 성공!")
        print(f"게시글 URL: {result['article_url']}")
        print(f"게시글 ID: {result['article_id']}")
    else:
        print(f"❌ 게시 실패:")
        print(f"에러 코드: {result.get('error')}")
        print(f"메시지: {result.get('message')}")

    return result