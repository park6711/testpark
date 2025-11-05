from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils import timezone
from django.contrib.auth.decorators import login_required
import json
from datetime import datetime, date, timedelta

from .models import Order, Assign, Estimate, AssignMemo
from company.models import Company


def order_list(request):
    """의뢰 목록 페이지"""
    from django.contrib import messages
    from django.shortcuts import redirect
    from staff.models import Staff

    # 로그인 확인
    if not request.session.get('staff_user'):
        messages.error(request, '로그인이 필요합니다.')
        return redirect('accounts:login')

    def get_current_staff(request):
        """현재 로그인한 스텝 정보 반환"""
        staff_user = request.session.get('staff_user')
        if not staff_user:
            return None
        return Staff.objects.filter(no=staff_user['no']).first()

    current_staff = get_current_staff(request)

    # 검색 및 필터링
    search = request.GET.get('search', '')
    status = request.GET.get('status', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')

    # 기본 쿼리셋 (최신순 정렬)
    orders = Order.objects.all().order_by('-created_at', '-no')

    # 검색
    if search:
        orders = orders.filter(
            Q(sName__icontains=search) |
            Q(sPhone__icontains=search) |
            Q(sArea__icontains=search) |
            Q(designation__icontains=search)
        )

    # 상태 필터
    if status:
        orders = orders.filter(recent_status=status)

    # 날짜 필터
    if date_from:
        orders = orders.filter(created_at__gte=date_from)
    if date_to:
        orders = orders.filter(created_at__lte=date_to + ' 23:59:59')

    # 페이지네이션 (50개씩 표시)
    paginator = Paginator(orders, 50)
    page = request.GET.get('page', 1)
    page_obj = paginator.get_page(page)

    # 각 Order의 Assign 정보 추가 (견적 및 메모 관리용)
    for order in page_obj:
        # 해당 Order의 첫 번째 Assign 조회 (보통 할당된 업체의 Assign)
        order.first_assign = Assign.objects.filter(noOrder=order.no).first()

    context = {
        'orders': page_obj,
        'current_staff': current_staff,
        'search': search,
        'status': status,
        'date_from': date_from,
        'date_to': date_to,
        'status_choices': Order.STATUS_CHOICES,
    }

    return render(request, 'order/order_list.html', context)


@require_http_methods(["GET"])
def api_order_list(request):
    """의뢰 목록 API"""
    try:
        # 쿼리 파라미터
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 20))
        search = request.GET.get('search', '')
        status_filter = request.GET.get('status', '')
        urgent_only = request.GET.get('urgent_only', '') == 'true'

        # 기본 쿼리셋
        queryset = Order.objects.all()

        # 검색 필터
        if search:
            queryset = queryset.filter(
                Q(sName__icontains=search) |
                Q(sPhone__icontains=search) |
                Q(sArea__icontains=search) |
                Q(sConstruction__icontains=search) |
                Q(sNaverID__icontains=search)
            )

        # 긴급 의뢰만
        if urgent_only:
            today = timezone.localtime().date()
            queryset = queryset.filter(
                dateSchedule__isnull=False,
                dateSchedule__gte=today,
                dateSchedule__lte=today + timedelta(days=3)
            )

        # 정렬 (최신순)
        queryset = queryset.order_by('-no')

        # 페이지네이션
        paginator = Paginator(queryset, page_size)
        page_obj = paginator.get_page(page)

        # 데이터 직렬화
        data = []
        for order in page_obj:
            # 할당 정보
            assigns = Assign.objects.filter(noOrder=order.no)
            assigned_companies = []
            current_status = '대기중'  # 기본 상태

            for assign in assigns:
                try:
                    company = Company.objects.get(no=assign.noCompany)
                    assigned_companies.append({
                        'id': company.no,
                        'name': company.sCompanyName or f'업체{company.no}',
                        'assigned_at': assign.time.isoformat(),
                        'status': assign.get_nAssignType_display(),
                        'response_received': assign.nAssignType in [1, 2]  # 할당 또는 반려
                    })

                    # 최신 할당 상태로 업데이트
                    if assign.time == assigns.order_by('-time').first().time:
                        current_status = assign.get_nAssignType_display()
                except Company.DoesNotExist:
                    continue

            # 상태별 색상 매핑
            status_color_map = {
                '대기중': 'warning',
                '할당': 'primary',
                '반려': 'danger',
                '취소': 'secondary',
                '제외': 'dark',
                '업체미비': 'info',
                '중복접수': 'warning',
                '가능문의': 'success',
                '불가능답변': 'secondary'
            }

            order_data = {
                'id': order.no,
                'customer_name': order.sName or '',
                'customer_phone': order.sPhone or '',
                'customer_email': '',  # Order 모델에 없는 필드
                'customer_address': order.sArea or '',
                'construction_content': order.sConstruction or '',
                'construction_date': order.dateSchedule.isoformat() if order.dateSchedule else None,
                'post_title': order.sPost or '',
                'naver_id': order.sNaverID or '',
                'nickname': order.sNick or '',
                'appointed_company': order.sAppoint or '',
                'status': current_status,
                'status_display': current_status,
                'status_color': status_color_map.get(current_status, 'secondary'),
                'privacy_agreement': order.bPrivacy1,
                'third_party_agreement': order.bPrivacy2,
                'privacy_status': order.get_privacy_status(),
                'schedule_status': order.get_schedule_status(),
                'is_urgent': order.is_urgent(),
                'assigned_companies': assigned_companies,
                'created_at': order.time.isoformat(),
                'updated_at': order.updated_at.isoformat(),
            }
            data.append(order_data)

        response_data = {
            'success': True,
            'data': data,
            'pagination': {
                'current_page': page_obj.number,
                'total_pages': paginator.num_pages,
                'total_items': paginator.count,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous(),
                'page_size': page_size
            }
        }

        return JsonResponse(response_data)

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def api_order_create(request):
    """의뢰 생성 API"""
    try:
        data = json.loads(request.body)

        # 필수 필드 검증
        required_fields = ['customer_name', 'customer_phone', 'customer_address', 'construction_content']

        for field in required_fields:
            django_field = {
                'customer_name': 'sName',
                'customer_phone': 'sPhone',
                'customer_address': 'sArea',
                'construction_content': 'sConstruction'
            }.get(field, field)

            if not data.get(field):
                return JsonResponse({
                    'success': False,
                    'error': f'{field} 필드는 필수입니다.'
                }, status=400)

        # 공사예정일 처리
        construction_date = None
        if data.get('construction_date'):
            try:
                construction_date = datetime.strptime(
                    data['construction_date'], '%Y-%m-%d'
                ).date()
            except ValueError:
                return JsonResponse({
                    'success': False,
                    'error': '공사예정일 형식이 올바르지 않습니다. (YYYY-MM-DD)'
                }, status=400)

        # Order 생성
        order = Order.objects.create(
            sName=data['customer_name'],
            sPhone=data['customer_phone'],
            sArea=data['customer_address'],
            sConstruction=data['construction_content'],
            dateSchedule=construction_date,
            sPost=data.get('post_title', ''),
            sNaverID=data.get('naver_id', ''),
            sNick=data.get('nickname', ''),
            sAppoint=data.get('appointed_company', ''),
            bPrivacy1=data.get('privacy_agreement', False),
            bPrivacy2=data.get('third_party_agreement', False)
        )

        return JsonResponse({
            'success': True,
            'data': {
                'id': order.no,
                'message': '의뢰가 성공적으로 생성되었습니다.'
            }
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': '잘못된 JSON 형식입니다.'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def api_order_assign_company(request, order_id):
    """의뢰 업체 할당 API"""
    try:
        order = get_object_or_404(Order, no=order_id)
        data = json.loads(request.body)

        company_ids = data.get('company_ids', [])
        memo = data.get('memo', '')
        construction_type = data.get('construction_type', 0)

        if not company_ids:
            return JsonResponse({
                'success': False,
                'error': '할당할 업체를 선택해주세요.'
            }, status=400)

        assigned_companies = []

        for company_id in company_ids:
            try:
                company = Company.objects.get(no=company_id)

                # Assign 생성
                assign = Assign.objects.create(
                    noOrder=order.no,
                    noCompany=company.no,
                    nConstructionType=construction_type,
                    nAssignType=1,  # 할당 상태
                    sWorker=request.user.username if request.user.is_authenticated else '',
                    sCompanySMS=memo
                )

                assigned_companies.append({
                    'id': company.no,
                    'name': company.sCompanyName or f'업체{company.no}'
                })

            except Company.DoesNotExist:
                continue

        return JsonResponse({
            'success': True,
            'data': {
                'assigned_companies': assigned_companies,
                'message': f'{len(assigned_companies)}개 업체에 할당되었습니다.'
            }
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': '잘못된 JSON 형식입니다.'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
def api_companies(request):
    """업체 목록 API"""
    try:
        search = request.GET.get('search', '')

        queryset = Company.objects.filter(bActive=True)

        if search:
            queryset = queryset.filter(
                Q(sCompanyName__icontains=search) |
                Q(sName__icontains=search)
            )

        companies = []
        for company in queryset[:50]:  # 최대 50개로 제한
            companies.append({
                'id': company.no,
                'name': company.sCompanyName or f'업체{company.no}',
                'owner_name': company.sName or '',
                'phone': company.sPhone or '',
                'address': company.sAddress or ''
            })

        return JsonResponse({
            'success': True,
            'data': companies
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["DELETE"])
def api_order_delete(request, order_id):
    """의뢰 삭제 API"""
    try:
        order = get_object_or_404(Order, no=order_id)

        # 관련 할당도 함께 삭제
        Assign.objects.filter(noOrder=order.no).delete()
        Estimate.objects.filter(noOrder=order.no).delete()
        AssignMemo.objects.filter(noOrder=order.no).delete()

        order.delete()

        return JsonResponse({
            'success': True,
            'message': '의뢰가 삭제되었습니다.'
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def api_order_bulk_delete(request):
    """의뢰 일괄 삭제 API"""
    try:
        data = json.loads(request.body)
        order_ids = data.get('order_ids', [])

        if not order_ids:
            return JsonResponse({
                'success': False,
                'error': '삭제할 항목을 선택해주세요.'
            }, status=400)

        # 관련 데이터도 함께 삭제
        Assign.objects.filter(noOrder__in=order_ids).delete()
        Estimate.objects.filter(noOrder__in=order_ids).delete()
        AssignMemo.objects.filter(noOrder__in=order_ids).delete()

        deleted_count = Order.objects.filter(no__in=order_ids).count()
        Order.objects.filter(no__in=order_ids).delete()

        return JsonResponse({
            'success': True,
            'data': {
                'deleted_count': deleted_count,
                'message': f'{deleted_count}개 항목이 삭제되었습니다.'
            }
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': '잘못된 JSON 형식입니다.'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
