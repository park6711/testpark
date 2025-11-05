from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from django.views.generic import ListView
from django.utils.decorators import method_decorator
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from .models import ClientReport, CompanyReport, CompanyReportFile
from company.models import Company
from staff.models import Staff
from order.models import Order
from point.models import Point
from datetime import datetime
from django.utils import timezone

def contract_list(request):
    """계약 목록 페이지"""
    return HttpResponse("Contract List - 계약 관리 페이지입니다.")

def companyreport_list(request):
    """계약보고 리스트 페이지"""

    # 로그인 체크
    if 'staff_user' not in request.session:
        messages.warning(request, '로그인이 필요한 서비스입니다.')
        return redirect('/auth/login/?next=/contract/companyreport/')

    # 현재 로그인한 스태프 정보
    current_staff = None
    has_write_permission = False
    if 'staff_user' in request.session:
        try:
            current_staff = Staff.objects.get(no=request.session['staff_user']['no'])
            # nContractAuthority가 2(쓰기권한)인 경우만 수정 가능
            has_write_permission = current_staff.nContractAuthority >= 2
        except Staff.DoesNotExist:
            pass

    # 활동상태 필터 (Company.nCondition)
    condition_filters = request.GET.getlist('condition')
    if not condition_filters:
        condition_filters = ['1', '2']  # 기본값: 정상, 일시정지

    # 보고구분 필터 (CompanyReport.nType)
    type_filters = request.GET.getlist('type')

    # 공사유형 필터 (CompanyReport.nConType)
    contype_filters = request.GET.getlist('contype')

    # 기본 쿼리셋
    queryset = CompanyReport.objects.all()

    # Company 조건으로 필터링
    if condition_filters:
        company_nos = Company.objects.filter(
            nCondition__in=condition_filters
        ).values_list('no', flat=True)
        queryset = queryset.filter(noCompany__in=company_nos)

    # 보고구분으로 필터링
    if type_filters:
        queryset = queryset.filter(nType__in=type_filters)

    # 공사유형으로 필터링
    if contype_filters:
        queryset = queryset.filter(nConType__in=contype_filters)

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
            Q(sCompanyMemo__icontains=search_query) |
            Q(sStaffMemo__icontains=search_query) |
            Q(sPost__icontains=search_query) |
            Q(noCompany__in=company_search)
        )

    # 정렬 처리
    sort_by = request.GET.get('sort', '-no')  # 기본값: no 내림차순

    # 유효한 정렬 필드인지 확인
    valid_sort_fields = ['no', '-no', 'timeStamp', '-timeStamp']
    if sort_by not in valid_sort_fields:
        sort_by = '-no'

    queryset = queryset.order_by(sort_by)

    # 페이징
    from django.core.paginator import Paginator
    paginator = Paginator(queryset, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # 각 CompanyReport에 Company 정보 추가
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
        'has_write_permission': has_write_permission,
        'companyreports': page_obj,
        'all_companies': all_companies,
        'search_query': search_query,
        'condition_filters': [int(c) for c in condition_filters],
        'type_filters': [int(c) for c in type_filters] if type_filters else [],
        'contype_filters': [int(c) for c in contype_filters] if contype_filters else [],
        'total_count': queryset.count(),
        'sort_by': sort_by,
        'TYPE_CHOICES': CompanyReport.TYPE_CHOICES,
        'CONSTRUCTION_TYPE_CHOICES': CompanyReport.CONSTRUCTION_TYPE_CHOICES,
    }

    return render(request, 'contract/companyreport_list.html', context)

def clientreport_list(request):
    """고객계약보고 리스트 페이지"""
    # 로그인 체크
    if 'staff_user' not in request.session:
        messages.warning(request, '로그인이 필요한 서비스입니다.')
        return redirect('/auth/login/?next=/contract/clientreport/')

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
    # 로그인 체크
    if 'staff_user' not in request.session:
        messages.warning(request, '로그인이 필요한 서비스입니다.')
        return redirect(f'/auth/login/?next=/contract/clientreport/{pk}/')

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
    # 로그인 체크
    if 'staff_user' not in request.session:
        messages.warning(request, '로그인이 필요한 서비스입니다.')
        return redirect(f'/auth/login/?next=/contract/clientreport/{pk}/edit/')

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
    # 로그인 체크
    if 'staff_user' not in request.session:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': '로그인이 필요합니다.'}, status=401)
        else:
            messages.warning(request, '로그인이 필요한 서비스입니다.')
            return redirect(f'/auth/login/?next=/contract/clientreport/{pk}/delete/')

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

