from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.contrib import messages
from django.db.models import Q
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from datetime import datetime
import json
from .models import Point
from .forms import PointForm
from company.models import Company
from staff.models import Staff


def get_current_staff(request):
    """현재 로그인한 스텝 정보 반환"""
    staff_user = request.session.get('staff_user')
    if not staff_user:
        return None
    return Staff.objects.filter(no=staff_user['no']).first()


def point_list(request):
    """포인트 리스트 뷰"""
    # 로그인 확인
    if not request.session.get('staff_user'):
        return render(request, 'point/point_list.html', {
            'not_logged_in': True,
            'points': [],
            'current_staff': None,
        })

    # 현재 스텝 정보 가져오기
    current_staff = get_current_staff(request)

    # 기본 쿼리셋 - no 내림차순 정렬
    queryset = Point.objects.select_related('noCompany', 'noCompanyReport').order_by('-no')

    # 통합 검색
    search_query = request.GET.get('search', '')
    if search_query:
        # 삭제된 업체 검색 시 처리
        if '삭제' in search_query.lower():
            queryset = queryset.filter(
                Q(noCompany__sName1__icontains=search_query) |
                Q(noCompany__sName2__icontains=search_query) |
                Q(sWorker__icontains=search_query) |
                Q(sMemo__icontains=search_query) |
                Q(noCompany__isnull=True)  # 삭제된 업체 포함
            )
        else:
            queryset = queryset.filter(
                Q(noCompany__sName1__icontains=search_query) |
                Q(noCompany__sName2__icontains=search_query) |
                Q(sWorker__icontains=search_query) |
                Q(sMemo__icontains=search_query)
            )


    # 구분 필터
    point_type = request.GET.get('type', '')
    if point_type:
        queryset = queryset.filter(nType=point_type)

    # 날짜 필터
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')

    if start_date:
        try:
            start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
            queryset = queryset.filter(time__gte=start_datetime)
        except ValueError:
            pass

    if end_date:
        try:
            end_datetime = datetime.strptime(end_date, '%Y-%m-%d')
            end_datetime = end_datetime.replace(hour=23, minute=59, second=59)
            queryset = queryset.filter(time__lte=end_datetime)
        except ValueError:
            pass

    # 페이지네이션
    paginator = Paginator(queryset, 20)
    page_number = request.GET.get('page', 1)
    points = paginator.get_page(page_number)

    # 컨텍스트 데이터
    context = {
        'points': points,
        'point_types': Point.TYPE_CHOICES,
        'current_staff': current_staff,
    }

    return render(request, 'point/point_list.html', context)


def point_detail(request, pk):
    """포인트 상세 보기"""
    # 로그인 확인
    if not request.session.get('staff_user'):
        return redirect('staff:login')

    # 현재 스텝 정보 가져오기
    current_staff = get_current_staff(request)

    point = get_object_or_404(Point.objects.select_related('noCompany', 'noCompanyReport'), pk=pk)

    # 해당 업체의 최근 포인트 내역
    recent_points = Point.objects.filter(
        noCompany=point.noCompany
    ).exclude(pk=pk).order_by('-time')[:5]

    context = {
        'point': point,
        'recent_points': recent_points,
        'current_staff': current_staff,
    }

    return render(request, 'point/point_detail.html', context)


def point_create(request):
    """포인트 추가"""
    # 로그인 확인
    if not request.session.get('staff_user'):
        return redirect('auth:login')

    # 현재 스텝 정보 가져오기
    current_staff = get_current_staff(request)

    if request.method == 'POST':
        form = PointForm(request.POST)
        if form.is_valid():
            point = form.save(commit=False)

            # 이전 포인트 잔액 계산
            last_point = Point.objects.filter(
                noCompany=point.noCompany
            ).order_by('-time', '-no').first()

            if last_point:
                point.nPrePoint = last_point.nRemainPoint
            else:
                point.nPrePoint = 0

            # 잔액 포인트 계산
            point.nRemainPoint = point.nPrePoint + point.nUsePoint

            # 작업자 정보 설정 (사용자가 입력한 값 사용, 없으면 현재 스텝 정보)
            if not point.sWorker and current_staff:
                point.sWorker = current_staff.sNick or current_staff.sName

            point.save()
            messages.success(request, f'포인트 내역이 추가되었습니다. (잔액: {point.nRemainPoint:,})')
            return redirect('point:point_list')
    else:
        form = PointForm()

    context = {
        'form': form,
        'title': '포인트 추가',
        'button_text': '추가',
        'current_staff': current_staff,
    }

    return render(request, 'point/point_form.html', context)


def point_update(request, pk):
    """포인트 수정 (AJAX API)"""
    # 로그인 확인
    if not request.session.get('staff_user'):
        return JsonResponse({'error': 'Not authenticated'}, status=401)

    point = get_object_or_404(Point, pk=pk)

    if request.method == 'POST':
        try:
            # JSON 데이터 파싱
            data = json.loads(request.body)

            # 필드 업데이트
            point.nType = int(data.get('nType', point.nType))
            point.sWorker = data.get('sWorker', point.sWorker)
            point.nUsePoint = int(data.get('nUsePoint', point.nUsePoint))
            point.sMemo = data.get('sMemo', point.sMemo)

            # 적용 포인트 0 체크
            if point.nUsePoint == 0:
                return JsonResponse({'error': '적용 포인트는 0이 될 수 없습니다.'}, status=400)

            # 잔액 재계산
            point.nRemainPoint = point.nPrePoint + point.nUsePoint

            point.save()

            return JsonResponse({
                'success': True,
                'message': '포인트 정보가 수정되었습니다.',
                'data': {
                    'nType': point.nType,
                    'sWorker': point.sWorker,
                    'nUsePoint': point.nUsePoint,
                    'nRemainPoint': point.nRemainPoint,
                    'sMemo': point.sMemo
                }
            })
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Method not allowed'}, status=405)


@require_POST
def point_delete(request, pk):
    """포인트 삭제"""
    # 로그인 확인
    if not request.session.get('staff_user'):
        return JsonResponse({'error': 'Not authenticated'}, status=401)

    point = get_object_or_404(Point, pk=pk)

    # Company가 NULL인 경우 처리
    if point.noCompany:
        company_name = point.noCompany.sName2
        # 이후 포인트 내역이 있는지 확인
        later_points = Point.objects.filter(
            noCompany=point.noCompany,
            time__gt=point.time
        ).exists()
    else:
        company_name = "삭제된 업체"
        later_points = False

    point_id = point.no

    if later_points:
        return JsonResponse({
            'error': '이후 포인트 내역이 존재하여 삭제할 수 없습니다. 최신 내역부터 삭제해주세요.'
        }, status=400)
    else:
        point.delete()
        return JsonResponse({
            'success': True,
            'message': f'{company_name}의 포인트 내역 #{point_id}이(가) 삭제되었습니다.'
        })


def get_previous_point(request, company_id):
    """업체의 최신 포인트 잔액을 반환하는 API"""
    # 로그인 확인
    if not request.session.get('staff_user'):
        return JsonResponse({'error': 'Not authenticated'}, status=401)

    try:
        # 해당 업체의 최신 포인트 내역 조회
        last_point = Point.objects.filter(
            noCompany_id=company_id
        ).order_by('-time', '-no').first()

        if last_point:
            previous_point = last_point.nRemainPoint
        else:
            previous_point = 0

        return JsonResponse({
            'previous_point': previous_point,
            'company_id': company_id
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)