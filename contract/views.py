from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from django.views.generic import ListView
from django.utils.decorators import method_decorator
from django.db.models import Q
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from .models import ClientReport
from company.models import Company
from staff.models import Staff

def contract_list(request):
    """계약 목록 페이지"""
    return HttpResponse("Contract List - 계약 관리 페이지입니다.")

def clientreport_list(request):
    """고객계약보고 리스트 페이지"""
    # 현재 로그인한 스태프 정보
    current_staff = None
    if 'staff_user' in request.session:
        try:
            current_staff = Staff.objects.get(no=request.session['staff_user']['no'])
        except Staff.DoesNotExist:
            pass

    # 활동상태 필터
    condition_filters = request.GET.getlist('condition')
    if not condition_filters:
        condition_filters = ['1', '2']  # 기본값: 정상, 일시정지

    # 확인 모드 필터
    check_filters = request.GET.getlist('check')

    # 기본 쿼리셋
    queryset = ClientReport.objects.all()

    # Company 조건으로 필터링
    if condition_filters:
        company_nos = Company.objects.filter(
            nCondition__in=condition_filters
        ).values_list('no', flat=True)
        queryset = queryset.filter(noCompany__in=company_nos)

    # 확인 상태로 필터링
    if check_filters:
        queryset = queryset.filter(nCheck__in=check_filters)

    # 통합 검색
    search_query = request.GET.get('search', '')
    if search_query:
        # Company 관련 검색
        company_search = Company.objects.filter(
            Q(sName1__icontains=search_query) |
            Q(sName2__icontains=search_query) |
            Q(sName3__icontains=search_query)
        ).values_list('no', flat=True)

        queryset = queryset.filter(
            Q(sCompanyName__icontains=search_query) |
            Q(sName__icontains=search_query) |
            Q(sArea__icontains=search_query) |
            Q(sPhone__icontains=search_query) |
            Q(sClientMemo__icontains=search_query) |
            Q(sMemo__icontains=search_query) |
            Q(sPost__icontains=search_query) |
            Q(sExplain__icontains=search_query) |
            Q(sPunish__icontains=search_query) |
            Q(noCompany__in=company_search)
        )

    # 정렬 처리
    sort_by = request.GET.get('sort', '-timeStamp')  # 기본값: timeStamp 내림차순

    # 유효한 정렬 필드인지 확인
    valid_sort_fields = ['no', '-no', 'timeStamp', '-timeStamp']
    if sort_by not in valid_sort_fields:
        sort_by = '-timeStamp'

    queryset = queryset.order_by(sort_by)

    # 페이징
    from django.core.paginator import Paginator
    paginator = Paginator(queryset, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # 각 ClientReport에 Company 정보 추가
    for report in page_obj:
        try:
            company = Company.objects.get(no=report.noCompany)
            report.company = company
        except Company.DoesNotExist:
            report.company = None

    # 모든 업체 리스트 (드롭다운용)
    all_companies = Company.objects.filter(
        nCondition__in=condition_filters
    ).order_by('sName2', 'sName1')

    context = {
        'current_staff': current_staff,
        'clientreports': page_obj,
        'all_companies': all_companies,
        'search_query': search_query,
        'condition_filters': [int(c) for c in condition_filters],
        'check_filters': [int(c) for c in check_filters] if check_filters else [],
        'total_count': queryset.count(),
        'sort_by': sort_by,
    }

    return render(request, 'contract/clientreport_list.html', context)

def clientreport_detail(request, pk):
    """고객계약보고 상세보기"""
    report = get_object_or_404(ClientReport, pk=pk)

    # Company 정보 가져오기
    try:
        company = Company.objects.get(no=report.noCompany)
        report.company = company
    except Company.DoesNotExist:
        report.company = None

    current_staff = None
    if 'staff_user' in request.session:
        try:
            current_staff = Staff.objects.get(no=request.session['staff_user']['no'])
        except Staff.DoesNotExist:
            pass

    context = {
        'report': report,
        'current_staff': current_staff,
        'mode': 'view',
    }

    return render(request, 'contract/clientreport_detail.html', context)

def clientreport_edit(request, pk):
    """고객계약보고 수정"""
    report = get_object_or_404(ClientReport, pk=pk)

    current_staff = None
    if 'staff_user' in request.session:
        try:
            current_staff = Staff.objects.get(no=request.session['staff_user']['no'])
        except Staff.DoesNotExist:
            pass

    if request.method == 'POST':
        # 수정 가능한 필드들만 업데이트
        report.noCompany = int(request.POST.get('noCompany', 0))
        report.sPost = request.POST.get('sPost', '')
        report.noAssign = int(request.POST.get('noAssign')) if request.POST.get('noAssign') else None
        report.noCompanyReport = int(request.POST.get('noCompanyReport')) if request.POST.get('noCompanyReport') else None
        report.nCheck = int(request.POST.get('nCheck', 0))
        report.sMemo = request.POST.get('sMemo', '')
        report.dateExplain0 = request.POST.get('dateExplain0') or None
        report.dateExplain1 = request.POST.get('dateExplain1') or None
        report.sExplain = request.POST.get('sExplain', '')
        report.sPunish = request.POST.get('sPunish', '')

        report.save()
        messages.success(request, '고객계약보고가 수정되었습니다.')
        return redirect('contract:clientreport_detail', pk=pk)

    # 모든 업체 리스트
    all_companies = Company.objects.filter(
        nCondition__in=[1, 2]
    ).order_by('sName2', 'sName1')

    context = {
        'report': report,
        'current_staff': current_staff,
        'mode': 'edit',
        'all_companies': all_companies,
    }

    return render(request, 'contract/clientreport_detail.html', context)

@csrf_exempt
@require_http_methods(["POST"])
def clientreport_delete(request, pk):
    """고객계약보고 삭제"""
    try:
        report = get_object_or_404(ClientReport, pk=pk)
        report.delete()

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True})
        else:
            messages.success(request, '고객계약보고가 삭제되었습니다.')
            return redirect('contract:clientreport_list')

    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': str(e)})
        else:
            messages.error(request, f'삭제 중 오류가 발생했습니다: {str(e)}')
            return redirect('contract:clientreport_list')
