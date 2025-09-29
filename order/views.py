from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Order, Assign, Estimate
from company.models import Company
from staff.models import Staff
from datetime import datetime, timedelta

def get_current_staff(request):
    """현재 로그인한 스텝 정보 반환"""
    staff_user = request.session.get('staff_user')
    if not staff_user:
        return None
    return Staff.objects.filter(no=staff_user['no']).first()

def order_list(request):
    """의뢰 목록 페이지"""
    # 로그인 확인
    if not request.session.get('staff_user'):
        messages.error(request, '로그인이 필요합니다.')
        return redirect('accounts:login')

    current_staff = get_current_staff(request)

    # 검색 및 필터링
    search = request.GET.get('search', '')
    status = request.GET.get('status', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')

    # 기본 쿼리셋
    orders = Order.objects.all()

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

    # 페이지네이션
    paginator = Paginator(orders, 20)
    page = request.GET.get('page', 1)
    page_obj = paginator.get_page(page)

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

