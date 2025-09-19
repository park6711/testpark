from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from .models import Member
from company.models import Company


def get_current_staff(request):
    """현재 로그인한 스텝 정보 반환"""
    from staff.models import Staff
    staff_user = request.session.get('staff_user')
    if not staff_user:
        return None
    return Staff.objects.filter(no=staff_user['no']).first()


def check_member_permission(request):
    """회원 관리 권한 확인 (0: 권한없음, 1: 읽기권한, 2: 쓰기권한)"""
    current_staff = get_current_staff(request)
    if not current_staff:
        return 0
    return current_staff.nCompanyAuthority  # 업체정보 권한으로 회원 관리


def member_list(request):
    """회원 목록 페이지"""
    # 로그인 확인
    if not request.session.get('staff_user'):
        return render(request, 'member/member_list.html', {
            'not_logged_in': True,
            'members': [],
            'member_permission': 0,
            'current_staff': None,
            'can_write': False,
        })

    # 권한 확인
    member_permission = check_member_permission(request)
    current_staff = get_current_staff(request)

    # 권한없음인 경우 빈 리스트와 메시지 표시
    if member_permission == 0:  # 권한없음
        context = {
            'members': [],
            'member_permission': member_permission,
            'current_staff': current_staff,
            'can_write': False,
            'no_permission': True,  # 권한없음 상태 표시용
        }
        return render(request, 'member/member_list.html', context)

    # 검색 기능
    search_query = request.GET.get('search', '')
    members = Member.objects.all()

    if search_query:
        members = members.filter(
            Q(sNaverID__icontains=search_query) |
            Q(sCompanyName__icontains=search_query) |
            Q(sName__icontains=search_query) |
            Q(sPhone__icontains=search_query)
        )

    # 정렬 기능
    sort_by = request.GET.get('sort', 'no')  # 기본값: no
    sort_order = request.GET.get('order', 'desc')  # 기본값: desc (내림차순)

    # 정렬 필드 검증
    valid_sort_fields = ['no', 'sNaverID', 'sCompanyName', 'sName', 'sPhone']
    if sort_by not in valid_sort_fields:
        sort_by = 'no'

    # 정렬 순서에 따라 쿼리 조정
    if sort_order == 'desc':
        members = members.order_by(f'-{sort_by}')
    else:
        members = members.order_by(sort_by)

    # 마스터 판별을 위해 Company 정보를 가져와서 각 Member에 마스터 여부 추가
    companies = Company.objects.all()
    companies_dict = {company.no: company for company in companies}

    # 각 Member에 마스터 여부 속성 추가
    for member in members:
        company = companies_dict.get(member.noCompany)
        member.is_company_master = (company and company.noMemberMaster == member.no)

    context = {
        'members': members,
        'member_permission': member_permission,
        'current_staff': current_staff,
        'can_write': member_permission == 2,
        'no_permission': False,
        'search_query': search_query,
        'sort_by': sort_by,
        'sort_order': sort_order,
    }
    return render(request, 'member/member_list.html', context)


def member_create(request):
    """회원 추가"""
    # 로그인 확인
    if not request.session.get('staff_user'):
        return render(request, 'member/member_form.html', {
            'not_logged_in': True,
            'title': '회원 추가',
            'action': 'create',
            'current_staff': None,
            'companies': []
        })

    # 쓰기 권한 확인
    if check_member_permission(request) != 2:
        messages.error(request, "회원 추가 권한이 없습니다.")
        return redirect('member:member_list')

    current_staff = get_current_staff(request)
    companies = Company.objects.all().order_by('sName1')

    # URL 파라미터에서 초기값 가져오기
    initial_no_company = request.GET.get('noCompany', '')
    initial_sname2 = request.GET.get('sName2', '')
    initial_scompany_name = request.GET.get('sCompanyName', '')

    if request.method == 'POST':
        try:
            member = Member.objects.create(
                sNaverID0='',  # 네이버 로그인 시에만 자동으로 설정됨
                bApproval=request.POST.get('bApproval') == 'on',
                sNaverID=request.POST.get('sNaverID', ''),
                sCompanyName=request.POST.get('sCompanyName', ''),
                sName2=request.POST.get('sName2', ''),
                noCompany=int(request.POST.get('noCompany', 0)),
                sName=request.POST.get('sName', ''),
                sPhone=request.POST.get('sPhone', ''),
                nCafeGrade=int(request.POST.get('nCafeGrade', 0)),
                nNick=request.POST.get('nNick', ''),
                nCompanyAuthority=int(request.POST.get('nCompanyAuthority', 2)),
                nOrderAuthority=int(request.POST.get('nOrderAuthority', 2)),
                nContractAuthority=int(request.POST.get('nContractAuthority', 2)),
                nEvaluationAuthority=int(request.POST.get('nEvaluationAuthority', 2))
            )
            messages.success(request, f'회원 "{member.sName}"이 성공적으로 추가되었습니다.')
            return redirect('member:member_list')
        except Exception as e:
            messages.error(request, f'회원 추가 중 오류가 발생했습니다: {str(e)}')
            return redirect('member:member_list')

    # 새로운 회원의 초기값 설정
    class DummyMember:
        is_company_master = False
        # 권한 초기값을 모두 쓰기권한(2)로 설정
        nCompanyAuthority = 2
        nOrderAuthority = 2
        nContractAuthority = 2
        nEvaluationAuthority = 2
        # 기타 필드 초기값
        bApproval = False
        nCafeGrade = 0

    return render(request, 'member/member_form.html', {
        'member': DummyMember() if not hasattr(request, 'member') else request.member,
        'title': '회원 추가',
        'action': 'create',
        'current_staff': current_staff,
        'companies': companies,
        'initial_no_company': initial_no_company,
        'initial_sname2': initial_sname2,
        'initial_scompany_name': initial_scompany_name
    })


