# contract/webhook_views.py
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.conf import settings
import json
import logging
from datetime import datetime
from .models import ClientReport, CompanyReport
from company.models import Company
from .utils import process_google_sheet_row

logger = logging.getLogger(__name__)

@csrf_exempt
@require_http_methods(["POST"])
def clientreport_webhook(request):
    """
    Google Apps Script에서 보낸 데이터를 받아 ClientReport 모델에 저장
    """
    # 인증 토큰 확인
    auth_header = request.headers.get('Authorization', '')
    expected_token = f"Bearer {getattr(settings, 'GOOGLE_SHEETS_WEBHOOK_TOKEN', 'testpark-google-sheets-webhook-2024')}"

    if auth_header != expected_token:
        logger.warning(f"Unauthorized webhook access attempt from {request.META.get('REMOTE_ADDR')}")
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    try:
        # JSON 데이터 파싱
        data = json.loads(request.body)
        logger.info(f"Received ClientReport data from Google Sheets: {data}")

        # 구글 시트에서 받은 원본 텍스트 데이터들
        s_timestamp = data.get('sTimeStamp', '')
        s_company_name = data.get('sCompanyName', '')
        s_date_contract = data.get('sDateContract', '')

        # 타임스탬프 변환 처리
        timestamp = None
        if s_timestamp:
            try:
                import re
                # 한국어 날짜 형식 처리 (예: "2025. 10. 11 오후 3:45:20")
                if '. ' in s_timestamp and ('오전' in s_timestamp or '오후' in s_timestamp):
                    # 날짜와 시간 분리
                    parts = s_timestamp.split(' ')
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

                        timestamp = datetime(year, month, day, hour, minute, second)
                        logger.info(f"Successfully parsed Korean timestamp format: {s_timestamp} -> {timestamp}")

                # 기타 형식 처리
                if not timestamp:
                    for fmt in ['%Y-%m-%d %H:%M:%S', '%Y/%m/%d %H:%M:%S', '%m/%d/%Y %H:%M:%S']:
                        try:
                            timestamp = datetime.strptime(s_timestamp, fmt)
                            logger.info(f"Successfully parsed timestamp with format {fmt}: {s_timestamp} -> {timestamp}")
                            break
                        except ValueError:
                            continue

                if not timestamp:
                    logger.warning(f"Could not parse timestamp with any format: {s_timestamp}")
            except Exception as e:
                logger.error(f"Error parsing timestamp '{s_timestamp}': {str(e)}")

        # 업체명으로 Company 찾기
        company_no = 0  # 기본값
        if s_company_name:
            try:
                # sName2와 sName3로만 검색
                company = Company.objects.filter(
                    sName2=s_company_name
                ).first() or Company.objects.filter(
                    sName3=s_company_name
                ).first()

                if company:
                    company_no = company.no
                    logger.info(f"Found company: {company.no} for name: {s_company_name}")
                else:
                    logger.warning(f"Company not found for name: {s_company_name}, using default value 0")
            except Exception as e:
                logger.error(f"Error searching company: {str(e)}")

        # 계약일 변환 처리
        date_contract = None
        if s_date_contract:
            try:
                import re
                # 한국어 날짜 형식 처리 (예: "2025. 10. 11")
                if '. ' in s_date_contract:
                    date_match = re.match(r'(\d{4})\.\s*(\d{1,2})\.\s*(\d{1,2})', s_date_contract)
                    if date_match:
                        year = int(date_match.group(1))
                        month = int(date_match.group(2))
                        day = int(date_match.group(3))
                        date_contract = datetime(year, month, day).date()
                        logger.info(f"Successfully parsed Korean date format: {s_date_contract} -> {date_contract}")

                # 기타 날짜 형식 처리
                if not date_contract:
                    for fmt in ['%Y-%m-%d', '%Y/%m/%d', '%m/%d/%Y', '%Y년 %m월 %d일']:
                        try:
                            date_contract = datetime.strptime(s_date_contract, fmt).date()
                            logger.info(f"Successfully parsed date with format {fmt}: {s_date_contract} -> {date_contract}")
                            break
                        except ValueError:
                            continue

                if not date_contract:
                    logger.warning(f"Could not parse contract date with any format: {s_date_contract}")
            except Exception as e:
                logger.error(f"Error parsing contract date '{s_date_contract}': {str(e)}")

        # ClientReport 객체 생성 - 원본 텍스트 필드와 변환된 필드 모두 저장
        client_report = ClientReport(
            # 구글 시트 원본 텍스트 필드들
            sTimeStamp=s_timestamp,
            sCompanyName=s_company_name,
            sName=data.get('sName', ''),
            sArea=data.get('sArea', ''),
            sPhone=data.get('sPhone', ''),
            sConMoney=data.get('sConMoney', ''),
            sDateContract=s_date_contract,
            sFile=data.get('sFile', ''),
            sClientMemo=data.get('sClientMemo', ''),

            # 변환된 필드들
            timeStamp=timestamp,
            noCompany=company_no,
            dateContract=date_contract,

            # 기타 필드들
            sPost='',
            noAssign=None,
            noCompanyReport=None,
            nCheck=0,
            sMemo=''
        )

        client_report.save()
        logger.info(f"Successfully created ClientReport record: {client_report.no}")

        # 성공 응답
        response_data = {
            'success': True,
            'report_id': client_report.no,
            'company_no': company_no,
            'message': '고객계약보고 데이터가 성공적으로 저장되었습니다.'
        }

        # 업체를 찾지 못한 경우 경고 추가
        if company_no == 0 and s_company_name:
            response_data['warning'] = f'업체명 "{s_company_name}"을 찾을 수 없어 업체ID가 0으로 설정되었습니다.'

        return JsonResponse(response_data)

    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {str(e)}")
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def test_clientreport_webhook(request):
    """
    ClientReport webhook 테스트용 엔드포인트
    """
    try:
        # 테스트 데이터 생성
        test_data = {
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "sCompanyName": "테스트업체",
            "sName": "테스트고객",
            "sPhone": "010-1234-5678",
            "sArea": "서울시 강남구",
            "dateContract": "2024-01-15",
            "sConMoney": "5000000",
            "sClientMemo": "테스트 메모입니다."
        }

        logger.info(f"Test webhook called with data: {test_data}")

        # 실제 webhook 호출
        request._body = json.dumps(test_data).encode('utf-8')
        request.META['HTTP_AUTHORIZATION'] = f"Bearer {getattr(settings, 'GOOGLE_SHEETS_WEBHOOK_TOKEN', 'testpark-google-sheets-webhook-2024')}"

        return clientreport_webhook(request)

    except Exception as e:
        logger.error(f"Test webhook error: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def companyreport_webhook(request):
    """
    Google Apps Script에서 보낸 데이터를 받아 CompanyReport 모델에 저장

    예상 데이터 형식:
    {
        "sTimeStamp": "2025. 10. 11 오후 3:45:20",
        "sCompanyName": "서울1호",
        "sName": "홍길동",
        "sPhone": "010-1234-5678",
        "sPost": "123456",
        "sDateContract": "2025. 10. 1",
        "sDateSchedule": "2025. 10. 30",
        "sConMoney": "50,000,000",
        "sCompanyMemo": "메모",
        "sFile": "https://..."
    }
    """
    # 인증 토큰 확인
    auth_header = request.headers.get('Authorization', '')
    expected_token = f"Bearer {getattr(settings, 'GOOGLE_SHEETS_WEBHOOK_TOKEN', 'testpark-google-sheets-webhook-2024')}"

    if auth_header != expected_token:
        logger.warning(f"Unauthorized webhook access attempt from {request.META.get('REMOTE_ADDR')}")
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    try:
        # JSON 데이터 파싱
        data = json.loads(request.body)
        logger.info(f"Received CompanyReport data from Google Sheets: {data}")

        # process_google_sheet_row 함수 사용하여 데이터 처리
        report = process_google_sheet_row(data)

        if report:
            # 성공 응답
            response_data = {
                'success': True,
                'report_id': report.no,
                'company_no': report.noCompany,
                'company_name': report.sCompanyName,
                'customer_name': report.sName,
                'contract_money': report.nConMoney,
                'message': '업체계약보고 데이터가 성공적으로 저장되었습니다.'
            }

            # 업체를 찾지 못한 경우 경고 추가
            if report.noCompany == 0 and report.sCompanyName:
                response_data['warning'] = f'업체명 "{report.sCompanyName}"을 찾을 수 없어 업체ID가 0으로 설정되었습니다.'

            return JsonResponse(response_data)
        else:
            return JsonResponse({
                'error': 'Failed to create CompanyReport',
                'message': '데이터 처리 중 오류가 발생했습니다.'
            }, status=400)

    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {str(e)}")
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def test_companyreport_webhook(request):
    """
    CompanyReport webhook 테스트용 엔드포인트
    """
    try:
        # 테스트 데이터 생성 (구글 시트 형식)
        test_data = {
            "sTimeStamp": "2025. 10. 11 오후 3:45:20",
            "sCompanyName": "서울1호",
            "sName": "테스트고객",
            "sPhone": "010-1234-5678",
            "sPost": "123456",
            "sDateContract": "2025. 10. 1",
            "sDateSchedule": "2025. 10. 30",
            "sConMoney": "50,000,000",
            "sCompanyMemo": "테스트 메모입니다.",
            "sFile": "https://drive.google.com/file/d/test"
        }

        logger.info(f"Test CompanyReport webhook called with data: {test_data}")

        # 실제 webhook 호출
        request._body = json.dumps(test_data).encode('utf-8')
        request.META['HTTP_AUTHORIZATION'] = f"Bearer {getattr(settings, 'GOOGLE_SHEETS_WEBHOOK_TOKEN', 'testpark-google-sheets-webhook-2024')}"

        return companyreport_webhook(request)

    except Exception as e:
        logger.error(f"Test webhook error: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)