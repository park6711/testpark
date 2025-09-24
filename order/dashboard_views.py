"""
동기화 대시보드 API
실시간 동기화 상태와 통계를 제공
"""
from django.http import JsonResponse
from django.core.cache import cache
from django.db.models import Q, Count
from django.utils import timezone
from datetime import datetime, timedelta
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from .models import Order, StatusHistory

@api_view(['GET'])
@permission_classes([AllowAny])
def sync_dashboard(request):
    """동기화 대시보드 데이터"""
    try:
        # 캐시에서 마지막 동기화 정보 가져오기
        last_sync = cache.get('last_sync_stats', {})

        # 오늘 통계
        today = timezone.now().date()
        today_orders = Order.objects.filter(
            created_at__date=today
        )

        # 상태별 통계
        status_counts = Order.objects.values('recent_status').annotate(
            count=Count('no')
        ).order_by('-count')

        # 최근 7일 동기화 트렌드
        week_ago = timezone.now() - timedelta(days=7)
        daily_stats = []

        for i in range(7):
            day = week_ago + timedelta(days=i)
            count = Order.objects.filter(
                created_at__date=day.date()
            ).count()
            daily_stats.append({
                'date': day.date().isoformat(),
                'count': count
            })

        # 대기중인 할당
        pending_assignments = Order.objects.filter(
            recent_status='대기중',
            assigned_company__in=['', None]
        ).count()

        # 24시간 내 할당된 건
        yesterday = timezone.now() - timedelta(days=1)
        recent_assignments = Order.objects.filter(
            recent_status='할당',
            updated_at__gte=yesterday
        ).count()

        # 업체별 할당 현황
        company_stats = Order.objects.exclude(
            assigned_company__in=['', None]
        ).values('assigned_company').annotate(
            total=Count('no')
        ).order_by('-total')[:10]

        # 응답 구성
        dashboard_data = {
            'last_sync': {
                'time': last_sync.get('sync_time', 'N/A'),
                'elapsed': last_sync.get('elapsed_seconds', 0),
                'result': last_sync.get('result', {})
            },
            'today': {
                'total': today_orders.count(),
                'pending': today_orders.filter(recent_status='대기중').count(),
                'assigned': today_orders.filter(recent_status='할당').count(),
                'completed': today_orders.filter(recent_status='계약').count()
            },
            'status_distribution': [
                {'status': item['recent_status'], 'count': item['count']}
                for item in status_counts
            ],
            'weekly_trend': daily_stats,
            'assignments': {
                'pending': pending_assignments,
                'recent_24h': recent_assignments
            },
            'top_companies': [
                {'name': item['assigned_company'], 'count': item['total']}
                for item in company_stats
            ],
            'alerts': get_system_alerts()
        }

        return Response(dashboard_data)

    except Exception as e:
        return Response({
            'error': str(e)
        }, status=500)

@api_view(['GET'])
@permission_classes([AllowAny])
def sync_history(request):
    """동기화 이력 조회"""
    try:
        # 최근 100개 동기화 이력
        history = []

        # 캐시에서 이력 가져오기 (실제로는 DB에 저장하는 것이 좋음)
        for i in range(1, 11):
            key = f'sync_history_{i}'
            data = cache.get(key)
            if data:
                history.append(data)

        return Response({
            'history': history,
            'total': len(history)
        })

    except Exception as e:
        return Response({
            'error': str(e)
        }, status=500)

@api_view(['POST'])
@permission_classes([AllowAny])
def manual_sync(request):
    """수동 동기화 실행"""
    try:
        from .google_sheets_sync import GoogleSheetsSync

        # 동기화 잠금 확인
        if cache.get('google_sheets_sync_lock'):
            return Response({
                'status': 'error',
                'message': '다른 동기화가 진행 중입니다.'
            }, status=409)

        # 잠금 설정
        cache.set('google_sheets_sync_lock', True, 300)

        # 동기화 실행
        sync = GoogleSheetsSync()
        result = sync.sync_data(update_existing=request.data.get('update_existing', False))

        # 결과 캐시 저장
        cache.set('last_sync_stats', {
            'sync_time': datetime.now().isoformat(),
            'result': result,
            'manual': True
        }, 3600)

        # 잠금 해제
        cache.delete('google_sheets_sync_lock')

        return Response({
            'status': 'success',
            'result': result
        })

    except Exception as e:
        cache.delete('google_sheets_sync_lock')
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=500)

@api_view(['GET'])
@permission_classes([AllowAny])
def pending_orders(request):
    """할당 대기 중인 주문 목록"""
    try:
        orders = Order.objects.filter(
            recent_status='대기중',
            assigned_company__in=['', None]
        ).select_related().order_by('-created_at')[:50]

        data = []
        for order in orders:
            data.append({
                'id': order.no,
                'name': order.sName,
                'phone': order.sPhone,
                'area': order.sArea,
                'designation': order.designation,
                'designation_type': order.designation_type,
                'construction': order.sConstruction[:100] if order.sConstruction else '',
                'created': order.created_at.isoformat() if order.created_at else '',
                'schedule_date': order.dateSchedule.isoformat() if order.dateSchedule else ''
            })

        return Response({
            'orders': data,
            'total': len(data)
        })

    except Exception as e:
        return Response({
            'error': str(e)
        }, status=500)

def get_system_alerts():
    """시스템 알림 생성"""
    alerts = []

    # 24시간 이상 대기중인 주문
    old_pending = Order.objects.filter(
        recent_status='대기중',
        created_at__lte=timezone.now() - timedelta(days=1)
    ).count()

    if old_pending > 0:
        alerts.append({
            'type': 'warning',
            'message': f'{old_pending}건이 24시간 이상 할당 대기 중입니다.'
        })

    # 동기화 오류 확인
    last_sync = cache.get('last_sync_stats', {})
    if last_sync.get('result', {}).get('error'):
        alerts.append({
            'type': 'error',
            'message': '마지막 동기화에서 오류가 발생했습니다.'
        })

    # 48시간 이상 할당 상태
    stale_assigned = Order.objects.filter(
        recent_status='할당',
        updated_at__lte=timezone.now() - timedelta(days=2)
    ).count()

    if stale_assigned > 0:
        alerts.append({
            'type': 'info',
            'message': f'{stale_assigned}건이 48시간 이상 할당 상태입니다.'
        })

    return alerts