@csrf_exempt
@require_http_methods(["POST"])
def assign_company(request):
    """업체 배정 API"""
    try:
        # 로그인 확인
        if 'staff_user' not in request.session:
            return JsonResponse({
                'success': False,
                'error': '로그인이 필요합니다.'
            }, status=401)

        # 권한 확인
        current_staff = Staff.objects.get(no=request.session['staff_user']['no'])
        if current_staff.nContractAuthority < 2:
            return JsonResponse({
                'success': False,
                'error': '업체 배정 권한이 없습니다.'
            }, status=403)

        # JSON 데이터 파싱
        data = json.loads(request.body)
        report_no = data.get('report_no')
        company_no = data.get('company_no')

        if not report_no or not company_no:
            return JsonResponse({
                'success': False,
                'error': '필수 파라미터가 누락되었습니다.'
            }, status=400)

        # CompanyReport 조회
        try:
            company_report = CompanyReport.objects.get(no=report_no)
        except CompanyReport.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': '계약보고를 찾을 수 없습니다.'
            }, status=404)

        # Company 조회
        try:
            company = Company.objects.get(no=company_no)
        except Company.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': '업체를 찾을 수 없습니다.'
            }, status=404)

        # 기존 업체와 동일한 경우 처리
        if company_report.noCompany == company_no:
            return JsonResponse({
                'success': True,
                'message': f'이미 {company.sName1}에 배정되어 있습니다.'
            })

        # 업체 배정 (재배정 가능)
        old_company_no = company_report.noCompany
        company_report.noCompany = company_no
        company_report.save()

        # 재배정인 경우와 신규 배정인 경우 구분하여 메시지 반환
        if old_company_no:
            # 재배정인 경우
            try:
                old_company = Company.objects.get(no=old_company_no)
                message = f'{old_company.sName1}에서 {company.sName1}로 변경되었습니다.'
            except Company.DoesNotExist:
                message = f'{company.sName1}로 변경되었습니다.'
        else:
            # 신규 배정인 경우
            message = f'{company.sName1}에 배정되었습니다.'

        return JsonResponse({
            'success': True,
            'message': message
        })

    except Staff.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': '스태프 정보를 찾을 수 없습니다.'
        }, status=404)
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': '잘못된 JSON 형식입니다.'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'업체 배정 중 오류가 발생했습니다: {str(e)}'
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def update_company_name(request):
    """업체명(구글)(sCompanyName) 변경 API"""
    try:
        # 로그인 확인
        if 'staff_user' not in request.session:
            return JsonResponse({
                'success': False,
                'error': '로그인이 필요합니다.'
            }, status=401)

        # JSON 데이터 파싱
        data = json.loads(request.body)
        report_id = data.get('report_id')
        company_name = data.get('company_name', '')

        if report_id is None:
            return JsonResponse({
                'success': False,
                'error': '필수 파라미터가 누락되었습니다.'
            }, status=400)

        # CompanyReport 조회
        try:
            company_report = CompanyReport.objects.get(no=report_id)
        except CompanyReport.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': '계약보고를 찾을 수 없습니다.'
            }, status=404)

        # sCompanyName 업데이트
        company_report.sCompanyName = company_name
        company_report.save()

        return JsonResponse({
            'success': True,
            'message': '업체명(구글)이 성공적으로 업데이트되었습니다.'
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': '잘못된 JSON 형식입니다.'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'업체명 업데이트 중 오류가 발생했습니다: {str(e)}'
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def update_report_type(request):
    """보고구분(nType) 변경 API"""
    try:
        # 로그인 확인
        if 'staff_user' not in request.session:
            return JsonResponse({
                'success': False,
                'error': '로그인이 필요합니다.'
            }, status=401)

        # JSON 데이터 파싱
        data = json.loads(request.body)
        report_id = data.get('report_id')
        new_type = data.get('new_type')

        if report_id is None or new_type is None:
            return JsonResponse({
                'success': False,
                'error': '필수 파라미터가 누락되었습니다.'
            }, status=400)

        # CompanyReport 조회
        try:
            company_report = CompanyReport.objects.get(no=report_id)
        except CompanyReport.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': '계약보고를 찾을 수 없습니다.'
            }, status=404)

        # nType 유효성 검사
        valid_types = [choice[0] for choice in CompanyReport.TYPE_CHOICES]
        if int(new_type) not in valid_types:
            return JsonResponse({
                'success': False,
                'error': '유효하지 않은 보고구분입니다.'
            }, status=400)

        # nType 변경
        company_report.nType = int(new_type)
        company_report.save()

        return JsonResponse({
            'success': True,
            'message': '보고구분이 성공적으로 변경되었습니다.'
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': '잘못된 JSON 형식입니다.'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'보고구분 변경 중 오류가 발생했습니다: {str(e)}'
        }, status=500)

def companyreport_detail(request, pk):
    """업체계약보고 상세보기/수정"""

    # 로그인 체크 - 세션에 staff_user가 없으면 로그인 페이지로 리디렉션
    if 'staff_user' not in request.session:
        messages.warning(request, '로그인이 필요한 서비스입니다.')
        return redirect(f'/auth/login/?next=/contract/companyreport/{pk}/detail/')

    report = get_object_or_404(CompanyReport, pk=pk)

    # Company 정보 가져오기
    try:
        company = Company.objects.get(no=report.noCompany)
        report.company = company
    except Company.DoesNotExist:
        report.company = None

    current_staff = None
    has_write_permission = False
    if 'staff_user' in request.session:
        try:
            current_staff = Staff.objects.get(no=request.session['staff_user']['no'])
            # nContractAuthority가 2(쓰기권한)인 경우만 수정 가능
            has_write_permission = current_staff.nContractAuthority >= 2
        except Staff.DoesNotExist:
            pass

    # 권한에 따라 모드 자동 결정
    if has_write_permission:
        mode = request.GET.get('mode', 'edit')  # 쓰기권한이 있으면 기본 edit
        action = request.GET.get('action', 'edit')
    else:
        mode = 'view'  # 읽기권한만 있으면 view 고정
        action = 'view'

    if request.method == 'POST':
        # POST 요청 처리 (쓰기권한이 있는 경우만)
        if not has_write_permission:
            messages.error(request, '수정 권한이 없습니다.')
            return redirect('contract:companyreport_detail', pk=pk)
        return handle_companyreport_save(request, report, action)

    # 보고구분별 액션 가능 여부 체크
    available_actions = get_available_actions(report, has_write_permission)

    # 관련 데이터 가져오기
    all_companies = Company.objects.filter(nCondition__in=[1, 2]).order_by('sName2', 'sName1')

    # 포인트 정보 가져오기
    from point.models import Point
    try:
        latest_point = Point.objects.filter(noCompany=report.noCompany).order_by('-no').first()
        remain_point = latest_point.nRemainPoint if latest_point else 0
    except:
        remain_point = 0

    # 사업자 목록 가져오기
    from license.models import License
    tax_companies = License.objects.filter(noCompany=report.noCompany).values_list('sCompanyName', flat=True)
    accounts = License.objects.filter(noCompany=report.noCompany).values_list('sAccount', flat=True)

    context = {
        'report': report,
        'current_staff': current_staff,
        'mode': mode,
        'action': action,
        'all_companies': all_companies,
        'available_actions': available_actions,
        'has_write_permission': has_write_permission,
        'remain_point': remain_point,
        'tax_companies': list(tax_companies),
        'accounts': list(accounts),
        'TYPE_CHOICES': CompanyReport.TYPE_CHOICES,
        'CONSTRUCTION_TYPE_CHOICES': CompanyReport.CONSTRUCTION_TYPE_CHOICES,
        'REFUND_TYPE_CHOICES': CompanyReport.REFUND_TYPE_CHOICES,
    }

    return render(request, 'contract/companyreport_detail.html', context)

def companyreport_edit(request, pk):
    """업체계약보고 수정"""
    return companyreport_detail(request, pk)

