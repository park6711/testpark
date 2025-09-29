"""
네이버 카페 자동 게시 모듈
한글 인코딩 문제를 완벽하게 처리하는 버전
"""

import requests
import urllib.parse
import json
import time
import logging
from typing import Dict, Optional, Tuple
import re

logger = logging.getLogger(__name__)

class NaverCafeAPI:
    """네이버 카페 API 클래스 - 한글 인코딩 완벽 처리"""

    def __init__(self, client_id: str = None, client_secret: str = None):
        """
        네이버 카페 API 초기화

        Args:
            client_id: 네이버 개발자센터에서 발급받은 클라이언트 ID
            client_secret: 네이버 개발자센터에서 발급받은 클라이언트 시크릿
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
        self.base_url = "https://openapi.naver.com/v1/cafe"

    def encode_korean_text(self, text: str) -> str:
        """
        한글 텍스트를 네이버 카페 API용으로 인코딩
        UTF-8 → MS949 → URL encode

        Args:
            text: 인코딩할 텍스트

        Returns:
            인코딩된 텍스트
        """
        try:
            # 방법 1: UTF-8 → MS949 → URL encode
            encoded = urllib.parse.quote(text.encode('ms949'))
            return encoded
        except UnicodeEncodeError:
            # MS949로 인코딩할 수 없는 문자가 있는 경우
            try:
                # 방법 2: UTF-8 → EUC-KR → URL encode
                encoded = urllib.parse.quote(text.encode('euc-kr'))
                return encoded
            except UnicodeEncodeError:
                # 방법 3: UTF-8 직접 URL encode
                encoded = urllib.parse.quote(text.encode('utf-8'))
                return encoded

    def validate_korean_text(self, text: str) -> Tuple[bool, str]:
        """
        한글 텍스트 유효성 검사

        Args:
            text: 검사할 텍스트

        Returns:
            (유효 여부, 에러 메시지 또는 정제된 텍스트)
        """
        if not text:
            return False, "텍스트가 비어있습니다"

        # 특수문자 체크 및 정제
        # 네이버 카페에서 문제를 일으킬 수 있는 문자들 제거
        problematic_chars = ['\\x00', '\x00', '\u200b', '\ufeff']
        for char in problematic_chars:
            text = text.replace(char, '')

        # MS949에서 지원하지 않는 문자 확인
        try:
            text.encode('ms949')
        except UnicodeEncodeError as e:
            # 문제가 되는 문자를 찾아서 대체
            problem_char = text[e.start:e.end]
            logger.warning(f"MS949로 인코딩할 수 없는 문자 발견: {problem_char}")
            # 대체 문자로 치환
            text = text.replace(problem_char, '?')

        return True, text

    def set_access_token(self, token: str):
        """액세스 토큰 설정"""
        self.access_token = token

    def post_to_cafe(self,
                    cafe_id: str,
                    menu_id: str,
                    subject: str,
                    content: str,
                    open_type: str = "public") -> Dict:
        """
        네이버 카페에 게시글 작성

        Args:
            cafe_id: 카페 ID (예: 29829680)
            menu_id: 메뉴 ID (예: 26)
            subject: 게시글 제목
            content: 게시글 내용
            open_type: 공개 설정 (public, member)

        Returns:
            API 응답 딕셔너리
        """
        if not self.access_token:
            return {"success": False, "error": "액세스 토큰이 설정되지 않았습니다"}

        # 한글 텍스트 유효성 검사 및 정제
        valid_subject, subject = self.validate_korean_text(subject)
        valid_content, content = self.validate_korean_text(content)

        if not valid_subject or not valid_content:
            return {"success": False, "error": "텍스트 유효성 검사 실패"}

        # API 엔드포인트
        url = f"{self.base_url}/{cafe_id}/menu/{menu_id}/articles"

        # 헤더 설정
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
        }

        # 데이터 준비 (URL 인코딩)
        data = {
            "subject": self.encode_korean_text(subject),
            "content": self.encode_korean_text(content),
            "openyn": "true" if open_type == "public" else "false"
        }

        # 폼 데이터로 변환
        form_data = "&".join([f"{key}={value}" for key, value in data.items()])

        try:
            # API 호출
            response = requests.post(url, headers=headers, data=form_data)
            response.raise_for_status()

            result = response.json()

            # 성공 시 게시글 URL 생성
            if result.get("message", {}).get("result", {}).get("articleId"):
                article_id = result["message"]["result"]["articleId"]
                article_url = f"https://cafe.naver.com/{cafe_id}/{article_id}"
                result["article_url"] = article_url

            return {"success": True, "data": result}

        except requests.exceptions.RequestException as e:
            logger.error(f"네이버 카페 API 호출 실패: {e}")
            return {"success": False, "error": str(e)}
        except json.JSONDecodeError as e:
            logger.error(f"응답 파싱 실패: {e}")
            return {"success": False, "error": "응답 파싱 실패", "response_text": response.text}


class NaverCafeSimplePost:
    """
    네이버 카페 간단 게시 (OAuth 없이 사용)
    웹훅이나 다른 방식으로 실제 게시를 처리
    """

    def __init__(self):
        self.cafe_url = "https://cafe.naver.com/f-e"
        self.cafe_id = "29829680"
        self.menu_id = "26"

    def format_post_content(self, order_data: Dict) -> Tuple[str, str]:
        """
        주문 데이터를 카페 게시글 형식으로 변환

        Args:
            order_data: 주문 정보 딕셔너리

        Returns:
            (제목, 내용) 튜플
        """
        # 제목 생성
        area = order_data.get('sArea', '지역미정')
        name = order_data.get('sName', '고객')
        title = f"[{area}] 인테리어 견적문의 - {name}님"

        # 내용 생성
        content = f"""
