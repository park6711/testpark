from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from .models import Company, ContractFile
from license.models import License
from point.models import Point


def safe_int(value, default=0):
    """안전한 정수 변환 함수"""
    try:
        if value is None or value == '':
            return default
        return int(value)
    except (ValueError, TypeError):
        return default


def safe_float(value, default=0.0):
    """안전한 실수 변환 함수"""
    try:
        if value is None or value == '':
            return default
        return float(value)
    except (ValueError, TypeError):
        return default


def get_current_staff(request):
    """현재 로그인한 스텝 정보 반환"""
    from staff.models import Staff
    staff_user = request.session.get('staff_user')
    if not staff_user:
        return None
    return Staff.objects.filter(no=staff_user['no']).first()


def check_company_permission(request):
    """업체 관리 권한 확인 (0: 권한없음, 1: 읽기권한, 2: 쓰기권한)"""
    current_staff = get_current_staff(request)
    if not current_staff:
        return 0
    return current_staff.nCompanyAuthority


def company_list(request):
    """업체 목록 페이지"""
    # 로그인 확인
    if not request.session.get('staff_user'):
        return render(request, 'company/company_list.html', {
            'not_logged_in': True,
            'companies': [],
            'company_permission': 0,
            'current_staff': None,
            'can_write': False,
        })

    # 권한 확인
    company_permission = check_company_permission(request)
    current_staff = get_current_staff(request)

    # 권한없음인 경우 빈 리스트와 메시지 표시
    if company_permission == 0:  # 권한없음
        context = {
            'companies': [],
            'company_permission': company_permission,
            'current_staff': current_staff,
            'can_write': False,
            'no_permission': True,  # 권한없음 상태 표시용
        }
        return render(request, 'company/company_list.html', context)

    # 검색, 필터 및 정렬 기능
    search_query = request.GET.get('search', '')
    selected_types = request.GET.getlist('nType')
    selected_conditions = request.GET.getlist('nCondition')
    selected_unions = request.GET.getlist('bUnion')
    selected_mentors = request.GET.getlist('bMentor')
    sort_by = request.GET.get('sort', 'no')  # 기본 정렬: no
    sort_order = request.GET.get('order', 'desc')  # 기본 순서: 내림차순

    companies = Company.objects.all()

    # 검색 필터
    if search_query:
        companies = companies.filter(
            Q(sName1__icontains=search_query) |
            Q(sNaverID__icontains=search_query) |
            Q(sName2__icontains=search_query) |
            Q(sCompanyName__icontains=search_query) |
            Q(sAddress__icontains=search_query) |
            Q(sBuildLicense__icontains=search_query) |
            Q(sStrength__icontains=search_query) |
            Q(sCeoName__icontains=search_query) |
            Q(sCeoPhone__icontains=search_query) |
            Q(sCeoMail__icontains=search_query) |
            Q(sSaleName__icontains=search_query) |
            Q(sSalePhone__icontains=search_query) |
            Q(sSaleMail__icontains=search_query) |
            Q(sAccoutName__icontains=search_query) |
            Q(sAccoutPhone__icontains=search_query) |
            Q(sAccoutMail__icontains=search_query) |
            Q(sManager__icontains=search_query)
        )

    # 타입 필터
    if selected_types:
        type_filter = Q()
        for type_val in selected_types:
            type_filter |= Q(nType=safe_int(type_val))
        companies = companies.filter(type_filter)

    # 상태 필터
    if selected_conditions:
        condition_filter = Q()
        for condition_val in selected_conditions:
            condition_filter |= Q(nCondition=safe_int(condition_val))
        companies = companies.filter(condition_filter)

    # 연합회 필터
    if selected_unions:
        companies = companies.filter(bUnion=True)

    # 멘토 필터
    if selected_mentors:
        companies = companies.filter(bMentor=True)

    # 정렬 처리
    valid_sort_fields = ['no', 'sName2']
    if sort_by in valid_sort_fields:
        if sort_order == 'desc':
            order_field = f'-{sort_by}'
        else:
            order_field = sort_by
        companies = companies.order_by(order_field)
    else:
        companies = companies.order_by('-no')

    context = {
        'companies': companies,
        'company_permission': company_permission,
        'current_staff': current_staff,
        'can_write': company_permission == 2,
        'no_permission': False,
        'search_query': search_query,
        'selected_types': selected_types,
        'selected_conditions': selected_conditions,
        'selected_unions': selected_unions,
        'selected_mentors': selected_mentors,
        'sort_by': sort_by,
        'sort_order': sort_order,
    }
    return render(request, 'company/company_list.html', context)


