from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db import transaction
from django.db.models import Q
import json
import logging
from datetime import datetime
from .models import Satisfy, Complain
from company.models import Company

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["POST"])
def google_sheets_webhook(request):
    """구글 시트에서 전송된 고객만족도 데이터 처리"""

    # 요청 정보 로깅
    logger.info("=" * 50)
    logger.info("고객만족도 웹훅 요청 수신")
    logger.info(f"Request Method: {request.method}")
    logger.info(f"Request Headers: {dict(request.headers)}")
    logger.info(f"Request Path: {request.path}")
    logger.info(f"Content Length: {request.headers.get('Content-Length', 'N/A')}")

    try:
        # 인증 확인
        auth_header = request.headers.get('Authorization', '')
        expected_token = 'Bearer testpark-google-sheets-webhook-2024'

        if auth_header != expected_token:
            logger.warning(f"Unauthorized webhook access attempt - received: {auth_header}")
            return JsonResponse({
                'success': False,
                'error': 'Unauthorized'
            }, status=401)

        # 요청 데이터 파싱
        data = json.loads(request.body)
        logger.info(f"Received webhook data: {data}")

        # 데이터 검증
        required_fields = ['sTimeStamp', 'sCompanyName']
        for field in required_fields:
            if not data.get(field):
                return JsonResponse({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }, status=400)

        # 타임스탬프 처리
        timestamp_str = data.get('sTimeStamp', '')
        timestamp_dt = None
        if timestamp_str:
            try:
                # 구글 시트 타임스탬프 형식: "2024. 12. 25. 오후 3:30:45" 또는 "12/25/2024 15:30:45"
                for fmt in [
                    '%Y. %m. %d. %p %I:%M:%S',  # 한국어 형식
                    '%Y. %m. %d. 오전 %I:%M:%S',
                    '%Y. %m. %d. 오후 %I:%M:%S',
                    '%m/%d/%Y %H:%M:%S',  # 영어 형식
                    '%Y-%m-%d %H:%M:%S'   # ISO 형식
                ]:
                    try:
                        if '오전' in timestamp_str:
                            timestamp_str_clean = timestamp_str.replace('오전', 'AM')
                            timestamp_dt = datetime.strptime(timestamp_str_clean, '%Y. %m. %d. %p %I:%M:%S')
                        elif '오후' in timestamp_str:
                            timestamp_str_clean = timestamp_str.replace('오후', 'PM')
                            timestamp_dt = datetime.strptime(timestamp_str_clean, '%Y. %m. %d. %p %I:%M:%S')
                        else:
                            timestamp_dt = datetime.strptime(timestamp_str, fmt)
                        break
                    except ValueError:
                        continue
            except Exception as e:
                logger.error(f"Timestamp parsing error: {e}")

        # 업체 매칭
        company_name = data.get('sCompanyName', '')
        company_no = 0

        if company_name:
            try:
                # 업체명으로 검색 (sName1, sName2, sName3 확인)
                company = Company.objects.filter(
                    Q(sName1=company_name) |
                    Q(sName2=company_name) |
                    Q(sName3=company_name)
                ).first()

                if company:
                    company_no = company.no
                    logger.info(f"Matched company: {company_name} -> {company_no}")
                else:
                    logger.warning(f"Company not found: {company_name}")
            except Exception as e:
                logger.error(f"Company matching error: {e}")

        # Satisfy 객체 생성
        with transaction.atomic():
            satisfy = Satisfy(
                sTimeStamp=timestamp_str,
                timeStamp=timestamp_dt,
                sCompanyName=company_name,
                noCompany=company_no,
                sPhone=data.get('sPhone', ''),
                sConMoney=data.get('sConMoney', ''),
                sArea=data.get('sArea', ''),
                # 만족도 평가 항목 (텍스트)
                sS1=data.get('sS1', '보통'),
                sS2=data.get('sS2', '보통'),
                sS3=data.get('sS3', '보통'),
                sS4=data.get('sS4', '보통'),
                sS5=data.get('sS5', '보통'),
                sS6=data.get('sS6', '보통'),
                sS7=data.get('sS7', '보통'),
                sS8=data.get('sS8', '보통'),
                sS9=data.get('sS9', '보통'),
                sS10=data.get('sS10', '보통'),
                sS11=data.get('sS11', '')  # 추가의견
            )

            # 만족도 합계 자동 계산 (save 메서드에서 처리됨)
            satisfy.save()

            logger.info(f"Created Satisfy record: {satisfy.no}")

            return JsonResponse({
                'success': True,
                'message': 'Data received and processed successfully',
                'satisfy_id': satisfy.no,
                'company_matched': company_no > 0,
                'satisfaction_sum': satisfy.fSatisfySum
            })

    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON format'
        }, status=400)

    except Exception as e:
        logger.error(f"Webhook processing error: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET", "POST"])
