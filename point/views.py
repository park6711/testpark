from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.contrib import messages
from django.db.models import Q
from django.views.decorators.http import require_POST
from datetime import datetime
from .models import Point
from .forms import PointForm
from company.models import Company


def point_list(request):
    """포인트 리스트 뷰"""
    # 기본 쿼리셋
    queryset = Point.objects.select_related('noCompany', 'noCompanyReport').all()

    # 통합 검색
    search_query = request.GET.get('search', '')
    if search_query:
        queryset = queryset.filter(
            Q(noCompany__sName1__icontains=search_query) |
            Q(noCompany__sName2__icontains=search_query) |
            Q(sWorker__icontains=search_query) |
            Q(sMemo__icontains=search_query)
        )

    # 업체 필터
    company_id = request.GET.get('company', '')
    if company_id:
        queryset = queryset.filter(noCompany_id=company_id)

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
        'companies': Company.objects.filter(dateWithdraw__isnull=True).order_by('sName2'),
        'point_types': Point.TYPE_CHOICES,
    }

    return render(request, 'point/point_list.html', context)


def point_detail(request, pk):
    """포인트 상세 보기"""
    point = get_object_or_404(Point.objects.select_related('noCompany', 'noCompanyReport'), pk=pk)

    # 해당 업체의 최근 포인트 내역
    recent_points = Point.objects.filter(
        noCompany=point.noCompany
    ).exclude(pk=pk).order_by('-time')[:5]

    context = {
        'point': point,
        'recent_points': recent_points,
    }

    return render(request, 'point/point_detail.html', context)


def point_create(request):
    """포인트 추가"""
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
            point.nRemainPoint = point.nPrePoint - point.nUsePoint

            # 작업자 정보 설정
            if hasattr(request, 'user') and request.user.is_authenticated:
                point.sWorker = request.user.username

            point.save()
            messages.success(request, f'포인트 내역이 추가되었습니다. (잔액: {point.nRemainPoint:,})')
            return redirect('point:point_list')
    else:
        form = PointForm()

    context = {
        'form': form,
        'title': '포인트 추가',
        'button_text': '추가',
    }

    return render(request, 'point/point_form.html', context)


def point_update(request, pk):
    """포인트 수정"""
    point = get_object_or_404(Point, pk=pk)

    if request.method == 'POST':
        form = PointForm(request.POST, instance=point)
        if form.is_valid():
            updated_point = form.save(commit=False)

            # 잔액 재계산
            updated_point.nRemainPoint = updated_point.nPrePoint - updated_point.nUsePoint

            updated_point.save()
            messages.success(request, '포인트 내역이 수정되었습니다.')
            return redirect('point:point_detail', pk=pk)
    else:
        form = PointForm(instance=point)

    context = {
        'form': form,
        'point': point,
        'title': '포인트 수정',
        'button_text': '수정',
    }

    return render(request, 'point/point_form.html', context)


@require_POST
def point_delete(request, pk):
    """포인트 삭제"""
    point = get_object_or_404(Point, pk=pk)
    company_name = point.noCompany.sName2
    point_id = point.no

    # 이후 포인트 내역이 있는지 확인
    later_points = Point.objects.filter(
        noCompany=point.noCompany,
        time__gt=point.time
    ).exists()

    if later_points:
        messages.error(
            request,
            '이후 포인트 내역이 존재하여 삭제할 수 없습니다. 최신 내역부터 삭제해주세요.'
        )
    else:
        point.delete()
        messages.success(request, f'{company_name}의 포인트 내역 #{point_id}이(가) 삭제되었습니다.')

    return redirect('point:point_list')