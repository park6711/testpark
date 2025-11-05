"""
구글 시트 데이터 변환 유틸리티
CompanyReport 데이터 변환 로직
"""

import re
from datetime import datetime
from django.utils import timezone
from company.models import Company


def parse_timestamp(timestamp_str):
    """
    구글 시트 타임스탬프 문자열을 datetime 객체로 변환

    Args:
        timestamp_str: "2025. 10. 11 오후 3:45:20" 형식의 문자열

    Returns:
        datetime 객체 또는 None
    """
    if not timestamp_str:
        return None

    try:
        # 한국어 날짜 형식 처리 (예: "2025. 10. 11 오후 3:45:20")
        if '. ' in timestamp_str and ('오전' in timestamp_str or '오후' in timestamp_str):
            # 날짜와 시간 분리
            parts = timestamp_str.split(' ')
            if len(parts) >= 5:
                year = int(parts[0].rstrip('.'))
                month = int(parts[1].rstrip('.'))
                day = int(parts[2])
                am_pm = parts[3]
                time_str = parts[4]

                # 시간 파싱
                time_parts = time_str.split(':')
                hour = int(time_parts[0])
                minute = int(time_parts[1]) if len(time_parts) > 1 else 0
                second = int(time_parts[2]) if len(time_parts) > 2 else 0

                # 오후인 경우 12시간 추가 (12시 제외)
                if am_pm == '오후' and hour != 12:
                    hour += 12
                elif am_pm == '오전' and hour == 12:
                    hour = 0

                # datetime 생성 (timezone aware)
                dt = datetime(year, month, day, hour, minute, second)
                return timezone.make_aware(dt)

        # 다른 형식들 시도
        formats = [
            '%Y-%m-%d %H:%M:%S',
            '%Y/%m/%d %H:%M:%S',
            '%m/%d/%Y %H:%M:%S',
            '%Y년 %m월 %d일 %H시 %M분 %S초',
        ]

        for fmt in formats:
            try:
                dt = datetime.strptime(timestamp_str, fmt)
                return timezone.make_aware(dt)
            except:
                continue

    except Exception as e:
        print(f"타임스탬프 파싱 오류: {timestamp_str} - {e}")

    return None


def parse_date(date_str):
    """
    구글 시트 날짜 문자열을 date 객체로 변환

    Args:
        date_str: "2025. 10. 11" 형식의 문자열

    Returns:
        date 객체 또는 None
    """
    if not date_str:
        return None

    try:
        # 한국어 날짜 형식 처리 (예: "2025. 10. 11")
        if '. ' in date_str:
            date_match = re.match(r'(\d{4})\.\s*(\d{1,2})\.\s*(\d{1,2})', date_str)
            if date_match:
                year = int(date_match.group(1))
                month = int(date_match.group(2))
                day = int(date_match.group(3))
                return datetime(year, month, day).date()

        # 다른 형식들 시도
        formats = [
            '%Y-%m-%d',
            '%Y/%m/%d',
            '%m/%d/%Y',
            '%Y년 %m월 %d일',
        ]

        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt).date()
            except:
                continue

    except Exception as e:
        print(f"날짜 파싱 오류: {date_str} - {e}")

    return None


def parse_money(money_str):
    """
    구글 시트 금액 문자열을 정수로 변환

    Args:
        money_str: "1,234,567", "1234567원", "1,234,567 원" 등의 문자열

    Returns:
        정수 금액 또는 0
    """
    if not money_str:
        return 0

    try:
        # 문자열로 변환
        money_str = str(money_str)

        # 숫자와 관련 없는 문자 제거
        # 콤마, 원, 공백, Won, KRW 등 제거
        cleaned = re.sub(r'[^0-9.-]', '', money_str)

        # 빈 문자열이면 0 반환
        if not cleaned:
            return 0

        # 정수로 변환
        return int(float(cleaned))

    except Exception as e:
        print(f"금액 파싱 오류: {money_str} - {e}")
        return 0


def find_company_by_name(company_name):
    """
    회사명으로 Company 찾기
    sName2와 sName3를 확인하여 매칭

    Args:
        company_name: 회사명 문자열

    Returns:
        Company.no 또는 None
    """
    if not company_name:
        return None

    try:
        # 정확히 일치하는 경우 먼저 확인
        company = Company.objects.filter(sName2=company_name).first()
        if company:
            return company.no

        company = Company.objects.filter(sName3=company_name).first()
        if company:
            return company.no

        # 부분 일치 확인
        company = Company.objects.filter(sName2__icontains=company_name).first()
        if company:
            return company.no

        company = Company.objects.filter(sName3__icontains=company_name).first()
        if company:
            return company.no

        # 역방향 부분 일치 (입력된 이름이 DB 이름을 포함)
        for comp in Company.objects.all():
            if comp.sName2 and comp.sName2 in company_name:
                return comp.no
            if comp.sName3 and comp.sName3 in company_name:
                return comp.no

    except Exception as e:
        print(f"회사 검색 오류: {company_name} - {e}")

    return None