안녕하세요. 인테리어 견적문의 드립니다.

=====================================
▶ 고객정보
=====================================
- 성함: {order_data.get('sName', '-')}
- 연락처: {order_data.get('sPhone', '-')}
- 네이버ID: {order_data.get('sNaverID', '-')}
- 별명: {order_data.get('sNick', '-')}

=====================================
▶ 공사정보
=====================================
- 공사지역: {order_data.get('sArea', '-')}
- 공사예정일: {order_data.get('dateSchedule', '협의')}
- 지정업체: {order_data.get('designation', '없음')}

=====================================
▶ 공사내용
=====================================
{order_data.get('sConstruction', '내용 없음')}

=====================================

견적 부탁드립니다.
감사합니다.
        """.strip()

        return title, content

    def create_posting_data(self, order_data: Dict) -> Dict:
        """
        게시용 데이터 생성

        Args:
            order_data: 주문 정보

        Returns:
            게시 데이터 딕셔너리
        """
        title, content = self.format_post_content(order_data)

        return {
            "cafe_id": self.cafe_id,
            "menu_id": self.menu_id,
            "title": title,
            "content": content,
            "order_id": order_data.get('no'),
            "timestamp": int(time.time())
        }

    def validate_and_clean_text(self, text: str) -> str:
        """
        텍스트 정제 및 유효성 검사
        """
        if not text:
            return ""

        # HTML 태그 제거
        text = re.sub(r'<[^>]+>', '', text)

        # 특수문자 정제
        text = text.replace('\x00', '')
        text = text.replace('\u200b', '')  # Zero-width space
        text = text.replace('\ufeff', '')  # BOM

        # 연속된 공백과 줄바꿈 정리
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r' {2,}', ' ', text)

        return text.strip()


# 테스트 함수들
def test_korean_encoding():
    """한글 인코딩 테스트"""
    api = NaverCafeAPI()

    test_cases = [
        "안녕하세요",
        "한글 테스트입니다",
        "특수문자 테스트: ★☆♥♡",
        "이모지 테스트: 😀🎉",
        "복잡한 한글: 됐었겠죠뷁",
    ]

    print("=== 한글 인코딩 테스트 ===")
    for text in test_cases:
        encoded = api.encode_korean_text(text)
        print(f"원본: {text}")
        print(f"인코딩: {encoded}")
        print("-" * 30)

def test_post_formatting():
    """게시글 포맷팅 테스트"""
    simple_post = NaverCafeSimplePost()

    test_order = {
        'no': 123,
        'sName': '홍길동',
        'sPhone': '010-1234-5678',
        'sNaverID': 'test_user',
        'sNick': '테스트닉',
        'sArea': '서울시 강남구',
        'dateSchedule': '2024년 1월',
        'designation': '특정업체 지정',
        'sConstruction': '아파트 32평\n전체 인테리어\n예산: 3000만원'
    }

    title, content = simple_post.format_post_content(test_order)

    print("=== 게시글 포맷팅 테스트 ===")
    print(f"제목: {title}")
    print("-" * 50)
    print("내용:")
    print(content)

if __name__ == "__main__":
    # 테스트 실행
    test_korean_encoding()
    print("\n")
    test_post_formatting()