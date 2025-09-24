# 구글 스프레드시트 동기화 서비스
import os
import json
import uuid
from datetime import datetime
import logging
from typing import List, Dict, Any
from django.conf import settings
from django.db import transaction
from django.core.cache import cache
from .models import Order
import gspread
from oauth2client.service_account import ServiceAccountCredentials

logger = logging.getLogger(__name__)

# 기본 경로 설정
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CREDENTIALS_PATH = os.path.join(BASE_DIR, 'seongdal-a900e25ac63c.json')

class GoogleSheetsSync:
    """구글 스프레드시트와 Django 데이터베이스를 동기화하는 서비스"""

    def __init__(self):
        # 구글 스프레드시트 ID와 시트 설정
        self.spreadsheet_id = '157_Z_ZGX2_bE_vgtZnrWtB6BxCBJOigNqaaAAMGJ1NM'
        self.sheet_name = '[견적의뢰 접수]'  # 정확한 시트 이름

        # 서비스 계정 인증 설정
        self.scope = ['https://spreadsheets.google.com/feeds',
                      'https://www.googleapis.com/auth/drive']

        # 인증 클라이언트 초기화
        self.client = None
        self.sheet = None
        self._authenticate()

    def _authenticate(self):
        """구글 서비스 계정으로 인증"""
        try:
            # 서비스 계정 인증정보 로드
            credentials = ServiceAccountCredentials.from_json_keyfile_name(
                CREDENTIALS_PATH, self.scope)

            # gspread 클라이언트 생성
            self.client = gspread.authorize(credentials)

            # 스프레드시트 열기
            self.sheet = self.client.open_by_key(self.spreadsheet_id)

            logger.info("구글 스프레드시트 인증 성공")
        except Exception as e:
            logger.error(f"구글 스프레드시트 인증 실패: {str(e)}")
            raise

    def fetch_sheet_data(self, last_sync_time=None) -> List[Dict[str, Any]]:
        """구글 스프레드시트에서 데이터 가져오기

        Args:
            last_sync_time: 마지막 동기화 시간 (증분 동기화용)
        """
        try:
            if not self.sheet:
                self._authenticate()

            # 시트 선택 (첫 번째 시트 또는 이름으로 선택)
            worksheet = self.sheet.worksheet(self.sheet_name)

            # 8행부터 AI열(35번째)까지 데이터 가져오기
            # get_all_values()는 모든 데이터를 리스트로 반환
            all_values = worksheet.get_all_values()

            # 8행부터 시작 (인덱스는 7)
            data_rows = all_values[7:]  # 8행부터

            if not data_rows:
                logger.info("스프레드시트에 데이터가 없습니다.")
                return []

            # 실제 스프레드시트 컬럼 순서
            # A(0): 타임스탬프
            # B(1): 카페에서도 견적의뢰 글을 올리셨나요?
            # C(2): 원하시는 [공동구매] 또는 [열린업체]가 있으시면 적어주세요
            # D(3): 별명 (카페내 별명)
            # E(4): Naver 아이디
            # F(5): 이름
            # G(6): 통화 가능한 고객님 핸드폰 번호
            # H(7): 견적의뢰게시글
            # I(8): 공사(또는 의뢰) 지역
            # J(9): 공사 예정일
            # K(10): 평형, 공사 내용 등을 기재해주세요
            # AH(33): 참조용링크
            # AI(34): UUID

            # 데이터를 딕셔너리 리스트로 변환
            result = []
            for row in data_rows:
                # UUID 컬럼(AI열, 인덱스 34)이 있는 행만 처리
                if len(row) > 34 and row[34]:  # AI열에 값이 있는지 확인
                    # A열(타임스탬프)이 유효한 날짜값인지 먼저 확인
                    timestamp_str = row[0] if len(row) > 0 else ''

                    # 타임스탬프가 없거나 빈 문자열인 경우 건너뛰기
                    if not timestamp_str or timestamp_str.strip() == '':
                        logger.debug(f"빈 타임스탬프로 인해 행 건너뜀: UUID={row[34]}")
                        continue

                    # 타임스탬프가 유효한 날짜 형식인지 확인
                    if not self._is_valid_timestamp(timestamp_str):
                        logger.warning(f"유효하지 않은 타임스탬프로 인해 행 건너뜀: {timestamp_str}, UUID={row[34]}")
                        continue

                    row_dict = {}

                    # 실제 컬럼 매핑 (정확한 구조)
                    row_dict['timestamp'] = timestamp_str  # A: 타임스탬프
                    row_dict['cafe_post'] = row[1] if len(row) > 1 else ''  # B: 카페글 여부
                    row_dict['designation'] = row[2] if len(row) > 2 else ''  # C: 공동구매/열린업체 지정
                    row_dict['nick'] = row[3] if len(row) > 3 else ''  # D: 별명
                    row_dict['naver_id'] = row[4] if len(row) > 4 else ''  # E: Naver 아이디
                    row_dict['name'] = row[5] if len(row) > 5 else ''  # F: 이름
                    row_dict['phone'] = row[6] if len(row) > 6 else ''  # G: 전화번호
                    row_dict['post'] = row[7] if len(row) > 7 else ''  # H: 견적의뢰게시글
                    row_dict['area'] = row[8] if len(row) > 8 else ''  # I: 공사지역
                    row_dict['schedule_date'] = row[9] if len(row) > 9 else ''  # J: 공사예정일
                    row_dict['construction'] = row[10] if len(row) > 10 else ''  # K: 공사내용

                    # AH열: 참조용링크 (인덱스 33)
                    row_dict['ref_link'] = row[33] if len(row) > 33 else ''

                    # 개인정보 동의 필드 (Y, Z열)
                    row_dict['privacy1'] = row[24] if len(row) > 24 else ''  # Y열: 개인정보 수집/이용 동의
                    row_dict['privacy2'] = row[25] if len(row) > 25 else ''  # Z열: 개인정보 제3자 제공 동의

                    # UUID 컬럼 추가 (AI열, 인덱스 34)
                    row_dict['uuid_col'] = row[34] if len(row) > 34 else ''

                    # UUID가 있는 경우만 추가
                    if row_dict.get('uuid_col'):
                        result.append(row_dict)

            logger.info(f"스프레드시트에서 {len(result)}개 행 가져옴")
            return result

        except Exception as e:
            logger.error(f"스프레드시트 데이터 가져오기 실패: {str(e)}")
            return []

    def _is_valid_timestamp(self, timestamp_str: str) -> bool:
        """타임스탬프가 유효한 날짜 형식인지 검증"""
        if not timestamp_str or not timestamp_str.strip():
            return False

        try:
            import re
            # 빈 문자열이나 공백만 있는 경우
            if timestamp_str.strip() == '':
                return False

            # 한국어 오전/오후 처리
            temp_str = timestamp_str.replace('오전', 'AM').replace('오후', 'PM')

            # 점 제거 (한국 날짜 형식)
            temp_str = re.sub(r'(\d+)\. (\d+)\. (\d+)', r'\1/\2/\3', temp_str)

            # 다양한 타임스탬프 형식 시도
            timestamp_formats = [
                '%Y/%m/%d %p %I:%M:%S',  # 2025/9/16 오후 12:12:46
                '%Y/%m/%d %H:%M:%S',     # 2025/9/16 12:12:46
                '%m/%d/%Y %I:%M:%S %p',  # 9/16/2025 12:12:46 PM
                '%m/%d/%Y %H:%M:%S',     # 9/16/2025 12:12:46
                '%Y-%m-%d %H:%M:%S',     # 2025-09-16 12:12:46
            ]

            for fmt in timestamp_formats:
                try:
                    datetime.strptime(temp_str, fmt)
                    return True
                except ValueError:
                    continue

            # 날짜만 있는 경우도 허용 (시간 없음)
            date_formats = ['%Y/%m/%d', '%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y']
            for fmt in date_formats:
                try:
                    datetime.strptime(temp_str.split()[0] if ' ' in temp_str else temp_str, fmt)
                    return True
                except ValueError:
                    continue

            return False

        except Exception as e:
            logger.debug(f"타임스탬프 검증 실패: {timestamp_str} - {str(e)}")
            return False

    def parse_date(self, date_str: str):
        """날짜 문자열 파싱"""
        if not date_str:
            return None

        try:
            import re
            # "2026. 1. 2" 같은 한국 형식 처리
            date_str = date_str.strip()
            date_str = re.sub(r'(\d+)\. (\d+)\. (\d+)', r'\1/\2/\3', date_str)

            # 다양한 날짜 형식 처리
            for fmt in ['%Y/%m/%d', '%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%Y. %m. %d']:
                try:
                    return datetime.strptime(date_str, fmt).date()
                except ValueError:
                    continue

            logger.warning(f"날짜 파싱 실패: {date_str}")
            return None
        except Exception as e:
            logger.warning(f"날짜 파싱 오류: {date_str} - {str(e)}")
            return None

    def parse_boolean(self, value: str) -> bool:
        """불린 값 파싱"""
        if not value:
            return False
        return value.lower() in ['true', 'yes', '예', '동의', '1', 'o']

    @transaction.atomic
    def sync_data(self, update_existing=False) -> Dict[str, int]:
        """구글 스프레드시트 데이터를 DB와 동기화

        Args:
            update_existing: True면 기존 레코드도 업데이트
        """
        from django.core.cache import cache

        # 마지막 동기화 시간 가져오기
        last_sync = cache.get('last_google_sync_time')

        sheet_data = self.fetch_sheet_data(last_sync)

        created_count = 0
        updated_count = 0
        skipped_count = 0
        invalid_count = 0

        for row in sheet_data:
            try:
                sheet_uuid = row.get('uuid_col', '').strip()

                if not sheet_uuid:
                    skipped_count += 1
                    continue

                # 타임스탬프 재검증 (이미 fetch_sheet_data에서 검증했지만 한번 더)
                timestamp_str = row.get('timestamp', '')
                if not timestamp_str or not self._is_valid_timestamp(timestamp_str):
                    skipped_count += 1
                    logger.warning(f"동기화 시 타임스탬프 검증 실패: UUID={sheet_uuid}")
                    continue

                # 최소한의 고객 정보가 있는지 확인 (이름 또는 전화번호 중 하나는 있어야 함)
                name = row.get('name', '').strip()
                phone = row.get('phone', '').strip()

                if not name and not phone:
                    skipped_count += 1
                    logger.info(f"고객 정보 부족으로 건너뜀: UUID={sheet_uuid}")
                    continue

                # UUID로 기존 레코드 확인
                existing_order = Order.objects.filter(google_sheet_uuid=sheet_uuid).first()

                if existing_order:
                    if update_existing:
                        # 기존 레코드 업데이트
                        updated = False

                        # 변경된 필드만 업데이트
                        fields_to_check = [
                            ('sName', row.get('name', '')),
                            ('sPhone', row.get('phone', '')),
                            ('sArea', row.get('area', '')),
                            ('sConstruction', row.get('construction', '')),
                        ]

                        for field_name, new_value in fields_to_check:
                            old_value = getattr(existing_order, field_name, '')
                            if str(old_value) != str(new_value):
                                setattr(existing_order, field_name, new_value)
                                updated = True

                        if updated:
                            existing_order.save()
                            updated_count += 1
                            logger.info(f"레코드 업데이트: {sheet_uuid}")
                        else:
                            skipped_count += 1
                    else:
                        # 이미 존재하는 경우 스킵
                        skipped_count += 1
                        logger.debug(f"이미 존재하는 UUID: {sheet_uuid}")
                    continue

                # 지정 타입 결정
                designation_value = row.get('designation', '')
                if '공동구매' in designation_value:
                    designation_type = '공동구매'
                elif '열린업체' in designation_value or designation_value:
                    designation_type = '업체지정'
                else:
                    designation_type = '지정없음'

                # 새 레코드 생성
                order_data = {
                    'google_sheet_uuid': sheet_uuid,
                    'designation': row.get('designation', ''),  # C열: 지정 내용
                    'designation_type': designation_type,
                    'sNick': row.get('nick', ''),  # D열: 별명
                    'sNaverID': row.get('naver_id', ''),  # E열: Naver 아이디
                    'sName': row.get('name', ''),  # F열: 이름
                    'sPhone': row.get('phone', ''),  # G열: 전화번호
                    'sPost': row.get('post', ''),  # H열: 견적의뢰게시글
                    'post_link': row.get('post', ''),  # H열을 링크로도 저장
                    'sArea': row.get('area', ''),  # I열: 공사지역
                    'dateSchedule': self.parse_date(row.get('schedule_date', '')),  # J열: 공사예정일
                    'sConstruction': row.get('construction', ''),  # K열: 공사내용
                    'bPrivacy1': self.parse_boolean(row.get('privacy1', '')),
                    'bPrivacy2': self.parse_boolean(row.get('privacy2', '')),
                    'recent_status': '대기중',
                    'assigned_company': '',
                }

                # 타임스탬프 처리 (한국 날짜 형식)
                timestamp_str = row.get('timestamp', '')
                if timestamp_str:
                    try:
                        # 다양한 타임스탬프 형식 처리
                        # 예: "2025. 9. 16 오전 12:12:46"
                        import re
                        # 한국어 오전/오후 처리
                        timestamp_str = timestamp_str.replace('오전', 'AM').replace('오후', 'PM')
                        # 점 제거
                        timestamp_str = re.sub(r'(\d+)\. (\d+)\. (\d+)', r'\1/\2/\3', timestamp_str)

                        # 여러 형식 시도
                        for fmt in ['%Y/%m/%d %p %I:%M:%S', '%Y/%m/%d %H:%M:%S', '%m/%d/%Y %H:%M:%S']:
                            try:
                                order_data['time'] = datetime.strptime(timestamp_str, fmt)
                                break
                            except:
                                continue
                    except Exception as e:
                        logger.warning(f"타임스탬프 파싱 실패: {timestamp_str} - {str(e)}")

                Order.objects.create(**order_data)
                created_count += 1
                logger.info(f"새 의뢰 생성: {sheet_uuid}")

            except Exception as e:
                logger.error(f"행 처리 오류: {str(e)}, UUID: {row.get('uuid_col', 'Unknown')}")
                continue

        # 동기화 시간 업데이트
        cache.set('last_google_sync_time', datetime.now(), None)

        result = {
            'created': created_count,
            'updated': updated_count,
            'skipped': skipped_count,
            'invalid': invalid_count,
            'total': len(sheet_data),
            'sync_time': datetime.now().isoformat()
        }

        # 새 접수 건이 있으면 로그 강조
        if created_count > 0:
            logger.warning(f"⚡ 새로운 접수 {created_count}건 동기화 완료!")

        logger.info(f"동기화 완료: {result}")
        return result

    def generate_uuid_for_new_entries(self):
        """스프레드시트의 새 항목에 UUID 생성 (수동 작업용)"""
        # 이 기능은 구글 앱스 스크립트나 별도 도구로 구현
        # 여기서는 UUID 생성 예시만 제공
        return str(uuid.uuid4())