def companyreport_create(request):
    """업체계약보고 신규 생성"""
    current_staff = None
    if 'staff_user' in request.session:
        try:
            current_staff = Staff.objects.get(no=request.session['staff_user']['no'])
        except Staff.DoesNotExist:
            pass

    if request.method == 'POST':
        # 새 보고서 생성
        report = CompanyReport()
        report.sWorker = current_staff.sNick if current_staff else ''
        return handle_companyreport_save(request, report, 'create')

    # GET 요청 - 새 보고서 작성 폼 표시
    all_companies = Company.objects.filter(nCondition__in=[1, 2]).order_by('sName2', 'sName1')

    context = {
        'current_staff': current_staff,
        'mode': 'create',
        'action': 'create',
        'all_companies': all_companies,
        'TYPE_CHOICES': CompanyReport.TYPE_CHOICES,
        'CONSTRUCTION_TYPE_CHOICES': CompanyReport.CONSTRUCTION_TYPE_CHOICES,
        'REFUND_TYPE_CHOICES': CompanyReport.REFUND_TYPE_CHOICES,
    }

    return render(request, 'contract/companyreport_detail.html', context)

@csrf_exempt
@require_http_methods(["POST"])
def companyreport_delete(request, pk):
    """업체계약보고 삭제"""
    try:
        report = get_object_or_404(CompanyReport, pk=pk)

        # 이후 보고가 있으면 삭제 불가
        if report.noNext and report.noNext > 0:
            return JsonResponse({
                'success': False,
                'error': '이후 보고가 있어 삭제할 수 없습니다.'
            }, status=400)

        # 이전 보고가 있으면 연결 해제
        if report.noPre and report.noPre > 0:
            try:
                prev_report = CompanyReport.objects.get(no=report.noPre)
                prev_report.noNext = None
                prev_report.save()
            except CompanyReport.DoesNotExist:
                pass

        report.delete()

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True})
        else:
            messages.success(request, '업체계약보고가 삭제되었습니다.')
            return redirect('contract:companyreport_list')

    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': str(e)})
        else:
            messages.error(request, f'삭제 중 오류가 발생했습니다: {str(e)}')
            return redirect('contract:companyreport_list')

def companyreport_increase(request, pk):
    """증액 보고"""
    # 로그인 체크
    if 'staff_user' not in request.session:
        messages.warning(request, '로그인이 필요한 서비스입니다.')
        return redirect(f'/auth/login/?next=/contract/companyreport/{pk}/increase/')

    target_report = get_object_or_404(CompanyReport, pk=pk)

    # pk가 증액 보고서(nType 2 또는 3)인 경우 - 수정 모드
    if target_report.nType in [2, 3]:
        mode = 'edit'
        report = target_report
        original_noPre = report.noPre  # noPre 변경 감지를 위해 원본 저장
        parent_report = get_object_or_404(CompanyReport, pk=report.noPre) if report.noPre else None

        # 디버깅: 현재 저장된 값 확인
        print(f"[DEBUG] Edit Mode - Report #{report.no}")
        print(f"[DEBUG] nConMoney in DB: {report.nConMoney}")
        print(f"[DEBUG] nAppPoint in DB: {report.nAppPoint}")
        print(f"[DEBUG] nDeposit in DB: {report.nDeposit}")

        if request.method == 'POST':
            # noPre가 변경되었는지 확인
            new_noPre = request.POST.get('noPre', '')
            new_noPre = int(new_noPre) if new_noPre else None

            # noPre가 변경되었다면 이전 parent의 noNext를 제거
            if original_noPre and new_noPre != original_noPre:
                try:
                    old_parent = CompanyReport.objects.get(no=original_noPre)
                    old_parent.noNext = None
                    old_parent.save()
                    print(f"[DEBUG] Removed noNext from old parent #{original_noPre}")
                except CompanyReport.DoesNotExist:
                    pass

            return handle_companyreport_save(request, report, 'increase', parent_report)

    # pk가 계약 보고서(nType 0 또는 1)인 경우 - 신규 증액 모드
    else:
        mode = 'create'
        parent_report = target_report

        # 계약(nType 0 또는 1)이 아니면 증액 불가
        if parent_report.nType not in [0, 1]:
            messages.error(request, '계약 보고서에서만 증액이 가능합니다.')
            return redirect('contract:companyreport_detail', pk=pk)

        # 이후 보고가 있으면 증액 불가
        if parent_report.noNext and parent_report.noNext > 0:
            messages.error(request, '이후 보고가 있어 증액할 수 없습니다. 증액/감액/취소는 1회만 가능합니다.')
            return redirect('contract:companyreport_detail', pk=pk)

        # 새 보고서 생성 (증액)
        report = CompanyReport()
        report.noPre = parent_report.no
        report.nType = 2  # 증액(입금X) 기본값

        # 부모 보고서에서 데이터 복사
        copy_fields = ['sCompanyName', 'noCompany', 'sName', 'sPhone', 'nConType',
                       'sPost', 'noAssign', 'noOrder', 'sArea', 'nRefund', 'sTaxCompany', 'sAccount',
                       'dateContract', 'dateSchedule']
        for field in copy_fields:
            setattr(report, field, getattr(parent_report, field))

        report.nPreConMoney = parent_report.nConMoney
        report.nPreFee = parent_report.nFee

        if request.method == 'POST':
            return handle_companyreport_save(request, report, 'increase', parent_report)

    context = get_report_context(request, report, 'increase')
    context['mode'] = mode
    context['parent_report'] = parent_report

    # 업체명 정보 추가
    company_name = ""
    if report.noCompany:
        try:
            company = Company.objects.get(no=report.noCompany)
            company_name = company.sName2
        except Company.DoesNotExist:
            company_name = "삭제된 업체"

    context['company_name'] = company_name

    return render(request, 'contract/companyreport_increase.html', context)