def company_create(request):
    """업체 추가"""
    # 로그인 확인
    if not request.session.get('staff_user'):
        return render(request, 'company/company_form.html', {
            'not_logged_in': True,
            'title': '업체 추가',
            'action': 'create',
            'current_staff': None
        })

    # 쓰기 권한 확인
    if check_company_permission(request) != 2:
        messages.error(request, "업체 추가 권한이 없습니다.")
        return redirect('company:company_list')

    current_staff = get_current_staff(request)

    # 스태프 목록 조회
    from staff.models import Staff
    staff_list = Staff.objects.filter(sNick__isnull=False).exclude(sNick='').order_by('sNick')

    if request.method == 'POST':
        try:
            # 날짜 필드 처리
            date_join = request.POST.get('dateJoin')
            date_join = date_join if date_join else None

            date_fix_fee_start = request.POST.get('dateFixFeeStart')
            date_fix_fee_start = date_fix_fee_start if date_fix_fee_start else None

            date_withdraw = request.POST.get('dateWithdraw')
            date_withdraw = date_withdraw if date_withdraw else None

            company = Company.objects.create(
                sName1=request.POST.get('sName1', ''),
                sName2=request.POST.get('sName2', ''),
                sName3=request.POST.get('sName3', ''),
                sNaverID=request.POST.get('sNaverID', ''),
                nType=safe_int(request.POST.get('nType')),
                nCondition=safe_int(request.POST.get('nCondition')),
                sCompanyName=request.POST.get('sCompanyName', ''),
                sAddress=request.POST.get('sAddress', ''),
                nMember=safe_int(request.POST.get('nMember')),
                sBuildLicense=request.POST.get('sBuildLicense', ''),
                sStrength=request.POST.get('sStrength', ''),
                sCeoName=request.POST.get('sCeoName', ''),
                sCeoPhone=request.POST.get('sCeoPhone', ''),
                sCeoMail=request.POST.get('sCeoMail', ''),
                sSaleName=request.POST.get('sSaleName', ''),
                sSalePhone=request.POST.get('sSalePhone', ''),
                sSaleMail=request.POST.get('sSaleMail', ''),
                sAccoutName=request.POST.get('sAccoutName', ''),
                sAccoutPhone=request.POST.get('sAccoutPhone', ''),
                sAccoutMail=request.POST.get('sAccoutMail', ''),
                sEmergencyName=request.POST.get('sEmergencyName', ''),
                sEmergencyPhone=request.POST.get('sEmergencyPhone', ''),
                sEmergencyRelation=request.POST.get('sEmergencyRelation', ''),
                dateJoin=date_join,
                nJoinFee=safe_int(request.POST.get('nJoinFee')),
                nDeposit=safe_int(request.POST.get('nDeposit')),
                nFixFee=safe_int(request.POST.get('nFixFee')),
                dateFixFeeStart=date_fix_fee_start,
                fFeePercent=safe_float(request.POST.get('fFeePercent')),
                nOrderFee=safe_int(request.POST.get('nOrderFee')),
                nReportPeriod=safe_int(request.POST.get('nReportPeriod')),
                bAptAll=request.POST.get('bAptAll') == 'on',
                bAptPart=request.POST.get('bAptPart') == 'on',
                bHouseAll=request.POST.get('bHouseAll') == 'on',
                bHousePart=request.POST.get('bHousePart') == 'on',
                bCommerceAll=request.POST.get('bCommerceAll') == 'on',
                bCommercePart=request.POST.get('bCommercePart') == 'on',
                bBuild=request.POST.get('bBuild') == 'on',
                bExtra=request.POST.get('bExtra') == 'on',
                bUnion=request.POST.get('bUnion') == 'on',
                bMentor=request.POST.get('bMentor') == 'on',
                sMentee=request.POST.get('sMentee', ''),
                nRefund=safe_int(request.POST.get('nRefund')),
                sManager=request.POST.get('sManager', ''),
                dateWithdraw=date_withdraw,
                sMemo=request.POST.get('sMemo', ''),
                sPicture=request.POST.get('sPicture', ''),
                sGallery=request.POST.get('sGallery', ''),
                sEstimate=request.POST.get('sEstimate', ''),
                fileBuildLicense=request.FILES.get('fileBuildLicense'),
                fileCeo=request.FILES.get('fileCeo'),
                fileSale=request.FILES.get('fileSale'),
                fileLicense=request.FILES.get('fileLicense'),
                fileCampaignAgree=request.FILES.get('fileCampaignAgree')
            )

            # 다중 협약서 파일 업로드 처리
            contract_files = request.FILES.getlist('contractFiles')
            print(f"DEBUG: Found {len(contract_files)} contract files to upload")
            for i, contract_file in enumerate(contract_files):
                print(f"DEBUG: Processing file {i}: {contract_file.name}")
                ContractFile.objects.create(
                    company=company,
                    file=contract_file
                )

            # Company 생성 시 자동으로 License 레코드 생성
            print(f"DEBUG: Starting License creation for company {company.no}")
            print(f"DEBUG: Company data - sCompanyName: '{company.sCompanyName}', sCeoName: '{company.sCeoName}', sCeoMail: '{company.sCeoMail}'")

            try:
                license = License.objects.create(
                    noCompany=company.no,
                    sCompanyName=company.sCompanyName,
                    sCeoName=company.sCeoName,
                    sAccountMail=company.sAccoutMail or '',  # 회계담당자 이메일을 계좌 메일로 사용 (빈 값 처리)
                    sLicenseNo='',  # 사업자등록번호는 빈 값으로 시작
                    sAccount='',    # 계좌번호는 빈 값으로 시작
                    fileLicense=company.fileLicense,  # Company의 사업자등록증 파일
                    fileAccount=None,  # 통장사본은 나중에 별도 업로드
                )
                print(f"DEBUG: SUCCESS - License record created for company {company.no}: License ID {license.no}")

                # Company의 noLicenseRepresent 필드를 새로 생성된 License.no로 설정
                company.noLicenseRepresent = license.no
                company.save()
                print(f"DEBUG: Company {company.no} noLicenseRepresent set to {license.no}")

                # Company 생성 시 자동으로 Member 레코드 생성 (마스터 회원)
                try:
                    from member.models import Member
                    member = Member.objects.create(
                        noCompany=company.no,
                        sCompanyName=company.sCompanyName,
                        sName2=company.sName2 or '',
                        sName=company.sCeoName,
                        sPhone=company.sCeoPhone or '',
                        sNaverID=company.sCeoMail or '',  # CEO 이메일을 네이버 ID로 사용
                        bApproval=True,  # 마스터 회원은 자동 승인
                        nCafeGrade=0,  # 일반 등급
                        nCompanyAuthority=2,  # 쓰기권한
                        nOrderAuthority=2,  # 쓰기권한
                        nContractAuthority=2,  # 쓰기권한
                        nEvaluationAuthority=2,  # 쓰기권한
                    )
                    print(f"DEBUG: SUCCESS - Member record created for company {company.no}: Member ID {member.no}")

                    # Company의 noMemberMaster 필드를 새로 생성된 Member.no로 설정
                    company.noMemberMaster = member.no
                    company.save()
                    print(f"DEBUG: Company {company.no} noMemberMaster set to {member.no}")

                    messages.success(request, f'업체 "{company.sCompanyName}"이 성공적으로 추가되었습니다. 사업자 정보(ID: {license.no})와 마스터 회원(ID: {member.no})도 자동으로 생성되었습니다.')
                except Exception as member_error:
                    print(f"DEBUG: ERROR - Failed to create Member record: {str(member_error)}")
                    print(f"DEBUG: Member Exception type: {type(member_error).__name__}")
                    import traceback
                    traceback.print_exc()
                    # Member 생성 실패해도 License와 Company는 성공으로 처리
                    messages.success(request, f'업체 "{company.sCompanyName}"이 성공적으로 추가되었습니다. 사업자 정보(ID: {license.no})도 자동으로 생성되었습니다. (마스터 회원 생성 실패: {str(member_error)})')
            except Exception as e:
                print(f"DEBUG: ERROR - Failed to create License record: {str(e)}")
                print(f"DEBUG: Exception type: {type(e).__name__}")
                import traceback
                traceback.print_exc()
                # License 생성 실패해도 Company 생성은 성공으로 처리
                messages.success(request, f'업체 "{company.sCompanyName}"이 성공적으로 추가되었습니다. (사업자 정보 생성 실패: {str(e)})')

            return redirect('company:company_list')
        except Exception as e:
            messages.error(request, f'업체 추가 중 오류가 발생했습니다: {str(e)}')
            return redirect('company:company_list')

    return render(request, 'company/company_form.html', {
        'title': '업체 추가',
        'action': 'create',
        'current_staff': current_staff,
        'staff_list': staff_list
    })


