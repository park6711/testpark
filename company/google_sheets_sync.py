# 구글 스프레드시트 동기화 서비스 (Company)
import os
import json
import uuid
import re
from datetime import datetime
import logging
from typing import List, Dict, Any
from django.conf import settings
from django.db import transaction
from django.core.cache import cache
from .models import Company
import gspread
from oauth2client.service_account import ServiceAccountCredentials

logger = logging.getLogger(__name__)

# 기본 경로 설정
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CREDENTIALS_PATH = os.path.join(BASE_DIR, 'seongdal-a900e25ac63c.json')

class CompanySheetsSync:
    """구글 스프레드시트와 Django 데이터베이스(Company)를 동기화하는 서비스"""

    def __init__(self):
        # 구글 스프레드시트 ID와 시트 설정
        self.spreadsheet_id = '1IB7YbVJcEpwcKmCGDsfmRaSIjdZQdy9NSDB6N7Gqf78'
        self.sheet_name = '열린/단종업체 (1906~)'

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
            credentials = ServiceAccountCredentials.from_json_keyfile_name(
                CREDENTIALS_PATH, self.scope)
            self.client = gspread.authorize(credentials)
            self.sheet = self.client.open_by_key(self.spreadsheet_id)
            logger.info(f"구글 스프레드시트 인증 성공: {self.sheet_name}")
        except Exception as e:
            logger.error(f"구글 스프레드시트 인증 실패: {str(e)}")
            raise

    def _is_valid_uuid(self, value: str) -> bool:
        """UUID 형식이 유효한지 검사"""
        if not value or not value.strip():
            return False
        try:
            uuid.UUID(value.strip())
            return True
        except ValueError:
            return False

    def _generate_uuid(self) -> str:
        """새 UUID 생성"""
        return str(uuid.uuid4())

    def fetch_sheet_data(self) -> List[Dict[str, Any]]:
        """구글 스프레드시트에서 업체 데이터 가져오기

        규칙1: 2행에 데이터베이스 클래스 이름 기록, x 및 빈칸은 무시
        규칙2: C열 "탈퇴" 포함 되어 있거나 "호"가 존재하지 않는 행은 무시
        규칙3: BK열 UUID 열로 빈칸이거나 UUID 형식이 아닌 경우 UUID 생성
        """
        try:
            if not self.sheet:
                self._authenticate()

            worksheet = self.sheet.worksheet(self.sheet_name)
            all_values = worksheet.get_all_values()

            if len(all_values) < 3:
                logger.warning("스프레드시트 데이터 부족 (최소 3행 필요)")
                return []

            # 2행: 필드명 헤더 (인덱스 1)
            header_row = all_values[1]

            # 3행부터 데이터 (인덱스 2부터)
            data_rows = all_values[2:]

            logger.info(f"헤더 컬럼 수: {len(header_row)}, 데이터 행 수: {len(data_rows)}")

            # 필드 매핑 생성 (x 및 빈칸은 무시)
            field_mapping = {}
            for idx, field_name in enumerate(header_row):
                field_name = field_name.strip()
                if field_name and field_name.lower() != 'x':
                    field_mapping[idx] = field_name

            logger.info(f"유효한 필드 매핑: {len(field_mapping)}개")

            result = []
            updated_rows = []  # UUID가 생성/갱신된 행 추적

            for row_idx, row in enumerate(data_rows):
                actual_row_num = row_idx + 3  # 실제 시트 행 번호 (1-based, 헤더 2행 + 현재 인덱스)

                # C열 (인덱스 2) 필터링
                c_column = row[2] if len(row) > 2 else ''

                # 규칙2: "탈퇴" 포함 또는 "호"가 없으면 무시
                if '탈퇴' in c_column:
                    logger.debug(f"행 {actual_row_num}: '탈퇴' 포함으로 건너뜀")
                    continue

                if '호' not in c_column:
                    logger.debug(f"행 {actual_row_num}: '호'가 없어서 건너뜀")
                    continue

                # BK열 (인덱스 62, 63번째 컬럼) - UUID
                uuid_value = row[62] if len(row) > 62 else ''

                # 규칙3: UUID 검증 및 생성
                if not self._is_valid_uuid(uuid_value):
                    # 새 UUID 생성
                    uuid_value = self._generate_uuid()
                    logger.info(f"행 {actual_row_num}: 새 UUID 생성 = {uuid_value}")

                    # UUID를 시트에 쓰기 위해 추적
                    updated_rows.append((actual_row_num, uuid_value))

                # 행 데이터를 딕셔너리로 변환
                row_dict = {'uuid': uuid_value, 'row_number': actual_row_num}

                for col_idx, field_name in field_mapping.items():
                    if col_idx < len(row):
                        row_dict[field_name] = row[col_idx]
                    else:
                        row_dict[field_name] = ''

                result.append(row_dict)

            # UUID를 시트에 다시 쓰기 (배치 업데이트)
            if updated_rows:
                try:
                    # BK열은 63번째 컬럼 (A=1, B=2, ..., BK=63)
                    updates = []
                    for row_num, uuid_val in updated_rows:
                        cell_ref = f'BK{row_num}'
                        updates.append({
                            'range': cell_ref,
                            'values': [[uuid_val]]
                        })

                    worksheet.batch_update(updates)
                    logger.info(f"{len(updated_rows)}개 UUID를 시트에 기록했습니다")
                except Exception as e:
                    logger.error(f"UUID 시트 업데이트 실패: {str(e)}")

            logger.info(f"스프레드시트에서 {len(result)}개 유효한 업체 데이터 가져옴")
            return result

        except Exception as e:
            logger.error(f"스프레드시트 데이터 가져오기 실패: {str(e)}")
            return []

    def parse_date(self, date_str: str):
        """날짜 문자열 파싱"""
        if not date_str:
            return None

        try:
            date_str = date_str.strip()

            # 한국어 날짜 형식 변환: "2018년08월28일" → "2018/08/28"
            date_str = re.sub(r'(\d{4})년\s*(\d{1,2})월\s*(\d{1,2})일', r'\1/\2/\3', date_str)

            # 다양한 날짜 형식 처리
            date_str = re.sub(r'(\d+)\. (\d+)\. (\d+)', r'\1/\2/\3', date_str)

            for fmt in ['%Y/%m/%d', '%Y-%m-%d', '%m/%d/%Y', '%Y. %m. %d', '%Y. %m. %d.']:
                try:
                    return datetime.strptime(date_str, fmt).date()
                except ValueError:
                    continue

            # 변환 실패한 경우만 경고 (너무 많은 로그 방지)
            return None
        except Exception as e:
            return None

    def parse_boolean(self, value: str) -> bool:
        """불린 값 파싱"""
        if not value:
            return False
        value_lower = str(value).lower().strip()
        return value_lower in ['true', 'yes', '예', '동의', '1', 'o', 'v']

    def parse_integer(self, value: str, default=0) -> int:
        """정수 파싱"""
        if not value:
            return default
        try:
            # 쉼표 제거 후 정수 변환
            cleaned = str(value).replace(',', '').replace(' ', '').strip()
            return int(float(cleaned))
        except (ValueError, TypeError):
            return default

    def parse_float(self, value: str, default=0.0) -> float:
        """실수 파싱"""
        if not value:
            return default
        try:
            cleaned = str(value).replace(',', '').replace(' ', '').strip()
            return float(cleaned)
        except (ValueError, TypeError):
            return default

    def sync_data(self, update_existing=False) -> Dict[str, int]:
        """구글 스프레드시트 데이터를 DB와 동기화

        Args:
            update_existing: True면 기존 레코드도 업데이트
        """
        sheet_data = self.fetch_sheet_data()

        created_count = 0
        updated_count = 0
        skipped_count = 0
        error_count = 0

        for row in sheet_data:
            sheet_uuid = row.get('uuid', '').strip()

            if not sheet_uuid:
                skipped_count += 1
                continue

            # sName1 필수 체크 (열린업체명1)
            sname1 = row.get('sName1', '').strip()
            if not sname1:
                skipped_count += 1
                logger.info(f"업체명 부족으로 건너뜀: UUID={sheet_uuid}")
                continue

            # UUID로 기존 레코드 확인
            try:
                existing_company = Company.objects.filter(google_sheet_uuid=sheet_uuid).first()
            except Exception as e:
                logger.error(f"UUID 조회 오류: {str(e)}, UUID: {sheet_uuid}")
                error_count += 1
                continue

            if existing_company:
                if update_existing:
                    # 기존 레코드 업데이트 로직
                    try:
                        with transaction.atomic():
                            # TODO: 업데이트 로직 구현
                            updated_count += 1
                            logger.info(f"레코드 업데이트: {sheet_uuid}")
                    except Exception as e:
                        error_count += 1
                        logger.error(f"레코드 업데이트 오류: {str(e)}, UUID: {sheet_uuid}")
                else:
                    skipped_count += 1
                continue

            # 새 레코드 생성
            try:
                with transaction.atomic():
                    company_data = self._build_company_data(row, sheet_uuid)
                    Company.objects.create(**company_data)
                    created_count += 1
                    logger.info(f"새 업체 생성: {sheet_uuid} - {sname1}")

            except Exception as e:
                error_count += 1
                logger.error(f"행 처리 오류: {str(e)}, UUID: {sheet_uuid}")
                continue

        # 동기화 시간 업데이트
        cache.set('last_company_sync_time', datetime.now(), None)

        result = {
            'created': created_count,
            'updated': updated_count,
            'skipped': skipped_count,
            'errors': error_count,
            'total': len(sheet_data),
            'sync_time': datetime.now().isoformat()
        }

        logger.info(f"Company 동기화 완료: {result}")
        return result

    def _build_company_data(self, row: Dict, sheet_uuid: str) -> Dict:
        """행 데이터로부터 Company 생성용 딕셔너리 구성"""
        # 필드 매핑 (2행의 필드명 → Company 모델 필드)
        # 실제 시트 구조에 맞게 매핑 필요

        return {
            'google_sheet_uuid': sheet_uuid,
            'sName1': row.get('sName1', '')[:100],
            'sName2': row.get('sName2', '')[:100],
            'sName3': row.get('sName3', '')[:100],
            'sNaverID': row.get('sNaverID', '')[:50],
            'noMemberMaster': self.parse_integer(row.get('noMemberMaster')),
            'nType': self.parse_integer(row.get('nType'), 0),
            'nCondition': self.parse_integer(row.get('nCondition'), 0),
            'sCompanyName': row.get('sCompanyName', '')[:200],
            'noLicenseRepresent': self.parse_integer(row.get('noLicenseRepresent')),
            'sAddress': row.get('sAddress', ''),
            'nMember': self.parse_integer(row.get('nMember'), 0),
            'sBuildLicense': row.get('sBuildLicense', '')[:100],
            'sStrength': row.get('sStrength', ''),
            'sCeoName': row.get('sCeoName', '')[:50],
            'sCeoPhone': row.get('sCeoPhone', '')[:20],
            'sCeoMail': row.get('sCeoMail', '')[:254],
            'sSaleName': row.get('sSaleName', '')[:50],
            'sSalePhone': row.get('sSalePhone', '')[:20],
            'sSaleMail': row.get('sSaleMail', '')[:254],
            'sAccoutName': row.get('sAccoutName', '')[:50],
            'sAccoutPhone': row.get('sAccoutPhone', '')[:20],
            'sAccoutMail': row.get('sAccoutMail', '')[:254],
            'sEmergencyName': row.get('sEmergencyName', '')[:50],
            'sEmergencyPhone': row.get('sEmergencyPhone', '')[:20],
            'sEmergencyRelation': row.get('sEmergencyRelation', '')[:50],
            'dateJoin': self.parse_date(row.get('dateJoin')),
            'nJoinFee': self.parse_integer(row.get('nJoinFee'), 0),
            'nDeposit': self.parse_integer(row.get('nDeposit'), 0),
            'nFixFee': self.parse_integer(row.get('nFixFee'), 0),
            'dateFixFeeStart': self.parse_date(row.get('dateFixFeeStart')),
            'fFeePercent': self.parse_float(row.get('fFeePercent'), 0.0),
            'nOrderFee': self.parse_integer(row.get('nOrderFee'), 0),
            'nReportPeriod': self.parse_integer(row.get('nReportPeriod'), 0),
            'bPrivacy': self.parse_boolean(row.get('bPrivacy')),
            'bCompetition': self.parse_boolean(row.get('bCompetition')),
            'bAptAll': self.parse_boolean(row.get('bAptAll')),
            'bAptPart': self.parse_boolean(row.get('bAptPart')),
            'bHouseAll': self.parse_boolean(row.get('bHouseAll')),
            'bHousePart': self.parse_boolean(row.get('bHousePart')),
            'bCommerceAll': self.parse_boolean(row.get('bCommerceAll')),
            'bCommercePart': self.parse_boolean(row.get('bCommercePart')),
            'bBuild': self.parse_boolean(row.get('bBuild')),
            'bExtra': self.parse_boolean(row.get('bExtra')),
            'bUnion': self.parse_boolean(row.get('bUnion')),
            'bMentor': self.parse_boolean(row.get('bMentor')),
            'sMentee': row.get('sMentee', '')[:100],
            'nRefund': self.parse_integer(row.get('nRefund'), 0),
            'sManager': row.get('sManager', '')[:50],
            'dateWithdraw': self.parse_date(row.get('dateWithdraw')),
            'sWithdraw': row.get('sWithdraw', '')[:200],
            'sMemo': row.get('sMemo', ''),
            'sPicture': row.get('sPicture', '')[:200],
            'sGallery': row.get('sGallery', ''),
            'sEstimate': row.get('sEstimate', ''),
            'sStop': row.get('sStop', ''),
            'dateStopStart': self.parse_date(row.get('dateStopStart')),
            'dateStopEnd': self.parse_date(row.get('dateStopEnd')),
            'nLevel': self.parse_integer(row.get('nLevel'), 0),
            'nGrade': self.parse_integer(row.get('nGrade'), 0),
            'nApplyGrade': self.parse_integer(row.get('nApplyGrade'), 0),
            'sApplyGradeReason': row.get('sApplyGradeReason', '')[:200],
            'nAssignAll2': self.parse_integer(row.get('nAssignAll2'), 0),
            'nAssignPart2': self.parse_integer(row.get('nAssignPart2'), 0),
            'nAssignAllTerm': self.parse_integer(row.get('nAssignAllTerm'), 0),
            'nAssignPartTerm': self.parse_integer(row.get('nAssignPartTerm'), 0),
            'nAssignMax': self.parse_integer(row.get('nAssignMax'), 0),
            'fAssignPercent': self.parse_float(row.get('fAssignPercent'), 0.0),
            'fAssignLack': self.parse_float(row.get('fAssignLack'), 0.0),
        }