def companyreport_decrease(request, pk):
    """감액 보고"""
    # 로그인 체크
    if 'staff_user' not in request.session:
        messages.warning(request, '로그인이 필요한 서비스입니다.')
        return redirect(f'/auth/login/?next=/contract/companyreport/{pk}/decrease/')

    target_report = get_object_or_404(CompanyReport, pk=pk)

    # pk가 감액 보고서(nType 4 또는 5)인 경우 - 수정 모드
    if target_report.nType in [4, 5]:
        mode = 'edit'
        report = target_report
        original_noPre = report.noPre  # noPre 변경 감지를 위해 원본 저장
        parent_report = get_object_or_404(CompanyReport, pk=report.noPre) if report.noPre else None

        if request.method == 'POST':
            # noPre가 변경되었는지 확인
            new_noPre = request.POST.get('noPre', '')
            new_noPre = int(new_noPre) if new_noPre else None

            # noPre가 변경되었다면 이전 parent의 noNext를 제거
            if original_noPre and new_noPre != original_noPre:
                try:
                    old_parent = CompanyReport.objects.get(no=original_noPre)
                    old_parent.noNext = None
                    old_parent.save()
                    print(f"[DEBUG] Removed noNext from old parent #{original_noPre}")
                except CompanyReport.DoesNotExist:
                    pass

            return handle_companyreport_save(request, report, 'decrease', parent_report)

    # pk가 계약 보고서(nType 0 또는 1)인 경우 - 신규 감액 모드
    else:
        mode = 'create'
        parent_report = target_report

        # 계약(nType 0 또는 1)이 아니면 감액 불가
        if parent_report.nType not in [0, 1]:
            messages.error(request, '계약 보고서에서만 감액이 가능합니다.')
            return redirect('contract:companyreport_detail', pk=pk)

        # 이후 보고가 있으면 감액 불가
        if parent_report.noNext and parent_report.noNext > 0:
            messages.error(request, '이후 보고가 있어 감액할 수 없습니다. 증액/감액/취소는 1회만 가능합니다.')
            return redirect('contract:companyreport_detail', pk=pk)

        # 새 보고서 생성 (감액)
        report = CompanyReport()
        report.noPre = parent_report.no
        report.nType = 4  # 감액(환불X) 기본값

        # 부모 보고서에서 데이터 복사
        copy_fields = ['sCompanyName', 'noCompany', 'sName', 'sPhone', 'nConType',
                       'sPost', 'noAssign', 'noOrder', 'sArea', 'nRefund', 'sTaxCompany', 'sAccount',
                       'dateContract', 'dateSchedule']
        for field in copy_fields:
            setattr(report, field, getattr(parent_report, field))

        report.nPreConMoney = parent_report.nConMoney
        report.nPreFee = parent_report.nFee

        if request.method == 'POST':
            # 포인트는 별도 버튼으로 처리하므로 제출 시에는 포인트 생성하지 않음
            return handle_companyreport_save(request, report, 'decrease', parent_report)

    # 현재 스텝 정보
    current_staff = None
    if 'staff_user' in request.session:
        try:
            current_staff = Staff.objects.get(no=request.session['staff_user']['no'])
        except Staff.DoesNotExist:
            pass

    # 업체명 정보 추가
    company_name = ""
    if report.noCompany:
        try:
            company = Company.objects.get(no=report.noCompany)
            company_name = company.sName2
        except Company.DoesNotExist:
            company_name = "삭제된 업체"

    # 사업자 목록 (환불계좌 드롭다운용)
    from license.models import License
    accounts = License.objects.filter(noCompany=report.noCompany).values_list('sAccount', flat=True)

    context = {
        'report': report,
        'parent_report': parent_report,
        'current_staff': current_staff,
        'company_name': company_name,
        'mode': mode,
        'accounts': list(accounts),
        'TYPE_CHOICES': CompanyReport.TYPE_CHOICES,
        'CONSTRUCTION_TYPE_CHOICES': CompanyReport.CONSTRUCTION_TYPE_CHOICES,
        'REFUND_TYPE_CHOICES': CompanyReport.REFUND_TYPE_CHOICES,
    }

    return render(request, 'contract/companyreport_decrease.html', context)

def companyreport_cancel(request, pk):
    """취소 보고"""
    # 로그인 체크
    if 'staff_user' not in request.session:
        messages.warning(request, '로그인이 필요한 서비스입니다.')
        return redirect(f'/auth/login/?next=/contract/companyreport/{pk}/cancel/')

    target_report = get_object_or_404(CompanyReport, pk=pk)

    # pk가 취소 보고서(nType 6 또는 7)인 경우 - 수정 모드
    if target_report.nType in [6, 7]:
        mode = 'edit'
        report = target_report
        original_noPre = report.noPre  # noPre 변경 감지를 위해 원본 저장
        parent_report = get_object_or_404(CompanyReport, pk=report.noPre) if report.noPre else None

        if request.method == 'POST':
            # noPre가 변경되었는지 확인
            new_noPre = request.POST.get('noPre', '')
            new_noPre = int(new_noPre) if new_noPre else None

            # noPre가 변경되었다면 이전 parent의 noNext를 제거
            if original_noPre and new_noPre != original_noPre:
                try:
                    old_parent = CompanyReport.objects.get(no=original_noPre)
                    old_parent.noNext = None
                    old_parent.save()
                    print(f"[DEBUG] Removed noNext from old parent #{original_noPre}")
                except CompanyReport.DoesNotExist:
                    pass

            return handle_companyreport_save(request, report, 'cancel', parent_report)

    # pk가 계약 보고서(nType 0 또는 1)인 경우 - 신규 취소 모드
    else:
        mode = 'create'
        parent_report = target_report

        # 계약(nType 0 또는 1)이 아니면 취소 불가
        if parent_report.nType not in [0, 1]:
            messages.error(request, '계약 보고서에서만 취소가 가능합니다.')
            return redirect('contract:companyreport_detail', pk=pk)

        # 이후 보고가 있으면 취소 불가
        if parent_report.noNext and parent_report.noNext > 0:
            messages.error(request, '이후 보고가 있어 취소할 수 없습니다. 증액/감액/취소는 1회만 가능합니다.')
            return redirect('contract:companyreport_detail', pk=pk)

        # 새 보고서 생성 (취소)
        report = CompanyReport()
        report.noPre = parent_report.no
        report.nType = 6  # 취소(환불X) 기본값

        # 부모 보고서에서 데이터 복사
        copy_fields = ['sCompanyName', 'noCompany', 'sName', 'sPhone', 'nConType',
                       'sPost', 'noAssign', 'noOrder', 'sArea', 'nRefund', 'sTaxCompany', 'sAccount',
                       'dateContract', 'dateSchedule']
        for field in copy_fields:
            setattr(report, field, getattr(parent_report, field))

        report.nPreConMoney = parent_report.nConMoney
        report.nPreFee = parent_report.nFee
        report.nConMoney = -parent_report.nConMoney  # 취소는 마이너스 금액
        report.nFee = -parent_report.nFee
        report.nDemand = -parent_report.nFee

        if request.method == 'POST':
            # 포인트는 별도 버튼으로 처리하므로 제출 시에는 포인트 생성하지 않음
            return handle_companyreport_save(request, report, 'cancel', parent_report)

    # 현재 스텝 정보
    current_staff = None
    if 'staff_user' in request.session:
        try:
            current_staff = Staff.objects.get(no=request.session['staff_user']['no'])
        except Staff.DoesNotExist:
            pass

    # 업체명 정보 추가
    company_name = ""
    if report.noCompany:
        try:
            company = Company.objects.get(no=report.noCompany)
            company_name = company.sName2
        except Company.DoesNotExist:
            company_name = "삭제된 업체"

    # 사업자 목록 (환불계좌 드롭다운용)
    from license.models import License
    accounts = License.objects.filter(noCompany=report.noCompany).values_list('sAccount', flat=True)

    context = {
        'report': report,
        'parent_report': parent_report,
        'current_staff': current_staff,
        'company_name': company_name,
        'mode': mode,
        'accounts': list(accounts),
        'TYPE_CHOICES': CompanyReport.TYPE_CHOICES,
        'CONSTRUCTION_TYPE_CHOICES': CompanyReport.CONSTRUCTION_TYPE_CHOICES,
        'REFUND_TYPE_CHOICES': CompanyReport.REFUND_TYPE_CHOICES,
    }

    return render(request, 'contract/companyreport_cancel.html', context)