def company_update(request, pk):
    """업체 수정"""
    # 로그인 확인
    if not request.session.get('staff_user'):
        return render(request, 'company/company_form.html', {
            'not_logged_in': True,
            'title': '업체 수정',
            'action': 'update',
            'current_staff': None
        })

    # 쓰기 권한 확인
    if check_company_permission(request) != 2:
        messages.error(request, "업체 수정 권한이 없습니다.")
        return redirect('company:company_list')

    current_staff = get_current_staff(request)
    company = get_object_or_404(Company, pk=pk)

    # 스태프 목록 조회
    from staff.models import Staff
    staff_list = Staff.objects.filter(sNick__isnull=False).exclude(sNick='').order_by('sNick')

    if request.method == 'POST':
        try:
            # 날짜 필드 처리
            date_join = request.POST.get('dateJoin')
            date_join = date_join if date_join else None

            date_fix_fee_start = request.POST.get('dateFixFeeStart')
            date_fix_fee_start = date_fix_fee_start if date_fix_fee_start else None

            date_withdraw = request.POST.get('dateWithdraw')
            date_withdraw = date_withdraw if date_withdraw else None

            company.sName1 = request.POST.get('sName1', '')
            company.sName2 = request.POST.get('sName2', '')
            company.sName3 = request.POST.get('sName3', '')
            company.sNaverID = request.POST.get('sNaverID', '')
            company.nType = safe_int(request.POST.get('nType'))
            company.nCondition = safe_int(request.POST.get('nCondition'))
            company.sCompanyName = request.POST.get('sCompanyName', '')
            company.sAddress = request.POST.get('sAddress', '')
            company.nMember = safe_int(request.POST.get('nMember'))
            company.sBuildLicense = request.POST.get('sBuildLicense', '')
            company.sStrength = request.POST.get('sStrength', '')
            company.sCeoName = request.POST.get('sCeoName', '')
            company.sCeoPhone = request.POST.get('sCeoPhone', '')
            company.sCeoMail = request.POST.get('sCeoMail', '')
            company.sSaleName = request.POST.get('sSaleName', '')
            company.sSalePhone = request.POST.get('sSalePhone', '')
            company.sSaleMail = request.POST.get('sSaleMail', '')
            company.sAccoutName = request.POST.get('sAccoutName', '')
            company.sAccoutPhone = request.POST.get('sAccoutPhone', '')
            company.sAccoutMail = request.POST.get('sAccoutMail', '')
            company.sEmergencyName = request.POST.get('sEmergencyName', '')
            company.sEmergencyPhone = request.POST.get('sEmergencyPhone', '')
            company.sEmergencyRelation = request.POST.get('sEmergencyRelation', '')
            company.dateJoin = date_join
            company.nJoinFee = safe_int(request.POST.get('nJoinFee'))
            company.nDeposit = safe_int(request.POST.get('nDeposit'))
            company.nFixFee = safe_int(request.POST.get('nFixFee'))
            company.dateFixFeeStart = date_fix_fee_start
            company.fFeePercent = safe_float(request.POST.get('fFeePercent'))
            company.nOrderFee = safe_int(request.POST.get('nOrderFee'))
            company.nReportPeriod = safe_int(request.POST.get('nReportPeriod'))
            company.bAptAll = request.POST.get('bAptAll') == 'on'
            company.bAptPart = request.POST.get('bAptPart') == 'on'
            company.bHouseAll = request.POST.get('bHouseAll') == 'on'
            company.bHousePart = request.POST.get('bHousePart') == 'on'
            company.bCommerceAll = request.POST.get('bCommerceAll') == 'on'
            company.bCommercePart = request.POST.get('bCommercePart') == 'on'
            company.bBuild = request.POST.get('bBuild') == 'on'
            company.bExtra = request.POST.get('bExtra') == 'on'
            company.bUnion = request.POST.get('bUnion') == 'on'
            company.bMentor = request.POST.get('bMentor') == 'on'
            company.sMentee = request.POST.get('sMentee', '')
            company.nRefund = safe_int(request.POST.get('nRefund'))
            company.sManager = request.POST.get('sManager', '')
            company.dateWithdraw = date_withdraw
            company.sMemo = request.POST.get('sMemo', '')
            company.sPicture = request.POST.get('sPicture', '')
            company.sGallery = request.POST.get('sGallery', '')
            company.sEstimate = request.POST.get('sEstimate', '')

            # 파일 삭제 처리
            if request.POST.get('delete_fileBuildLicense'):
                if company.fileBuildLicense:
                    company.fileBuildLicense.delete()
                company.fileBuildLicense = None
            if request.POST.get('delete_fileCeo'):
                if company.fileCeo:
                    company.fileCeo.delete()
                company.fileCeo = None
            if request.POST.get('delete_fileSale'):
                if company.fileSale:
                    company.fileSale.delete()
                company.fileSale = None
            if request.POST.get('delete_fileLicense'):
                if company.fileLicense:
                    company.fileLicense.delete()
                company.fileLicense = None
            if request.POST.get('delete_fileCampaignAgree'):
                if company.fileCampaignAgree:
                    company.fileCampaignAgree.delete()
                company.fileCampaignAgree = None

            # 협약서 파일 개별 삭제 처리
            delete_contract_file_ids = request.POST.getlist('delete_contract_file')
            if delete_contract_file_ids:
                contract_files_to_delete = ContractFile.objects.filter(
                    id__in=delete_contract_file_ids,
                    company=company
                )
                for contract_file in contract_files_to_delete:
                    contract_file.file.delete()
                    contract_file.delete()

            # 파일 업로드 처리 (삭제되지 않은 경우에만)
            if request.FILES.get('fileBuildLicense') and not request.POST.get('delete_fileBuildLicense'):
                company.fileBuildLicense = request.FILES.get('fileBuildLicense')
            if request.FILES.get('fileCeo') and not request.POST.get('delete_fileCeo'):
                company.fileCeo = request.FILES.get('fileCeo')
            if request.FILES.get('fileSale') and not request.POST.get('delete_fileSale'):
                company.fileSale = request.FILES.get('fileSale')
            if request.FILES.get('fileLicense') and not request.POST.get('delete_fileLicense'):
                company.fileLicense = request.FILES.get('fileLicense')
            if request.FILES.get('fileCampaignAgree') and not request.POST.get('delete_fileCampaignAgree'):
                company.fileCampaignAgree = request.FILES.get('fileCampaignAgree')

            # 새 협약서 파일 업로드 처리
            contract_files = request.FILES.getlist('contractFiles')
            print(f"DEBUG UPDATE: Found {len(contract_files)} contract files to upload")
            for i, contract_file in enumerate(contract_files):
                print(f"DEBUG UPDATE: Processing file {i}: {contract_file.name}")
                ContractFile.objects.create(
                    company=company,
                    file=contract_file
                )

            company.save()

            messages.success(request, f'업체 "{company.sCompanyName}"이 성공적으로 수정되었습니다.')
            return redirect('company:company_list')
        except Exception as e:
            messages.error(request, f'업체 수정 중 오류가 발생했습니다: {str(e)}')
            return redirect('company:company_list')

    return render(request, 'company/company_form.html', {
        'company': company,
        'title': '업체 수정',
        'action': 'update',
        'current_staff': current_staff,
        'staff_list': staff_list
    })


