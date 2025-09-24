"""
Celery 태스크를 사용한 자동 동기화 시스템
"""
from celery import shared_task
from datetime import datetime, timedelta
from django.core.cache import cache
from django.db import transaction
import logging
import json

logger = logging.getLogger(__name__)

@shared_task
def sync_google_sheets_task():
    """
    Google Sheets 자동 동기화 태스크
    5분마다 실행되도록 설정
    """
    try:
        from .google_sheets_sync import GoogleSheetsSync
        from .models import Order

        # 동기화 실행
        sync = GoogleSheetsSync()
        result = sync.sync_data()

        # 새로운 접수 건이 있으면 알림
        if result.get('created', 0) > 0:
            notify_new_orders(result['created'])

        # 결과를 캐시에 저장 (대시보드용)
        cache.set('last_sync_result', {
            'timestamp': datetime.now().isoformat(),
            'result': result
        }, 600)  # 10분간 유지

        logger.info(f"자동 동기화 완료: {result}")
        return result

    except Exception as e:
        logger.error(f"자동 동기화 실패: {str(e)}")
        return {'error': str(e)}

@shared_task
def notify_new_orders(count):
    """
    새 접수 건에 대한 알림 발송
    """
    try:
        from .models import Order
        from .jandi_webhook import send_jandi_notification

        # 최근 생성된 주문 조회
        recent_orders = Order.objects.filter(
            created_at__gte=datetime.now() - timedelta(minutes=10),
            recent_status='대기중'
        ).order_by('-created_at')[:count]

        if recent_orders:
            message = f"🔔 새로운 견적 의뢰가 {count}건 접수되었습니다!\n"

            for order in recent_orders:
                message += f"\n• {order.sName or '이름없음'} - {order.sArea or '지역미정'}"
                if order.sConstruction:
                    preview = order.sConstruction[:30] + "..." if len(order.sConstruction) > 30 else order.sConstruction
                    message += f"\n  내용: {preview}"

            message += f"\n\n👉 업체 할당이 필요합니다!"

            # Jandi 알림 발송 (구현되어 있다면)
            # send_jandi_notification(message)

            # 로그 기록
            logger.info(f"새 접수 알림 발송: {count}건")

    except Exception as e:
        logger.error(f"알림 발송 실패: {str(e)}")

@shared_task
def auto_assign_companies():
    """
    업체 자동 할당 규칙 적용
    - 지역별 업체 매칭
    - 공동구매 지정 확인
    - 업체 가용성 체크
    """
    try:
        from .models import Order, Company, GroupPurchase
        from area.models import Area

        # 대기중인 주문 조회
        pending_orders = Order.objects.filter(
            recent_status='대기중',
            assigned_company=''
        )

        assigned_count = 0

        for order in pending_orders:
            # 공동구매 지정 확인
            if order.designation_type == '공동구매':
                # 공동구매 업체 할당 로직
                group_purchase = GroupPurchase.objects.filter(
                    is_active=True,
                    available_areas__contains=order.sArea
                ).first()

                if group_purchase:
                    order.assigned_company = group_purchase.company_name
                    order.recent_status = '할당'
                    order.save()
                    assigned_count += 1
                    continue

            # 일반 업체 할당 (지역 기반)
            if order.sArea:
                # 해당 지역에서 활동 가능한 업체 찾기
                available_companies = Company.objects.filter(
                    is_active=True,
                    service_areas__contains=order.sArea
                ).order_by('current_assignments')  # 현재 할당 수가 적은 업체 우선

                if available_companies.exists():
                    company = available_companies.first()
                    order.assigned_company = company.sCompanyName
                    order.recent_status = '할당'
                    order.save()

                    # 업체의 현재 할당 수 증가
                    company.current_assignments += 1
                    company.save()

                    assigned_count += 1

        logger.info(f"자동 할당 완료: {assigned_count}건")
        return {'assigned': assigned_count}

    except Exception as e:
        logger.error(f"자동 할당 실패: {str(e)}")
        return {'error': str(e)}

@shared_task
def check_assignment_deadlines():
    """
    할당 후 응답 없는 업체 확인
    24시간 내 응답 없으면 재할당
    """
    try:
        from .models import Order, StatusHistory

        deadline = datetime.now() - timedelta(hours=24)

        # 24시간 이상 할당 상태인 주문 조회
        stale_assignments = Order.objects.filter(
            recent_status='할당',
            updated_at__lte=deadline
        )

        reassigned_count = 0

        for order in stale_assignments:
            # 상태 이력 확인
            last_status = StatusHistory.objects.filter(
                order=order,
                new_status='할당'
            ).order_by('-created_at').first()

            if last_status and last_status.created_at <= deadline:
                # 반려 처리하고 재할당 대기
                order.recent_status = '반려'
                order.assigned_company = ''
                order.save()

                # 이력 기록
                StatusHistory.objects.create(
                    order=order,
                    old_status='할당',
                    new_status='반려',
                    message_content='24시간 내 응답 없음 - 자동 반려',
                    author='시스템'
                )

                reassigned_count += 1

        if reassigned_count > 0:
            logger.info(f"응답 없는 할당 {reassigned_count}건 반려 처리")

        return {'reassigned': reassigned_count}

    except Exception as e:
        logger.error(f"할당 기한 체크 실패: {str(e)}")
        return {'error': str(e)}