def handle_companyreport_save(request, report, action, parent_report=None):
    """CompanyReport 저장 처리"""
    try:
        # 디버깅: POST 데이터 확인
        print(f"\n[DEBUG] ========== CompanyReport Save ==========")
        print(f"[DEBUG] action: {action}")
        print(f"[DEBUG] nConMoney: '{request.POST.get('nConMoney', 'NOT_FOUND')}'")
        print(f"[DEBUG] nAppPoint: '{request.POST.get('nAppPoint', 'NOT_FOUND')}'")
        print(f"[DEBUG] nDeposit: '{request.POST.get('nDeposit', 'NOT_FOUND')}'")
        print(f"[DEBUG] file in FILES: {'file' in request.FILES}")
        if 'file' in request.FILES:
            print(f"[DEBUG] file name: {request.FILES['file'].name}")
            print(f"[DEBUG] file size: {request.FILES['file'].size} bytes")
        print(f"[DEBUG] Content-Type: {request.content_type}")
        print(f"[DEBUG] ==========================================\n")

        # 기본 필드 처리
        if 'noCompany' in request.POST:
            report.noCompany = int(request.POST.get('noCompany', 0))
        if 'sCompanyName' in request.POST:
            report.sCompanyName = request.POST.get('sCompanyName', '')
        if 'sPost' in request.POST:
            report.sPost = request.POST.get('sPost', '')
        if 'nConType' in request.POST:
            report.nConType = int(request.POST.get('nConType', 0))
        if 'sName' in request.POST:
            report.sName = request.POST.get('sName', '')
        if 'sPhone' in request.POST:
            report.sPhone = request.POST.get('sPhone', '')
        if 'sArea' in request.POST:
            report.sArea = request.POST.get('sArea', '')

        # 날짜 필드
        if 'dateContract' in request.POST:
            date_str = request.POST.get('dateContract')
            if date_str:
                report.dateContract = datetime.strptime(date_str, '%Y-%m-%d').date()

        if 'dateSchedule' in request.POST:
            date_str = request.POST.get('dateSchedule')
            if date_str:
                report.dateSchedule = datetime.strptime(date_str, '%Y-%m-%d').date()

        if 'dateDeposit' in request.POST:
            date_str = request.POST.get('dateDeposit')
            if date_str:
                report.dateDeposit = datetime.strptime(date_str, '%Y-%m-%d').date()
            else:
                report.dateDeposit = None

        # 금액 필드 - 강력한 정제 로직
        # 구글 금액 필드 (문자열로 저장)
        if 'sConMoney' in request.POST:
            report.sConMoney = request.POST.get('sConMoney', '')

        if 'nConMoney' in request.POST:
            raw_value = request.POST.get('nConMoney', '0')
            # 모든 비숫자 문자 제거 (쉼표, 공백 등)
            import re
            clean_value = re.sub(r'[^\d-]', '', raw_value)
            if not clean_value:
                clean_value = '0'
            try:
                report.nConMoney = int(clean_value)
            except ValueError:
                report.nConMoney = 0
            print(f"[DEBUG] nConMoney: raw='{raw_value}' -> clean='{clean_value}' -> int={report.nConMoney}")

        if 'nFee' in request.POST:
            raw_value = request.POST.get('nFee', '0')
            clean_value = re.sub(r'[^\d-]', '', raw_value)
            if not clean_value:
                clean_value = '0'
            try:
                report.nFee = int(clean_value)
            except ValueError:
                report.nFee = 0

        if 'nAppPoint' in request.POST:
            raw_value = request.POST.get('nAppPoint', '0')
            clean_value = re.sub(r'[^\d-]', '', raw_value)
            if not clean_value:
                clean_value = '0'
            try:
                report.nAppPoint = int(clean_value)
            except ValueError:
                report.nAppPoint = 0
            print(f"[DEBUG] nAppPoint: raw='{raw_value}' -> clean='{clean_value}' -> int={report.nAppPoint}")

        if 'nDeposit' in request.POST:
            raw_value = request.POST.get('nDeposit', '0')
            clean_value = re.sub(r'[^\d-]', '', raw_value)
            if not clean_value:
                clean_value = '0'
            try:
                report.nDeposit = int(clean_value)
            except ValueError:
                report.nDeposit = 0
            print(f"[DEBUG] nDeposit: raw='{raw_value}' -> clean='{clean_value}' -> int={report.nDeposit}")

        # nDemand 계산
        report.nDemand = report.nFee - report.nAppPoint

        # nExcess 계산
        report.nExcess = report.nDeposit - report.nDemand

        # 입금 관련 추가 필드 처리
        if 'nRefund' in request.POST:
            report.nRefund = int(request.POST.get('nRefund', 0))
        if 'sTaxCompany' in request.POST:
            report.sTaxCompany = request.POST.get('sTaxCompany', '')
        if 'sAccount' in request.POST:
            report.sAccount = request.POST.get('sAccount', '')

        # 기존 단일 파일 처리 (호환성 유지)
        if 'file' in request.FILES:
            uploaded_file = request.FILES['file']
            report.file = uploaded_file
            print(f"[DEBUG] Single file uploaded: {uploaded_file.name} ({uploaded_file.size} bytes)")
        if 'sFile' in request.POST:
            report.sFile = request.POST.get('sFile', '')
        if 'sMemo' in request.POST:
            report.sMemo = request.POST.get('sMemo', '')
        if 'sCompanyMemo' in request.POST:
            report.sCompanyMemo = request.POST.get('sCompanyMemo', '')
        if 'sStaffMemo' in request.POST:
            report.sStaffMemo = request.POST.get('sStaffMemo', '')

        # 증액/감액/취소 전용 필드 처리
        if action in ['increase', 'decrease', 'cancel']:
            if 'noPre' in request.POST:
                nopre_val = request.POST.get('noPre', '')
                report.noPre = int(nopre_val) if nopre_val else None
            if 'nPreConMoney' in request.POST:
                report.nPreConMoney = int(request.POST.get('nPreConMoney', 0))
            if 'nPreFee' in request.POST:
                report.nPreFee = int(request.POST.get('nPreFee', 0))
            if 'noOrder' in request.POST:
                noorder_val = request.POST.get('noOrder', '')
                report.noOrder = int(noorder_val) if noorder_val else None
            if 'noAssign' in request.POST:
                noassign_val = request.POST.get('noAssign', '')
                report.noAssign = int(noassign_val) if noassign_val else None

        # nType 자동 설정 (입금일 여부에 따라)
        if action in ['create', 'edit']:
            if report.dateDeposit:  # 입금일이 있으면
                report.nType = 1  # 계약(입금O)
            else:
                report.nType = 0  # 계약(입금X)
        elif action == 'increase':
            if report.dateDeposit:  # 입금일이 있으면
                report.nType = 3  # 증액(입금O)
            else:
                report.nType = 2  # 증액(입금X)
        elif action == 'decrease':
            if report.dateDeposit:  # 입금일(환불일)이 있으면
                report.nType = 5  # 감액(환불O)
            else:
                report.nType = 4  # 감액(환불X)
        elif action == 'cancel':
            if report.dateDeposit:  # 입금일(환불일)이 있으면
                report.nType = 7  # 취소(환불O)
            else:
                report.nType = 6  # 취소(환불X)

        # 타임스탬프 설정
        if not report.timeStamp:
            report.timeStamp = timezone.now()

        # 보고자 설정
        if not report.sWorker and 'staff_user' in request.session:
            try:
                current_staff = Staff.objects.get(no=request.session['staff_user']['no'])
                report.sWorker = current_staff.sNick
            except:
                pass

        # 저장
        report.save()

        # 다중 파일 업로드 처리
        if 'files' in request.FILES:
            files = request.FILES.getlist('files')
            current_staff_nick = ''
            if 'staff_user' in request.session:
                try:
                    current_staff = Staff.objects.get(no=request.session['staff_user']['no'])
                    current_staff_nick = current_staff.sNick
                except:
                    pass

            for uploaded_file in files:
                CompanyReportFile.objects.create(
                    report=report,
                    file=uploaded_file,
                    original_name=uploaded_file.name,
                    file_size=uploaded_file.size,
                    uploaded_by=current_staff_nick
                )
                print(f"[DEBUG] Multi-file uploaded: {uploaded_file.name} ({uploaded_file.size} bytes)")

        # 부모 보고서 업데이트 (증액/감액/취소의 경우)
        # noPre가 변경되었을 수 있으므로, report.noPre를 기준으로 새로운 parent를 찾아야 함
        if action in ['increase', 'decrease', 'cancel'] and report.noPre:
            try:
                # 현재 저장된 noPre 값으로 실제 parent 찾기
                actual_parent = CompanyReport.objects.get(no=report.noPre)
                actual_parent.noNext = report.no
                actual_parent.save()
                print(f"[DEBUG] Updated parent report #{actual_parent.no} noNext to {report.no}")
            except CompanyReport.DoesNotExist:
                print(f"[DEBUG] Parent report #{report.noPre} not found")

        # 포인트 처리는 수동으로만 (자동 처리 제거)
        # 사용자가 [포인트 차감 적용] 또는 [과입금 포인트 적립] 버튼을 명시적으로 클릭해야 함

        messages.success(request, f'업체계약보고가 {action} 되었습니다.')

        # 리다이렉트 결정
        if action in ['increase', 'decrease', 'cancel']:
            # 증액/감액/취소 수정(pk가 이미 존재)이면 목록으로, 신규 생성이면 목록으로
            if report.no and report.nType in [2, 3, 4, 5, 6, 7]:
                # 증액/감액/취소 보고서 수정 완료 -> 목록으로
                return redirect('contract:companyreport_list')
            else:
                # 신규 생성 -> 목록으로
                return redirect('contract:companyreport_list')
        else:
            # 일반 계약 보고서 -> 상세로
            return redirect('contract:companyreport_detail', pk=report.no)

    except Exception as e:
        messages.error(request, f'저장 중 오류가 발생했습니다: {str(e)}')
        if report.no:
            return redirect('contract:companyreport_detail', pk=report.no)
        else:
            return redirect('contract:companyreport_list')