def company_delete(request, pk):
    """업체 삭제"""
    # 로그인 확인
    if not request.session.get('staff_user'):
        return redirect('company:company_list')

    # 쓰기 권한 확인
    if check_company_permission(request) != 2:
        messages.error(request, "업체 삭제 권한이 없습니다.")
        return redirect('company:company_list')

    company = get_object_or_404(Company, pk=pk)
    company_name = company.sCompanyName

    # 포인트 잔액 확인
    last_point = Point.objects.filter(noCompany=company).order_by('-time', '-no').first()
    if last_point and last_point.nRemainPoint != 0:
        messages.warning(
            request,
            f'업체 "{company_name}"의 포인트 잔액이 {last_point.nRemainPoint:,}원 있습니다. '
            f'삭제하면 포인트 내역은 보존되지만 업체 정보는 "삭제된 업체"로 표시됩니다.'
        )

    # 연관된 파일들 삭제
    file_fields = [
        company.fileBuildLicense,
        company.fileCeo,
        company.fileSale,
        company.fileLicense,
        company.fileCampaignAgree
    ]

    for file_field in file_fields:
        if file_field:
            file_field.delete()

    # 협약서 파일들 삭제
    contract_files = company.contract_files.all()
    for contract_file in contract_files:
        contract_file.file.delete()
        contract_file.delete()

    # Company 삭제 (모델의 delete 메서드에서 관련 레코드 정리)
    company.delete()
    messages.success(request, f'업체 "{company_name}"이 성공적으로 삭제되었습니다.')
    return redirect('company:company_list')