def member_update(request, pk):
    """회원 수정"""
    # 로그인 확인
    if not request.session.get('staff_user'):
        return render(request, 'member/member_form.html', {
            'not_logged_in': True,
            'title': '회원 수정',
            'action': 'update',
            'current_staff': None,
            'companies': []
        })

    # 쓰기 권한 확인
    if check_member_permission(request) != 2:
        messages.error(request, "회원 수정 권한이 없습니다.")
        return redirect('member:member_list')

    current_staff = get_current_staff(request)
    member = get_object_or_404(Member, pk=pk)
    companies = Company.objects.all().order_by('sName1')

    if request.method == 'POST':
        try:
            # sNaverID0는 네이버 로그인 시에만 자동으로 설정되므로 수동 업데이트 불가
            member.bApproval = request.POST.get('bApproval') == 'on'
            member.sNaverID = request.POST.get('sNaverID', '')
            member.sCompanyName = request.POST.get('sCompanyName', '')
            member.sName2 = request.POST.get('sName2', '')
            member.noCompany = int(request.POST.get('noCompany', 0))
            member.sName = request.POST.get('sName', '')
            member.sPhone = request.POST.get('sPhone', '')
            member.nCafeGrade = int(request.POST.get('nCafeGrade', 0))
            member.nNick = request.POST.get('nNick', '')
            member.nCompanyAuthority = int(request.POST.get('nCompanyAuthority', 0))
            member.nOrderAuthority = int(request.POST.get('nOrderAuthority', 0))
            member.nContractAuthority = int(request.POST.get('nContractAuthority', 0))
            member.nEvaluationAuthority = int(request.POST.get('nEvaluationAuthority', 0))
            member.save()

            messages.success(request, f'회원 "{member.sName}"이 성공적으로 수정되었습니다.')
            return redirect('member:member_list')
        except Exception as e:
            messages.error(request, f'회원 수정 중 오류가 발생했습니다: {str(e)}')
            return redirect('member:member_list')

    # 초기값들 설정 (member_create와 동일한 로직)
    try:
        if member.noCompany and member.noCompany > 0:
            company = Company.objects.get(no=member.noCompany)
            initial_scompany_name = company.sCompanyName
        else:
            initial_scompany_name = member.sCompanyName
    except Company.DoesNotExist:
        initial_scompany_name = member.sCompanyName

    # member_update용 초기값들
    initial_no_company = member.noCompany if member.noCompany else 0
    initial_sname2 = member.sName2 if member.sName2 else ''

    # 마스터 여부 판별 (Company.noMemberMaster == Member.no)
    try:
        if member.noCompany:
            company = Company.objects.get(no=member.noCompany)
            member.is_company_master = (company.noMemberMaster == member.no)
        else:
            member.is_company_master = False
    except Company.DoesNotExist:
        member.is_company_master = False

    return render(request, 'member/member_form.html', {
        'member': member,
        'title': '회원 수정',
        'action': 'update',
        'current_staff': current_staff,
        'companies': companies,
        'initial_no_company': initial_no_company,
        'initial_sname2': initial_sname2,
        'initial_scompany_name': initial_scompany_name
    })


def member_delete(request, pk):
    """회원 삭제"""
    # 로그인 확인
    if not request.session.get('staff_user'):
        return redirect('member:member_list')

    # 쓰기 권한 확인
    if check_member_permission(request) != 2:
        messages.error(request, "회원 삭제 권한이 없습니다.")
        return redirect('member:member_list')

    member = get_object_or_404(Member, pk=pk)
    member_name = member.sName
    member.delete()
    messages.success(request, f'회원 "{member_name}"이 성공적으로 삭제되었습니다.')
    return redirect('member:member_list')


def member_view(request, pk):
    """회원 상세 보기 (읽기 전용)"""
    # 로그인 확인
    if not request.session.get('staff_user'):
        return render(request, 'member/member_form.html', {
            'not_logged_in': True,
            'title': '회원 정보 보기',
            'action': 'view',
            'current_staff': None,
            'read_only': True,
            'companies': []
        })

    # 최소 읽기 권한 확인
    member_permission = check_member_permission(request)
    if member_permission == 0:  # 권한없음
        messages.error(request, "회원 정보 조회 권한이 없습니다.")
        return redirect('member:member_list')

    current_staff = get_current_staff(request)
    member = get_object_or_404(Member, pk=pk)
    companies = Company.objects.all().order_by('sName1')

    # 마스터 여부 판별 (Company.noMemberMaster == Member.no)
    try:
        if member.noCompany:
            company = Company.objects.get(no=member.noCompany)
            member.is_company_master = (company.noMemberMaster == member.no)
        else:
            member.is_company_master = False
    except Company.DoesNotExist:
        member.is_company_master = False

    return render(request, 'member/member_form.html', {
        'member': member,
        'title': f'회원 정보 보기 - {member.sName}',
        'action': 'view',
        'current_staff': current_staff,
        'read_only': True,
        'companies': companies
    })