def test_webhook(request):
    """Webhook 테스트 엔드포인트"""

    if request.method == 'GET':
        # GET 요청으로 연결 테스트
        return JsonResponse({
            'status': 'active',
            'message': 'Google Sheets webhook endpoint is ready',
            'endpoint': '/evaluation/webhook/google-sheets/',
            'method': 'POST',
            'required_headers': {
                'Authorization': 'Bearer testpark-google-sheets-webhook-2024',
                'Content-Type': 'application/json'
            }
        })

    elif request.method == 'POST':
        # POST 요청으로 테스트 데이터 처리
        try:
            data = json.loads(request.body) if request.body else {}

            # 테스트 데이터 생성
            test_data = {
                'sTimeStamp': '2024. 12. 26. 오후 3:30:45',
                'sCompanyName': '테스트업체',
                'sPhone': '010-1234-5678',
                'sConMoney': '1,000,000원',
                'sArea': '서울시 강남구',
                'sS1': '매우 만족',
                'sS2': '만족',
                'sS3': '보통',
                'sS4': '만족',
                'sS5': '매우 만족',
                'sS6': '만족',
                'sS7': '보통',
                'sS8': '만족',
                'sS9': '매우 만족',
                'sS10': '만족',
                'sS11': '테스트 추가의견입니다.'
            }

            # 실제 데이터가 전송되었으면 그것을 사용
            if data:
                test_data.update(data)

            return JsonResponse({
                'success': True,
                'message': 'Test webhook received',
                'received_data': test_data,
                'timestamp': datetime.now().isoformat()
            })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def google_sheets_webhook_complain(request):
    """구글 시트에서 전송된 고객불만 데이터 처리"""

    try:
        # 인증 확인
        auth_header = request.headers.get('Authorization', '')
        expected_token = 'Bearer testpark-google-sheets-webhook-2024'

        if auth_header != expected_token:
            logger.warning(f"Unauthorized webhook access attempt for complain")
            return JsonResponse({
                'success': False,
                'error': 'Unauthorized'
            }, status=401)

        # 요청 데이터 파싱
        data = json.loads(request.body)
        logger.info(f"Received complain webhook data: {data}")

        # 타임스탬프 처리
        timestamp_str = data.get('sTimeStamp', '')
        timestamp_dt = None
        if timestamp_str:
            try:
                for fmt in [
                    '%Y. %m. %d. %p %I:%M:%S',
                    '%Y. %m. %d. 오전 %I:%M:%S',
                    '%Y. %m. %d. 오후 %I:%M:%S',
                    '%m/%d/%Y %H:%M:%S',
                    '%Y-%m-%d %H:%M:%S'
                ]:
                    try:
                        if '오전' in timestamp_str:
                            timestamp_str_clean = timestamp_str.replace('오전', 'AM')
                            timestamp_dt = datetime.strptime(timestamp_str_clean, '%Y. %m. %d. %p %I:%M:%S')
                        elif '오후' in timestamp_str:
                            timestamp_str_clean = timestamp_str.replace('오후', 'PM')
                            timestamp_dt = datetime.strptime(timestamp_str_clean, '%Y. %m. %d. %p %I:%M:%S')
                        else:
                            timestamp_dt = datetime.strptime(timestamp_str, fmt)
                        break
                    except ValueError:
                        continue
            except Exception as e:
                logger.error(f"Timestamp parsing error: {e}")

        # 업체명 매칭
        company_name = data.get('sCompanyName', '')
        company_no = 0

        if company_name:
            try:
                company = Company.objects.filter(
                    Q(sName1=company_name) |
                    Q(sName2=company_name) |
                    Q(sName3=company_name)
                ).first()

                if company:
                    company_no = company.no
                    logger.info(f"Matched company for complain: {company_name} -> {company_no}")
                else:
                    logger.warning(f"Company not found for complain: {company_name}")
            except Exception as e:
                logger.error(f"Company matching error: {e}")

        # Complain 객체 생성
        with transaction.atomic():
            complain = Complain(
                sTimeStamp=timestamp_str,
                timeStamp=timestamp_dt,
                sCompanyName=company_name,
                noCompany=company_no,
                sPass=data.get('sPass', ''),
                sComplain=data.get('sComplain', ''),
                sComplainPost=data.get('sComplainPost', ''),
                sPost=data.get('sPost', ''),
                sSMSBool=data.get('sSMSBool', ''),
                sSMSMent=data.get('sSMSMent', ''),
                sFile=data.get('sFile', ''),
                sCheck=data.get('sCheck', ''),
                sWorker=data.get('sWorker', ''),
                fComplain=0.2  # 강제로 0.2로 설정
            )

            complain.save()
            logger.info(f"Created Complain record: {complain.no}")

            return JsonResponse({
                'success': True,
                'message': 'Complain data received and processed successfully',
                'complain_id': complain.no,
                'company_matched': company_no > 0
            })

    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON format'
        }, status=400)

    except Exception as e:
        logger.error(f"Complain webhook processing error: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)