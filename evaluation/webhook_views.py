# evaluation/webhook_views.py
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.conf import settings
import json
import logging
from datetime import datetime
from .models import Complain, Satisfy
from company.models import Company

logger = logging.getLogger(__name__)

@csrf_exempt
@require_http_methods(["POST"])
def google_sheets_webhook(request):
    """
    Google Apps Script에서 보낸 데이터를 받아 Complain 모델에 저장
    """
    # 인증 토큰 확인
    auth_header = request.headers.get('Authorization', '')
    expected_token = f"Bearer {getattr(settings, 'GOOGLE_SHEETS_WEBHOOK_TOKEN', 'your-secret-token-here')}"

    if auth_header != expected_token:
        logger.warning(f"Unauthorized webhook access attempt from {request.META.get('REMOTE_ADDR')}")
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    try:
        # JSON 데이터 파싱
        data = json.loads(request.body)
        logger.info(f"Received Google Sheets data: {data}")

        # 업체명으로 Company 찾기
        company_name = data.get('sCompanyName', '')
        company_no = 0  # 기본값 설정 (회사를 찾지 못한 경우)

        if company_name:
            try:
                # sName2, sName1, sName3 순으로 검색
                company = Company.objects.filter(
                    sName2=company_name
                ).first() or Company.objects.filter(
                    sName1=company_name
                ).first() or Company.objects.filter(
                    sName3=company_name
                ).first()

                if company:
                    company_no = company.no
                    logger.info(f"Found company: {company.no} for name: {company_name}")
                else:
                    logger.warning(f"Company not found for name: {company_name}, using default value 0")
                    company_no = 0  # 회사를 찾지 못한 경우 0으로 설정
            except Exception as e:
                logger.error(f"Error searching company: {str(e)}, using default value 0")
                company_no = 0

        # Complain 객체 생성
        complain = Complain(
            sTimeStamp=data.get('sTimeStamp', ''),
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
            fComplain=0.2  # Google Forms에서 들어오는 불만점수는 항상 0.2로 설정
        )

        complain.save()
        logger.info(f"Successfully created Complain record: {complain.no} with fComplain=0.2")

        return JsonResponse({
            'success': True,
            'complain_id': complain.no,
            'fComplain': 0.2,
            'message': '고객불만 데이터가 성공적으로 저장되었습니다. (불만점수: 0.2)'
        })

    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {str(e)}")
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def satisfy_webhook(request):
    """
    Google Apps Script에서 보낸 고객만족도 데이터를 받아 Satisfy 모델에 저장
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
        logger.info(f"Received Satisfy data from Google Sheets: {data}")

        # 구글 시트에서 받은 텍스트 데이터들
        s_timestamp = data.get('sTimeStamp', '')
        s_company_name = data.get('sCompanyName', '')

        # 타임스탬프 변환 처리
        timestamp = None
        if s_timestamp:
            try:
                import re
                # 한국어 날짜 형식 처리 (예: "2025. 9. 28 오후 6:50:46")
                if '. ' in s_timestamp:
                    # 날짜 부분 추출
                    date_match = re.match(r'(\d{4})\.\s*(\d{1,2})\.\s*(\d{1,2})', s_timestamp)
                    if date_match:
                        year = int(date_match.group(1))
                        month = int(date_match.group(2))
                        day = int(date_match.group(3))

                        # 시간 부분 처리
                        time_match = re.search(r'(오전|오후)\s*(\d{1,2}):(\d{2}):(\d{2})', s_timestamp)
                        if time_match:
                            am_pm = time_match.group(1)
                            hour = int(time_match.group(2))
                            minute = int(time_match.group(3))
                            second = int(time_match.group(4))

                            # 오후 시간 조정
                            if am_pm == '오후' and hour < 12:
                                hour += 12
                            elif am_pm == '오전' and hour == 12:
                                hour = 0

                            timestamp = datetime(year, month, day, hour, minute, second)
                        else:
                            timestamp = datetime(year, month, day)
                else:
                    # 다른 형식들 시도
                    for fmt in ['%Y-%m-%d %H:%M:%S', '%Y/%m/%d %H:%M:%S', '%m/%d/%Y %H:%M:%S']:
                        try:
                            timestamp = datetime.strptime(s_timestamp, fmt)
                            break
                        except ValueError:
                            continue
            except Exception as e:
                logger.warning(f"Could not parse timestamp: {s_timestamp}")

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

        # Satisfy 객체 생성
        satisfy = Satisfy(
            # 텍스트 필드들
            sTimeStamp=s_timestamp,
            sCompanyName=s_company_name,
            sPhone=data.get('sPhone', ''),
            sConMoney=data.get('sConMoney', ''),
            sArea=data.get('sArea', ''),

            # 만족도 평가 항목들 (기본값: '보통')
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

            # 추가 필드들
            sS11=data.get('sS11', ''),  # 추가 의견

            # 변환된 필드들
            timeStamp=timestamp,
            noCompany=company_no
        )

        # 만족도 점수 자동 계산 (모델에 calculate_scores 메서드가 있다면)
        if hasattr(satisfy, 'calculate_scores'):
            satisfy.calculate_scores()

        satisfy.save()
        logger.info(f"Successfully created Satisfy record: {satisfy.no}")

        # 성공 응답
        response_data = {
            'success': True,
            'satisfy_id': satisfy.no,
            'company_no': company_no,
            'satisfaction_score': getattr(satisfy, 'fSatisfySum', 0),
            'message': '고객만족도 데이터가 성공적으로 저장되었습니다.'
        }

        # 업체를 찾지 못한 경우 경고 추가
        if company_no == 0 and s_company_name:
            response_data['warning'] = f'업체명 "{s_company_name}"을 찾을 수 없어 업체ID가 0으로 설정되었습니다.'

        return JsonResponse(response_data)

    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {str(e)}")
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        logger.error(f"Error processing satisfy webhook: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def test_satisfy_webhook(request):
    """
    Satisfy webhook 테스트용 엔드포인트
    """
    try:
        # 테스트 데이터 생성
        test_data = {
            "sTimeStamp": "2025. 9. 28 오후 7:00:00",
            "sCompanyName": "테스트업체",
            "sPhone": "010-1234-5678",
            "sConMoney": "5000000",
            "sArea": "서울시 강남구",
            "sS1": "매우 만족",
            "sS2": "만족",
            "sS3": "매우 만족",
            "sS4": "만족",
            "sS5": "매우 만족",
            "sS6": "만족",
            "sS7": "만족",
            "sS8": "매우 만족",
            "sS9": "만족",
            "sS10": "매우 만족",
            "sS11": "테스트 만족도 의견입니다."
        }

        logger.info(f"Test satisfy webhook called with data: {test_data}")

        # 실제 webhook 호출
        request._body = json.dumps(test_data).encode('utf-8')
        request.META['HTTP_AUTHORIZATION'] = f"Bearer {getattr(settings, 'GOOGLE_SHEETS_WEBHOOK_TOKEN', 'testpark-google-sheets-webhook-2024')}"

        return satisfy_webhook(request)

    except Exception as e:
        logger.error(f"Test satisfy webhook error: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def complain_webhook(request):
    """
    Google Apps Script에서 보낸 고객불만 데이터를 받아 Complain 모델에 저장
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
        logger.info(f"Received Complain data from Google Sheets: {data}")

        # 구글 시트에서 받은 텍스트 데이터들
        s_timestamp = data.get('sTimeStamp', '')
        s_company_name = data.get('sCompanyName', '')

        # 타임스탬프 변환 처리
        timestamp = None
        if s_timestamp:
            try:
                import re
                # 한국어 날짜 형식 처리 (예: "2025. 9. 28 오후 6:50:46")
                if '. ' in s_timestamp:
                    # 날짜 부분 추출
                    date_match = re.match(r'(\d{4})\.\s*(\d{1,2})\.\s*(\d{1,2})', s_timestamp)
                    if date_match:
                        year = int(date_match.group(1))
                        month = int(date_match.group(2))
                        day = int(date_match.group(3))

                        # 시간 부분 처리
                        time_match = re.search(r'(오전|오후)\s*(\d{1,2}):(\d{2}):(\d{2})', s_timestamp)
                        if time_match:
                            am_pm = time_match.group(1)
                            hour = int(time_match.group(2))
                            minute = int(time_match.group(3))
                            second = int(time_match.group(4))

                            # 오후 시간 조정
                            if am_pm == '오후' and hour < 12:
                                hour += 12
                            elif am_pm == '오전' and hour == 12:
                                hour = 0

                            timestamp = datetime(year, month, day, hour, minute, second)
                        else:
                            timestamp = datetime(year, month, day)
                else:
                    # 다른 형식들 시도
                    for fmt in ['%Y-%m-%d %H:%M:%S', '%Y/%m/%d %H:%M:%S', '%m/%d/%Y %H:%M:%S']:
                        try:
                            timestamp = datetime.strptime(s_timestamp, fmt)
                            break
                        except ValueError:
                            continue
            except Exception as e:
                logger.warning(f"Could not parse timestamp: {s_timestamp}")

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

        # 불만점수 변환
        f_complain = 0.2  # 기본값
        try:
            f_complain = float(data.get('fComplain', 0.2))
        except:
            f_complain = 0.2

        # Complain 객체 생성
        complain = Complain(
            # 텍스트 필드들
            sTimeStamp=s_timestamp,
            sCompanyName=s_company_name,
            sPass=data.get('sPass', ''),
            sComplain=data.get('sComplain', ''),
            sComplainPost=data.get('sComplainPost', ''),
            sPost=data.get('sPost', ''),
            sSMSBool=data.get('sSMSBool', ''),
            sSMSMent=data.get('sSMSMent', ''),
            sFile=data.get('sFile', ''),
            sCheck=data.get('sCheck', ''),
            sWorker=data.get('sWorker', ''),

            # 변환된 필드들
            timeStamp=timestamp,
            noCompany=company_no,
            fComplain=f_complain
        )

        complain.save()
        logger.info(f"Successfully created Complain record: {complain.no}")

        # 성공 응답
        response_data = {
            'success': True,
            'complain_id': complain.no,
            'company_no': company_no,
            'complain_score': f_complain,
            'message': '고객불만 데이터가 성공적으로 저장되었습니다.'
        }

        # 업체를 찾지 못한 경우 경고 추가
        if company_no == 0 and s_company_name:
            response_data['warning'] = f'업체명 "{s_company_name}"을 찾을 수 없어 업체ID가 0으로 설정되었습니다.'

        return JsonResponse(response_data)

    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {str(e)}")
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        logger.error(f"Error processing complain webhook: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def test_complain_webhook(request):
    """
    Complain webhook 테스트용 엔드포인트
    """
    try:
        # 테스트 데이터 생성
        test_data = {
            "sTimeStamp": "2025. 9. 28 오후 7:30:00",
            "sCompanyName": "테스트업체",
            "sPass": "온라인",
            "sComplain": "공사 마감이 깔끔하지 않습니다.",
            "sComplainPost": "https://example.com/complain/123",
            "sPost": "의뢰글-123",
            "sSMSBool": "발송완료",
            "sSMSMent": "고객님의 소중한 의견 감사합니다. 신속히 처리하겠습니다.",
            "sFile": "https://drive.google.com/file/complain123",
            "sCheck": "확인",
            "sWorker": "김담당",
            "fComplain": "0.2"
        }

        logger.info(f"Test complain webhook called with data: {test_data}")

        # 실제 webhook 호출
        request._body = json.dumps(test_data).encode('utf-8')
        request.META['HTTP_AUTHORIZATION'] = f"Bearer {getattr(settings, 'GOOGLE_SHEETS_WEBHOOK_TOKEN', 'testpark-google-sheets-webhook-2024')}"

        return complain_webhook(request)

    except Exception as e:
        logger.error(f"Test complain webhook error: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)