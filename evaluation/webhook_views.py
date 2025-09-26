# evaluation/webhook_views.py
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.conf import settings
import json
import logging
from .models import Complain
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