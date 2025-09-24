from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from django.db import models
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.urls import reverse
from .models import FixFee, FixFeeDate
from company.models import Company
from staff.models import Staff
import json


def fixfee_list(request):
    """월고정비 납부 현황 리스트"""

    # 현재 스텝 정보 가져오기
    current_staff = None
    if request.session.get('staff_user'):
        try:
            current_staff = Staff.objects.get(no=request.session['staff_user']['no'])
        except Staff.DoesNotExist:
            pass

    # 쿼리셋 기본 설정
    queryset = FixFee.objects.all().select_related()

    # 필터링
    fee_date_filter = request.GET.get('fee_date', '')
    company_filter = request.GET.get('company', '')
    type_filter = request.GET.get('type', '')
    search = request.GET.get('search', '')
    # nCondition 필터링 (체크박스로 여러 개 선택 가능)
    # 초기 화면에서는 1(정상)과 2(일시정지)를 기본값으로 설정
    condition_filters = request.GET.getlist('condition')
    if not condition_filters and not any([fee_date_filter, company_filter, type_filter, search]):
        condition_filters = ['1', '2']

    if fee_date_filter:
        queryset = queryset.filter(noFixFeeDate=fee_date_filter)

    if company_filter:
        queryset = queryset.filter(noCompany=company_filter)

    if type_filter:
        queryset = queryset.filter(nType=type_filter)

    if condition_filters:
        # 선택된 조건의 회사들만 필터링
        company_ids = Company.objects.filter(nCondition__in=condition_filters).values_list('no', flat=True)
        queryset = queryset.filter(noCompany__in=company_ids)

    if search:
        # 통합 검색 (업체명, 비고)
        company_ids = Company.objects.filter(
            Q(sName1__icontains=search) |
            Q(sName2__icontains=search)
        ).values_list('no', flat=True)

        queryset = queryset.filter(
            Q(noCompany__in=company_ids) |
            Q(sMemo__icontains=search)
        )

    # 정렬
    sort = request.GET.get('sort', '-no')
    queryset = queryset.order_by(sort)

    # 페이지네이션
    paginator = Paginator(queryset, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # 필터 옵션 데이터
    fee_dates = FixFeeDate.objects.all().order_by('no')[:12]  # 최근 12개월

    # 체크된 조건에 맞는 업체만 필터링
    if condition_filters:
        companies = Company.objects.filter(nType=1, nCondition__in=condition_filters).order_by('sName2')
    else:
        # 조건이 선택되지 않은 경우 모든 업체 표시
        companies = Company.objects.filter(nType=1).order_by('sName2')

    # 업체 정보에 상태 텍스트 추가
    companies_with_condition = []
    for company in companies:
        condition_text = dict(Company.CONDITION_CHOICES).get(company.nCondition, '')
        companies_with_condition.append({
            'no': company.no,
            'sName2': company.sName2,
            'nCondition': company.nCondition,
            'condition_text': condition_text,
            'display_name': f"{company.sName2} ({condition_text})"
        })

    payment_types = FixFee.TYPE_CHOICES

    context = {
        'page_obj': page_obj,
        'current_staff': current_staff,
        'fee_dates': fee_dates,
        'companies': companies_with_condition,
        'payment_types': payment_types,
        'condition_choices': Company.CONDITION_CHOICES,
        'fee_date_filter': fee_date_filter,
        'company_filter': company_filter,
        'type_filter': type_filter,
        'condition_filters': condition_filters,
        'search': search,
    }

    return render(request, 'fixfee/fixfee_list.html', context)


def fixfee_detail(request, pk):
    """월고정비 상세 보기/수정"""

    fixfee = get_object_or_404(FixFee, pk=pk)

    # 현재 스텝 정보 가져오기
    current_staff = None
    if request.session.get('staff_user'):
        try:
            current_staff = Staff.objects.get(no=request.session['staff_user']['no'])
        except Staff.DoesNotExist:
            pass

    # 참조 페이지 정보 저장
    referrer = request.GET.get('referrer', '')
    ref_fee_date = request.GET.get('ref_fee_date', '')
    ref_conditions = request.GET.getlist('ref_condition')

    if request.method == 'POST':
        # 수정 처리
        try:
            fixfee.dateDeposit = request.POST.get('dateDeposit') or None
            fixfee.nFixFee = int(request.POST.get('nFixFee', 0))
            fixfee.nType = int(request.POST.get('nType', 0))
            fixfee.sMemo = request.POST.get('sMemo', '')
            fixfee.save()

            messages.success(request, '월고정비 정보가 수정되었습니다.')

            # 참조 페이지가 있으면 그곳으로 돌아가기
            referrer = request.POST.get('referrer', '')
            if referrer == 'status':
                ref_fee_date = request.POST.get('ref_fee_date', '')
                ref_conditions = request.POST.getlist('ref_condition')
                url = reverse('fixfee:fixfee_status')
                params = []
                if ref_fee_date:
                    params.append(f'fee_date={ref_fee_date}')
                for cond in ref_conditions:
                    params.append(f'condition={cond}')
                if params:
                    url += '?' + '&'.join(params)
                return redirect(url)

            return redirect('fixfee:fixfee_detail', pk=pk)

        except Exception as e:
            messages.error(request, f'수정 중 오류가 발생했습니다: {str(e)}')

    # 관련 데이터
    company = Company.objects.filter(no=fixfee.noCompany).first()
    fee_date = FixFeeDate.objects.filter(no=fixfee.noFixFeeDate).first()
    payment_types = FixFee.TYPE_CHOICES

    context = {
        'fixfee': fixfee,
        'company': company,
        'fee_date': fee_date,
        'payment_types': payment_types,
        'current_staff': current_staff,
        'is_edit': request.GET.get('edit') == 'true',
        'referrer': referrer,
        'ref_fee_date': ref_fee_date,
        'ref_conditions': ref_conditions,
    }

    return render(request, 'fixfee/fixfee_detail.html', context)


def fixfee_add(request):
    """월고정비 추가"""

    # 현재 스텝 정보 가져오기
    current_staff = None
    if request.session.get('staff_user'):
        try:
            current_staff = Staff.objects.get(no=request.session['staff_user']['no'])
        except Staff.DoesNotExist:
            pass

    # URL 파라미터에서 업체와 납부기준일 가져오기
    preselected_company = request.GET.get('company', '')
    preselected_fee_date = request.GET.get('fee_date', '')

    # 참조 페이지 정보 저장
    referrer = request.GET.get('referrer', '')
    ref_fee_date = request.GET.get('ref_fee_date', '')
    ref_conditions = request.GET.getlist('ref_condition')

    if request.method == 'POST':
        try:
            noCompany = int(request.POST.get('noCompany'))
            noFixFeeDate = int(request.POST.get('noFixFeeDate'))

            # 중복 체크: 같은 업체와 같은 납부기준일의 레코드가 있는지 확인
            existing = FixFee.objects.filter(
                noCompany=noCompany,
                noFixFeeDate=noFixFeeDate
            ).exists()

            if existing:
                messages.error(request, '동일한 업체에서 동일한 납부기준일의 월고정비 납부 데이터가 있습니다.')
            else:
                fixfee = FixFee(
                    noCompany=noCompany,
                    noFixFeeDate=noFixFeeDate,
                    dateDeposit=request.POST.get('dateDeposit') or None,
                    nFixFee=int(request.POST.get('nFixFee', 0)),
                    nType=int(request.POST.get('nType', 0)),
                    sMemo=request.POST.get('sMemo', '')
                )
                fixfee.save()

                messages.success(request, '월고정비가 추가되었습니다.')

                # 참조 페이지가 있으면 그곳으로 돌아가기
                referrer = request.POST.get('referrer', '')
                if referrer == 'status':
                    ref_fee_date = request.POST.get('ref_fee_date', '')
                    ref_conditions = request.POST.getlist('ref_condition')
                    url = reverse('fixfee:fixfee_status')
                    params = []
                    if ref_fee_date:
                        params.append(f'fee_date={ref_fee_date}')
                    for cond in ref_conditions:
                        params.append(f'condition={cond}')
                    if params:
                        url += '?' + '&'.join(params)
                    return redirect(url)

                return redirect('fixfee:fixfee_list')

        except Exception as e:
            messages.error(request, f'추가 중 오류가 발생했습니다: {str(e)}')

    # 선택 옵션 데이터
    companies = Company.objects.filter(nType=1).exclude(nCondition=3).order_by('sName2')  # 고정비토탈 업체만, 탈퇴 제외

    # 업체 정보에 상태 텍스트 추가
    companies_with_condition = []
    for company in companies:
        condition_text = dict(Company.CONDITION_CHOICES).get(company.nCondition, '')
        companies_with_condition.append({
            'no': company.no,
            'sName2': company.sName2,
            'nCondition': company.nCondition,
            'nFixFee': company.nFixFee,
            'condition_text': condition_text,
            'display_name': f"{company.sName2} ({condition_text})"
        })

    fee_dates = FixFeeDate.objects.all().order_by('no')[:12]  # 최근 12개월
    payment_types = FixFee.TYPE_CHOICES

    context = {
        'companies': companies_with_condition,
        'fee_dates': fee_dates,
        'payment_types': payment_types,
        'current_staff': current_staff,
        'preselected_company': preselected_company,
        'preselected_fee_date': preselected_fee_date,
        'referrer': referrer,
        'ref_fee_date': ref_fee_date,
        'ref_conditions': ref_conditions,
    }

    return render(request, 'fixfee/fixfee_add.html', context)


@require_POST
def fixfee_delete(request, pk):
    """월고정비 삭제"""

    try:
        fixfee = get_object_or_404(FixFee, pk=pk)
        fixfee.delete()

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # AJAX 요청에 대해 리다이렉트 URL 포함
            referrer = request.POST.get('referrer', '')
            if referrer == 'status':
                ref_fee_date = request.POST.get('ref_fee_date', '')
                ref_conditions = request.POST.getlist('ref_condition')
                url = reverse('fixfee:fixfee_status')
                params = []
                if ref_fee_date:
                    params.append(f'fee_date={ref_fee_date}')
                for cond in ref_conditions:
                    params.append(f'condition={cond}')
                if params:
                    url += '?' + '&'.join(params)
                return JsonResponse({'success': True, 'message': '삭제되었습니다.', 'redirect_url': url})
            return JsonResponse({'success': True, 'message': '삭제되었습니다.'})

        messages.success(request, '월고정비가 삭제되었습니다.')

    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': str(e)})

        messages.error(request, f'삭제 중 오류가 발생했습니다: {str(e)}')

    # 일반 요청에 대한 리다이렉트
    referrer = request.POST.get('referrer', '')
    if referrer == 'status':
        ref_fee_date = request.POST.get('ref_fee_date', '')
        ref_conditions = request.POST.getlist('ref_condition')
        url = reverse('fixfee:fixfee_status')
        params = []
        if ref_fee_date:
            params.append(f'fee_date={ref_fee_date}')
        for cond in ref_conditions:
            params.append(f'condition={cond}')
        if params:
            url += '?' + '&'.join(params)
        return redirect(url)

    return redirect('fixfee:fixfee_list')


def check_duplicate(request):
    """중복 체크 (AJAX)"""

    company_id = request.GET.get('company_id')
    fee_date_id = request.GET.get('fee_date_id')

    if not company_id or not fee_date_id:
        return JsonResponse({'error': '필수 파라미터가 누락되었습니다.'}, status=400)

    try:
        existing = FixFee.objects.filter(
            noCompany=int(company_id),
            noFixFeeDate=int(fee_date_id)
        ).exists()

        return JsonResponse({'duplicate': existing})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def fixfee_status(request):
    """월고정비 현황 - 행렬 형태"""

    # 현재 스텝 정보 가져오기
    current_staff = None
    if request.session.get('staff_user'):
        try:
            current_staff = Staff.objects.get(no=request.session['staff_user']['no'])
        except Staff.DoesNotExist:
            pass

    # 활동상태 필터링 (체크박스)
    condition_filters = request.GET.getlist('condition')
    if not condition_filters:
        # 초기값: 정상(1)과 일시정지(2) 체크
        condition_filters = ['1', '2']

    # 납부기준일 선택
    fee_date_filter = request.GET.get('fee_date', '')
    if not fee_date_filter:
        # 초기값: no=1 (2025년 9월 1일)
        fee_date_filter = '1'

    # 모든 납부기준일 가져오기
    all_fee_dates = FixFeeDate.objects.all().order_by('no')

    # 선택된 납부기준일과 그 다음 2개월 가져오기
    try:
        selected_fee_date_no = int(fee_date_filter)
        # 선택된 날짜부터 3개월치 가져오기
        fee_dates_for_matrix = FixFeeDate.objects.filter(
            no__gte=selected_fee_date_no,
            no__lt=selected_fee_date_no + 3
        ).order_by('no')[:3]
    except:
        fee_dates_for_matrix = FixFeeDate.objects.all().order_by('no')[:3]

    # 조건에 맞는 업체 가져오기
    companies = Company.objects.filter(
        nType=1,  # 고정비토탈
        nCondition__in=condition_filters
    ).order_by('sName2')

    # 행렬 데이터 생성
    matrix_data = []
    for company in companies:
        row = {
            'company': company,
            'cells': []
        }

        for fee_date in fee_dates_for_matrix:
            # FixFee 데이터 찾기
            fixfee = FixFee.objects.filter(
                noCompany=company.no,
                noFixFeeDate=fee_date.no
            ).first()

            if fixfee:
                # 데이터가 있는 경우
                payment_type_display = fixfee.get_payment_type_display_custom()
                cell_data = {
                    'status': 'paid',
                    'display': f"{payment_type_display}({fixfee.nFixFee:,}원)",
                    'fixfee_id': fixfee.no,
                    'company_id': company.no,
                    'fee_date_id': fee_date.no
                }
            else:
                # 미납인 경우
                cell_data = {
                    'status': 'unpaid',
                    'display': '미납',
                    'company_id': company.no,
                    'fee_date_id': fee_date.no
                }

            row['cells'].append(cell_data)

        matrix_data.append(row)

    context = {
        'current_staff': current_staff,
        'all_fee_dates': all_fee_dates,
        'fee_dates_for_matrix': fee_dates_for_matrix,
        'matrix_data': matrix_data,
        'condition_choices': Company.CONDITION_CHOICES,
        'condition_filters': condition_filters,
        'fee_date_filter': fee_date_filter,
    }

    return render(request, 'fixfee/fixfee_status.html', context)


def get_company_info(request):
    """업체 정보 조회 (AJAX)"""

    company_id = request.GET.get('company_id')
    if not company_id:
        return JsonResponse({'error': '업체 ID가 필요합니다.'}, status=400)

    try:
        company = Company.objects.get(no=company_id)
        return JsonResponse({
            'no': company.no,
            'sName1': company.sName1,
            'sName2': company.sName2,
            'nType': company.nType,
            'nFixFee': company.nFixFee,  # 월고정비 추가
        })
    except Company.DoesNotExist:
        return JsonResponse({'error': '업체를 찾을 수 없습니다.'}, status=404)
