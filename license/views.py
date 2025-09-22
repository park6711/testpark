from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from .models import License
from company.models import Company


def get_current_staff(request):
    """현재 로그인한 스텝 정보 반환"""
    from staff.models import Staff
    staff_user = request.session.get('staff_user')
    if not staff_user:
        return None
    return Staff.objects.filter(no=staff_user['no']).first()


def check_license_permission(request):
    """사업자 정보 관리 권한 확인 (0: 권한없음, 1: 읽기권한, 2: 쓰기권한)"""
    current_staff = get_current_staff(request)
    if not current_staff:
        return 0
    return current_staff.nCompanyAuthority  # 업체정보 권한으로 사업자 정보 관리


def license_list(request):
    """사업자 정보 목록 페이지"""
    # 로그인 확인
    if not request.session.get('staff_user'):
        return render(request, 'license/license_list.html', {
            'not_logged_in': True,
            'licenses': [],
            'license_permission': 0,
            'current_staff': None,
            'can_write': False,
        })

    # 권한 확인
    license_permission = check_license_permission(request)
    current_staff = get_current_staff(request)

    # 권한없음인 경우 빈 리스트와 메시지 표시
    if license_permission == 0:  # 권한없음
        context = {
            'licenses': [],
            'license_permission': license_permission,
            'current_staff': current_staff,
            'can_write': False,
            'no_permission': True,  # 권한없음 상태 표시용
        }
        return render(request, 'license/license_list.html', context)

    # 검색 기능
    search_query = request.GET.get('search', '')
    licenses = License.objects.all()

    if search_query:
        # Company의 sName2도 검색에 포함
        company_ids = Company.objects.filter(
            Q(sName2__icontains=search_query) | Q(sName1__icontains=search_query)
        ).values_list('no', flat=True)

        licenses = licenses.filter(
            Q(sCompanyName__icontains=search_query) |
            Q(sCeoName__icontains=search_query) |
            Q(sLicenseNo__icontains=search_query) |
            Q(sAccountMail__icontains=search_query) |
            Q(sAccount__icontains=search_query) |
            Q(noCompany__in=company_ids)
        )

    # 정렬 기능
    sort_by = request.GET.get('sort', 'no')  # 기본값: no
    sort_order = request.GET.get('order', 'desc')  # 기본값: desc (내림차순)

    # 정렬 필드 검증
    valid_sort_fields = ['no', 'noCompany', 'sCompanyName', 'sCeoName', 'sLicenseNo']
    if sort_by not in valid_sort_fields:
        sort_by = 'no'

    # 정렬 순서에 따라 쿼리 조정
    if sort_order == 'desc':
        licenses = licenses.order_by(f'-{sort_by}')
    else:
        licenses = licenses.order_by(sort_by)

    # 대표 사업자 판별을 위해 Company 정보를 가져와서 각 License에 대표 여부 추가
    companies = Company.objects.all()
    companies_dict = {company.no: company for company in companies}

    # 각 License에 대표 사업자 여부 속성 추가
    for license_obj in licenses:
        company = companies_dict.get(license_obj.noCompany)
        license_obj.is_company_represent = (company and company.noLicenseRepresent == license_obj.no)

    context = {
        'licenses': licenses,
        'license_permission': license_permission,
        'current_staff': current_staff,
        'can_write': license_permission == 2,
        'no_permission': False,
        'search_query': search_query,
        'sort_by': sort_by,
        'sort_order': sort_order,
    }
    return render(request, 'license/license_list.html', context)


def license_create(request):
    """사업자 정보 추가"""
    # 로그인 확인
    if not request.session.get('staff_user'):
        return render(request, 'license/license_form.html', {
            'not_logged_in': True,
            'title': '사업자 정보 추가',
            'action': 'create',
            'current_staff': None,
            'companies': []
        })

    # 쓰기 권한 확인
    if check_license_permission(request) != 2:
        messages.error(request, "사업자 정보 추가 권한이 없습니다.")
        return redirect('license:license_list')

    current_staff = get_current_staff(request)
    companies = Company.objects.all().order_by('sName1')

    # URL 파라미터에서 noCompany 값을 가져와서 초기값으로 설정
    initial_no_company = request.GET.get('noCompany', '')

    if request.method == 'POST':
        try:
            license_obj = License.objects.create(
                noCompany=int(request.POST.get('noCompany', 0)),
                sCompanyName=request.POST.get('sCompanyName', ''),
                sCeoName=request.POST.get('sCeoName', ''),
                sLicenseNo=request.POST.get('sLicenseNo', ''),
                sAccountMail=request.POST.get('sAccountMail', ''),
                sAccount=request.POST.get('sAccount', ''),
                fileLicense=request.FILES.get('fileLicense'),
                fileAccount=request.FILES.get('fileAccount')
            )
            messages.success(request, f'사업자 정보 "{license_obj.sCompanyName}"이 성공적으로 추가되었습니다.')
            return redirect('license:license_list')
        except Exception as e:
            messages.error(request, f'사업자 정보 추가 중 오류가 발생했습니다: {str(e)}')
            return redirect('license:license_list')

    # 새로운 라이센스이므로 대표 상태는 False로 초기화
    class DummyLicense:
        is_company_represent = False

    return render(request, 'license/license_form.html', {
        'license': DummyLicense() if not hasattr(request, 'license') else request.license,
        'title': '사업자 정보 추가',
        'action': 'create',
        'current_staff': current_staff,
        'companies': companies,
        'initial_no_company': initial_no_company
    })