def get_available_actions(report, has_write_permission=False):
    """보고구분별 사용 가능한 액션 반환"""
    actions = []

    # 권한에 따라 기본 액션 설정
    if has_write_permission:
        actions.append('edit')  # 쓰기권한이 있으면 수정 가능
    else:
        actions.append('view')  # 읽기권한만 있으면 보기만 가능

    # 쓰기권한이 있고, 이후 보고가 없는 경우에만 추가 액션 가능
    if has_write_permission and (not report.noNext or report.noNext == 0):
        if report.nType in [0, 1]:  # 계약
            actions.extend(['delete', 'increase', 'decrease', 'cancel'])
        elif report.nType in [2, 3]:  # 증액
            actions.append('delete')
        elif report.nType in [4, 5]:  # 감액
            actions.append('delete')
        elif report.nType in [6, 7]:  # 취소
            actions.append('delete')

    return actions

def get_report_context(request, report, action):
    """CompanyReport 컨텍스트 생성"""
    current_staff = None
    if 'staff_user' in request.session:
        try:
            current_staff = Staff.objects.get(no=request.session['staff_user']['no'])
        except Staff.DoesNotExist:
            pass

    all_companies = Company.objects.filter(nCondition__in=[1, 2]).order_by('sName2', 'sName1')

    # 포인트 정보
    from point.models import Point
    try:
        latest_point = Point.objects.filter(noCompany=report.noCompany).order_by('-no').first()
        remain_point = latest_point.nRemainPoint if latest_point else 0
    except:
        remain_point = 0

    # 사업자 목록
    from license.models import License
    tax_companies = License.objects.filter(noCompany=report.noCompany).values_list('sCompanyName', flat=True)
    accounts = License.objects.filter(noCompany=report.noCompany).values_list('sAccount', flat=True)

    return {
        'report': report,
        'current_staff': current_staff,
        'mode': action,
        'action': action,
        'all_companies': all_companies,
        'remain_point': remain_point,
        'tax_companies': list(tax_companies),
        'accounts': list(accounts),
        'TYPE_CHOICES': CompanyReport.TYPE_CHOICES,
        'CONSTRUCTION_TYPE_CHOICES': CompanyReport.CONSTRUCTION_TYPE_CHOICES,
        'REFUND_TYPE_CHOICES': CompanyReport.REFUND_TYPE_CHOICES,
    }