def convert_google_sheet_to_company_report(sheet_data):
    """
    구글 시트 데이터를 CompanyReport 모델 필드로 변환

    Args:
        sheet_data: 구글 시트에서 받은 딕셔너리 데이터
            {
                'sTimeStamp': '2025. 10. 11 오후 3:45:20',
                'sCompanyName': '서울1호',
                'sName': '홍길동',
                'sPhone': '010-1234-5678',
                'sPost': '123456',
                'sDateContract': '2025. 10. 1',
                'sDateSchedule': '2025. 10. 30',
                'sConMoney': '50,000,000',
                'sCompanyMemo': '메모',
                'sFile': 'https://...'
            }

    Returns:
        CompanyReport 생성용 딕셔너리
    """

    converted_data = {}

    # 원본 텍스트 필드 그대로 저장
    converted_data['sTimeStamp'] = sheet_data.get('sTimeStamp', '')
    converted_data['sCompanyName'] = sheet_data.get('sCompanyName', '')
    converted_data['sName'] = sheet_data.get('sName', '')
    converted_data['sPhone'] = sheet_data.get('sPhone', '')
    converted_data['sPost'] = sheet_data.get('sPost', '')
    converted_data['sDateContract'] = sheet_data.get('sDateContract', '')
    converted_data['sDateSchedule'] = sheet_data.get('sDateSchedule', '')
    converted_data['sConMoney'] = sheet_data.get('sConMoney', '')
    converted_data['sCompanyMemo'] = sheet_data.get('sCompanyMemo', '')
    converted_data['sFile'] = sheet_data.get('sFile', '')

    # 변환 필드
    # 1. 타임스탬프 변환
    converted_data['timeStamp'] = parse_timestamp(converted_data['sTimeStamp'])

    # 2. 회사 ID 찾기
    converted_data['noCompany'] = find_company_by_name(converted_data['sCompanyName'])
    if not converted_data['noCompany']:
        # 회사를 찾지 못한 경우 기본값 설정 (예: 0 또는 특정 회사)
        converted_data['noCompany'] = 0
        print(f"경고: '{converted_data['sCompanyName']}' 회사를 찾을 수 없습니다.")

    # 3. 날짜 변환
    converted_data['dateContract'] = parse_date(converted_data['sDateContract'])
    converted_data['dateSchedule'] = parse_date(converted_data['sDateSchedule'])

    # 4. 금액 변환
    converted_data['nConMoney'] = parse_money(converted_data['sConMoney'])

    # 기본값 설정 (구글 시트에 없는 필드들)
    converted_data['nType'] = 0  # 가계약 (기본값)
    converted_data['nConType'] = 0  # 카페건-인테리어 (기본값)
    converted_data['sArea'] = ''  # 주소 (필요시 추가)
    converted_data['bVat'] = False  # VAT 미포함 (기본값)
    converted_data['nFee'] = 0
    converted_data['nAppPoint'] = 0
    converted_data['nDemand'] = 0
    converted_data['nDeposit'] = 0
    converted_data['nExcess'] = 0
    converted_data['nRefund'] = 0
    converted_data['sTaxCompany'] = ''
    converted_data['sAccount'] = ''
    converted_data['sStaffMemo'] = ''
    converted_data['sWorker'] = '구글시트'

    return converted_data


def process_google_sheet_row(row_data):
    """
    구글 시트의 한 행 데이터를 처리하여 CompanyReport 생성

    Args:
        row_data: 구글 시트 행 데이터 (리스트 또는 딕셔너리)

    Returns:
        생성된 CompanyReport 객체 또는 None
    """
    from contract.models import CompanyReport

    try:
        # 리스트인 경우 딕셔너리로 변환 (컬럼 인덱스 매핑)
        if isinstance(row_data, list):
            sheet_dict = {
                'sTimeStamp': row_data[0] if len(row_data) > 0 else '',
                'sCompanyName': row_data[1] if len(row_data) > 1 else '',
                'sName': row_data[2] if len(row_data) > 2 else '',
                'sPhone': row_data[3] if len(row_data) > 3 else '',
                'sPost': row_data[4] if len(row_data) > 4 else '',
                # 5, 6번 컬럼은 게시글, 주소 (현재 미사용)
                'sDateContract': row_data[7] if len(row_data) > 7 else '',
                'sDateSchedule': row_data[8] if len(row_data) > 8 else '',
                'sConMoney': row_data[9] if len(row_data) > 9 else '',
                # 10-19번 컬럼은 회비, 잔액 등 (현재 미사용)
                'sCompanyMemo': row_data[20] if len(row_data) > 20 else '',
                'sFile': row_data[21] if len(row_data) > 21 else '',
            }
        else:
            sheet_dict = row_data

        # 데이터 변환
        converted = convert_google_sheet_to_company_report(sheet_dict)

        # CompanyReport 생성
        report = CompanyReport.objects.create(**converted)
        print(f"CompanyReport 생성 성공: ID={report.no}, 회사={report.sCompanyName}, 고객={report.sName}")

        return report

    except Exception as e:
        print(f"CompanyReport 생성 실패: {e}")
        import traceback
        traceback.print_exc()
        return None