def company_view(request, pk):
    """업체 상세 보기 (읽기 전용)"""
    # 로그인 확인
    if not request.session.get('staff_user'):
        return render(request, 'company/company_form.html', {
            'not_logged_in': True,
            'title': '업체 정보 보기',
            'action': 'view',
            'current_staff': None,
            'read_only': True
        })

    # 최소 읽기 권한 확인
    company_permission = check_company_permission(request)
    if company_permission == 0:  # 권한없음
        messages.error(request, "업체 정보 조회 권한이 없습니다.")
        return redirect('company:company_list')

    current_staff = get_current_staff(request)
    company = get_object_or_404(Company, pk=pk)

    # 스태프 목록 조회 (읽기 전용 모드에서는 필요없지만 일관성을 위해)
    from staff.models import Staff
    staff_list = Staff.objects.filter(sNick__isnull=False).exclude(sNick='').order_by('sNick')

    return render(request, 'company/company_form.html', {
        'company': company,
        'title': f'업체 정보 보기 - {company.sCompanyName}',
        'action': 'view',
        'current_staff': current_staff,
        'read_only': True,
        'staff_list': staff_list
    })


from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def sync_companies_from_sheets(request):
    """Google Sheets에서 Company 데이터를 동기화하는 API 엔드포인트"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'POST 메서드만 허용됩니다'}, status=405)

    try:
        from .google_sheets_sync import CompanySheetsSync
        import logging

        logger = logging.getLogger(__name__)
        logger.info("Company 동기화 API 호출됨")

        sync_service = CompanySheetsSync()
        result = sync_service.sync_data(update_existing=False)

        return JsonResponse({
            'success': True,
            'message': '동기화 완료',
            'result': result
        })

    except Exception as e:
        logger.error(f"Company 동기화 실패: {str(e)}", exc_info=True)
        return JsonResponse({
            'success': False,
            'message': f'동기화 실패: {str(e)}'
        }, status=500)