# API 함수들
@csrf_exempt
@require_http_methods(["POST"])
def companyreport_action_api(request, pk):
    """CompanyReport 액션 처리 API"""
    try:
        data = json.loads(request.body)
        action = data.get('action')

        if action == 'calculate_fee':
            # 수수료 계산
            con_type = int(data.get('con_type', 0))
            con_money = int(data.get('con_money', 0))

            if con_money <= 0:
                fee = 0
            elif con_type == 0:  # [카페건]인테리어/리모델링/기타 (5.5%)
                if con_money < 50000000:
                    fee = int(con_money * 0.055)
                else:
                    fee = int(50000000 * 0.055 + (con_money - 50000000) * 0.033)
            elif con_type == 1:  # [카테건]신축/증축/개축 (3.3%)
                fee = int(con_money * 0.033)
            elif con_type == 2:  # [소개건]인테리어/리모델링/기타 (3.3%)
                fee = int(con_money * 0.033)
            elif con_type == 3:  # [소개건]신축/증축/개축 (2.2%)
                fee = int(con_money * 0.022)
            else:
                fee = 0

            return JsonResponse({'success': True, 'fee': fee})

        elif action == 'search_order':
            # Order 검색
            post = data.get('post')
            from order.models import Order

            try:
                order = Order.objects.filter(sPost=post).first()
                if order:
                    return JsonResponse({
                        'success': True,
                        'order_no': order.no
                    })
                else:
                    return JsonResponse({
                        'success': False,
                        'message': '일치하는 의뢰를 찾을 수 없습니다.'
                    })
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'error': str(e)
                })

        else:
            return JsonResponse({
                'success': False,
                'error': '알 수 없는 액션입니다.'
            })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def calculate_fee_api(request):
    """수수료 계산 API"""
    try:
        data = json.loads(request.body)
        con_type = int(data.get('con_type', 0))
        con_money = int(data.get('con_money', 0))

        fee = CompanyReport().calculate_fee_static(con_type, con_money)

        return JsonResponse({
            'success': True,
            'fee': fee
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def process_point_api(request):
    """포인트 처리 API

    요구사항:
    - Point.noCompany = CompanyReport.noCompany
    - Point.time = 지금 시각
    - Point.nType = 0(수수료납부) 또는 2(과/미입금)
    - Point.noCompanyReport = CompanyReport.no
    - Point.sWorker = 현재 Staff.sNick
    - Point.nPrePoint = 이전 Point.nRemainPoint
    - Point.nUsePoint = CompanyReport.nExcess (과입금 적립 시)
    - Point.nRemainPoint = 자동계산 (nPrePoint + nUsePoint for 적립, nPrePoint - nUsePoint for 차감)
    """
    try:
        from point.models import Point
        data = json.loads(request.body)

        # 포인트 처리 로직
        company_no = int(data.get('company_no'))
        point_type = int(data.get('type'))  # 0:수수료납부(차감), 2:과/미입금(적립)
        use_point = int(data.get('use_point', 0))
        report_no = data.get('report_no')  # null 가능
        worker = data.get('worker', '')  # 프론트에서 전달받은 작업자

        # 최신 포인트 조회하여 이전 포인트 가져오기
        latest_point = Point.objects.filter(noCompany=company_no).order_by('-time', '-no').first()
        pre_point = latest_point.nRemainPoint if latest_point else 0

        # 새 포인트 레코드 생성
        point = Point()
        point.noCompany = company_no
        point.time = timezone.now()
        point.nType = point_type
        point.noCompanyReport = report_no if report_no else None
        point.nPrePoint = pre_point
        point.sWorker = worker

        # 포인트 계산
        if point_type == 0:  # 수수료납부 (차감)
            point.nUsePoint = -use_point  # 음수로 저장 (차감)
            point.nRemainPoint = pre_point - use_point
        elif point_type == 2:  # 과/미입금 (적립)
            point.nUsePoint = use_point  # 양수로 저장 (적립)
            point.nRemainPoint = pre_point + use_point
        else:
            # 기타 타입 (1: 수수료환불, 3: 페이백적립, 4: 닷컴포인트전환)
            point.nUsePoint = use_point
            point.nRemainPoint = pre_point + use_point

        # 포인트가 음수가 되지 않도록 검증
        if point.nRemainPoint < 0:
            return JsonResponse({
                'success': False,
                'error': '포인트 잔액이 부족합니다.'
            }, status=400)

        point.save()

        return JsonResponse({
            'success': True,
            'remain_point': point.nRemainPoint,
            'message': '포인트가 성공적으로 처리되었습니다.'
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def search_order_api(request):
    """Order 검색 API"""
    try:
        from order.models import Order
        data = json.loads(request.body)

        post = data.get('post')
        company_no = int(data.get('company_no', 0))

        # post로 Order 검색
        order = Order.objects.filter(sPost=post).first()

        if order:
            return JsonResponse({
                'success': True,
                'order_no': order.no
            })
        else:
            return JsonResponse({
                'success': False,
                'message': '일치하는 의뢰를 찾을 수 없습니다.'
            })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def search_assign_api(request):
    """Assign 검색 API"""
    try:
        from order.models import Assign
        data = json.loads(request.body)

        company_no = int(data.get('company_no', 0))
        order_no = int(data.get('order_no', 0))

        # company_no와 order_no로 Assign 검색
        assign = Assign.objects.filter(
            noCompany=company_no,
            noOrder=order_no
        ).first()

        if assign:
            return JsonResponse({
                'success': True,
                'assign_no': assign.no
            })
        else:
            return JsonResponse({
                'success': False,
                'message': '일치하는 할당을 찾을 수 없습니다.'
            })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def search_company_api(request):
    """업체 실시간 검색 API"""
    try:
        search_term = request.GET.get('q', '').strip()

        if not search_term:
            companies = Company.objects.all()[:20]
        else:
            companies = Company.objects.filter(
                Q(sName2__icontains=search_term) |
                Q(sName1__icontains=search_term)
            ).order_by('sName2')[:20]

        results = []
        for company in companies:
            results.append({
                'no': company.no,
                'sName2': company.sName2,
                'sName1': company.sName1,
                'display_name': company.sName2
            })

        return JsonResponse({
            'success': True,
            'companies': results
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def delete_report_file(request, file_id):
    """계약보고 첨부파일 삭제"""
    try:
        # 파일 찾기
        file_obj = get_object_or_404(CompanyReportFile, no=file_id)

        # 권한 체크 (쓰기권한이 있는 경우만)
        if "staff_user" not in request.session:
            return JsonResponse({
                "success": False,
                "error": "로그인이 필요합니다."
            }, status=401)

        try:
            current_staff = Staff.objects.get(no=request.session["staff_user"]["no"])
            if current_staff.nContractAuthority < 2:
                return JsonResponse({
                    "success": False,
                    "error": "삭제 권한이 없습니다."
                }, status=403)
        except Staff.DoesNotExist:
            return JsonResponse({
                "success": False,
                "error": "권한을 확인할 수 없습니다."
            }, status=403)

        # 파일명 저장 (응답용)
        file_name = file_obj.original_name

        # 파일 삭제
        file_obj.delete()

        return JsonResponse({
            "success": True,
            "message": f"{file_name} 파일이 삭제되었습니다."
        })

    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def create_refund_point(request):
    """감액 환불 포인트 즉시 생성"""
    try:
        data = json.loads(request.body)
        company_no = data.get("company_no")
        refund_amount = data.get("refund_amount", 0)
        pre_report_no = data.get("pre_report_no")
        
        # 로그인 체크
        if "staff_user" not in request.session:
            return JsonResponse({
                "success": False,
                "error": "로그인이 필요합니다."
            }, status=401)
        
        # 스태프 정보
        try:
            current_staff = Staff.objects.get(no=request.session["staff_user"]["no"])
            worker_name = current_staff.sNick
        except Staff.DoesNotExist:
            return JsonResponse({
                "success": False,
                "error": "스태프 정보를 찾을 수 없습니다."
            }, status=404)
        
        # 환불액이 음수가 아니면 오류
        if refund_amount >= 0:
            return JsonResponse({
                "success": False,
                "error": "환불액은 음수여야 합니다."
            }, status=400)
        
        # 이전 포인트 잔액 조회
        from point.models import Point
        last_point = Point.objects.filter(
            noCompany=company_no
        ).order_by("-time", "-no").first()
        
        nPrePoint = last_point.nRemainPoint if last_point else 0
        
        # 포인트 생성
        # refund_amount는 음수이므로 -refund_amount는 양수
        use_point = -refund_amount
        new_point = Point.objects.create(
            noCompany=company_no,
            time=timezone.now(),
            nType=1,  # 포인트 추가
            noCompanyReport=pre_report_no,
            sWorker=worker_name,
            nPrePoint=nPrePoint,
            nUsePoint=use_point,  # -nDeposit (양수)
            nRemainPoint=nPrePoint + use_point,
            sMemo=f"감액 환불 포인트 적립 (이전보고 #{pre_report_no})"
        )
        
        return JsonResponse({
            "success": True,
            "message": f"포인트 {abs(refund_amount):,}원이 적립되었습니다.",
            "point_no": new_point.no,
            "remain_point": new_point.nRemainPoint
        })

    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=500)


@require_http_methods(["GET"])
def get_companyreport_data(request, pk):
    """CompanyReport 데이터를 가져오는 API"""
    print(f"[API] get_companyreport_data called with pk={pk}")
    print(f"[API] Request method: {request.method}")
    # headers 출력 시 dict 변환 필요
    # print(f"[API] Request headers: {dict(request.headers)}")

    try:
        # 세션 체크는 일단 제거 (다른 API들과 동일하게 처리)
        # 필요시 나중에 전체 API에 일관성 있게 적용

        # CompanyReport 조회
        report = get_object_or_404(CompanyReport, pk=pk)
        print(f"[API] Found CompanyReport: no={report.no}, noCompany={report.noCompany}")

        # 회사 정보 조회
        company = None
        if report.noCompany:
            try:
                company = Company.objects.get(no=report.noCompany)
            except Company.DoesNotExist:
                pass

        # License 정보 조회 (noCompany와 연결된 사업자 정보들)
        licenses = []
        if report.noCompany:
            from license.models import License
            licenses = License.objects.filter(noCompany=report.noCompany).values(
                'sCompanyName', 'sAccount'
            )

        # 데이터 준비
        data = {
            'success': True,
            'data': {
                'noCompany': report.noCompany,
                'sCompanyName': company.sName1 if company else report.sCompanyName,
                'companyName': company.sName2 if company else '',  # 업체명 표시용
                'sName': report.sName,
                'sPhone': report.sPhone,
                'nType': report.nType,  # 보고구분 추가 (바로가기용)
                'noNext': report.noNext,  # 이후보고 추가 (중복 연결 방지용)
                'nConType': report.nConType,  # nConType으로 수정 (noConType 아님)
                'sPost': report.sPost,
                'noAssign': report.noAssign,
                'noOrder': report.noOrder,  # noOrder 추가
                'sArea': report.sArea,
                'nRefund': report.nRefund,
                'sTaxCompany': report.sTaxCompany,
                'sAccount': report.sAccount,
                'dateContract': report.dateContract.strftime('%Y-%m-%d') if report.dateContract else '',
                'dateSchedule': report.dateSchedule.strftime('%Y-%m-%d') if report.dateSchedule else '',
                # 금액 필드 추가 (증액 화면에서 이전 금액으로 사용)
                'nConMoney': report.nConMoney,
                'nFee': report.nFee,
                'nDeposit': report.nDeposit,  # 입금액 추가 (취소 시 환불액 계산에 필요)
                # nPreConMoney와 nPreFee도 반환 (증액 체인에서 필요)
                'nPreConMoney': report.nPreConMoney,
                'nPreFee': report.nPreFee,
                # License 정보 추가 (드롭다운 업데이트용)
                'licenses': list(licenses)
            }
        }

        print(f"[API] Returning success response with data keys: {data['data'].keys()}")
        return JsonResponse(data)

    except Exception as e:
        print(f"[API] Error occurred: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