def license_update(request, pk):
    """사업자 정보 수정"""
    # 로그인 확인
    if not request.session.get('staff_user'):
        return render(request, 'license/license_form.html', {
            'not_logged_in': True,
            'title': '사업자 정보 수정',
            'action': 'update',
            'current_staff': None,
            'companies': []
        })

    # 쓰기 권한 확인
    if check_license_permission(request) != 2:
        messages.error(request, "사업자 정보 수정 권한이 없습니다.")
        return redirect('license:license_list')

    current_staff = get_current_staff(request)
    license_obj = get_object_or_404(License, pk=pk)
    companies = Company.objects.all().order_by('sName1')

    if request.method == 'POST':
        try:
            license_obj.noCompany = int(request.POST.get('noCompany', 0))
            license_obj.sCompanyName = request.POST.get('sCompanyName', '')
            license_obj.sCeoName = request.POST.get('sCeoName', '')
            license_obj.sLicenseNo = request.POST.get('sLicenseNo', '')
            license_obj.sAccountMail = request.POST.get('sAccountMail', '')
            license_obj.sAccount = request.POST.get('sAccount', '')

            if request.FILES.get('fileLicense'):
                license_obj.fileLicense = request.FILES.get('fileLicense')
            if request.FILES.get('fileAccount'):
                license_obj.fileAccount = request.FILES.get('fileAccount')

            license_obj.save()

            messages.success(request, f'사업자 정보 "{license_obj.sCompanyName}"이 성공적으로 수정되었습니다.')
            return redirect('license:license_list')
        except Exception as e:
            messages.error(request, f'사업자 정보 수정 중 오류가 발생했습니다: {str(e)}')
            return redirect('license:license_list')

    # 대표 사업자 여부 판별 (Company.noLicenseRepresent == License.no)
    try:
        if license_obj.noCompany:
            company = Company.objects.get(no=license_obj.noCompany)
            license_obj.is_company_represent = (company.noLicenseRepresent == license_obj.no)
        else:
            license_obj.is_company_represent = False
    except Company.DoesNotExist:
        license_obj.is_company_represent = False

    return render(request, 'license/license_form.html', {
        'license': license_obj,
        'title': '사업자 정보 수정',
        'action': 'update',
        'current_staff': current_staff,
        'companies': companies
    })


def license_delete(request, pk):
    """사업자 정보 삭제"""
    # 로그인 확인
    if not request.session.get('staff_user'):
        return redirect('license:license_list')

    # 쓰기 권한 확인
    if check_license_permission(request) != 2:
        messages.error(request, "사업자 정보 삭제 권한이 없습니다.")
        return redirect('license:license_list')

    license_obj = get_object_or_404(License, pk=pk)
    company_name = license_obj.sCompanyName
    license_obj.delete()
    messages.success(request, f'사업자 정보 "{company_name}"이 성공적으로 삭제되었습니다.')
    return redirect('license:license_list')


def license_view(request, pk):
    """사업자 정보 상세 보기 (읽기 전용)"""
    # 로그인 확인
    if not request.session.get('staff_user'):
        return render(request, 'license/license_form.html', {
            'not_logged_in': True,
            'title': '사업자 정보 보기',
            'action': 'view',
            'current_staff': None,
            'read_only': True,
            'companies': []
        })

    # 최소 읽기 권한 확인
    license_permission = check_license_permission(request)
    if license_permission == 0:  # 권한없음
        messages.error(request, "사업자 정보 조회 권한이 없습니다.")
        return redirect('license:license_list')

    current_staff = get_current_staff(request)
    license_obj = get_object_or_404(License, pk=pk)
    companies = Company.objects.all().order_by('sName1')

    # 대표 사업자 여부 판별 (Company.noLicenseRepresent == License.no)
    try:
        if license_obj.noCompany:
            company = Company.objects.get(no=license_obj.noCompany)
            license_obj.is_company_represent = (company.noLicenseRepresent == license_obj.no)
        else:
            license_obj.is_company_represent = False
    except Company.DoesNotExist:
        license_obj.is_company_represent = False

    return render(request, 'license/license_form.html', {
        'license': license_obj,
        'title': f'사업자 정보 보기 - {license_obj.sCompanyName}',
        'action': 'view',
        'current_staff': current_staff,
        'read_only': True,
        'companies': companies
    })
