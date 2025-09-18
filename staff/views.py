from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from .models import Staff


def get_current_staff(request):
    """현재 로그인한 스텝 정보 반환"""
    staff_user = request.session.get('staff_user')
    if not staff_user:
        return None
    return Staff.objects.filter(no=staff_user['no']).first()


def check_staff_permission(request):
    """스텝 관리 권한 확인 (0: 권한없음, 1: 읽기권한, 2: 쓰기권한)"""
    current_staff = get_current_staff(request)
    if not current_staff:
        return 0
    return current_staff.nStaffAuthority


def check_master_edit_permission(request, target_staff):
    """마스터 권한 수정 가능 여부 확인"""
    current_staff = get_current_staff(request)
    if not current_staff:
        return False

    # 슈퍼마스터는 모든 마스터 권한 수정 가능
    if current_staff.nMaster == 2:  # 슈퍼마스터
        return True

    # 마스터는 일반 사용자의 마스터 권한만 수정 가능 (슈퍼마스터 불가)
    if current_staff.nMaster == 1:  # 마스터
        return target_staff.nMaster != 2  # 슈퍼마스터가 아닌 경우만

    # 일반 사용자는 마스터 권한 수정 불가
    return False


def staff_list(request):
    """스텝 목록 페이지"""
    # 로그인 확인
    if not request.session.get('staff_user'):
        # 로그아웃 상태에서는 타이틀과 로그인 버튼만 표시
        return render(request, 'staff/staff_list.html', {
            'not_logged_in': True,
            'staff_members': [],
            'staff_permission': 0,
            'current_staff': None,
            'can_write': False,
        })

    # 권한 확인
    staff_permission = check_staff_permission(request)
    current_staff = get_current_staff(request)

    # 권한없음인 경우 빈 리스트와 메시지 표시
    if staff_permission == 0:  # 권한없음
        context = {
            'staff_members': [],
            'staff_permission': staff_permission,
            'current_staff': current_staff,
            'can_write': False,
            'no_permission': True,  # 권한없음 상태 표시용
        }
        return render(request, 'staff/staff_list.html', context)

    staff_members = Staff.objects.all().order_by('no')
    context = {
        'staff_members': staff_members,
        'staff_permission': staff_permission,  # 템플릿에서 사용
        'current_staff': current_staff,
        'can_write': staff_permission == 2,  # 쓰기 권한 여부
        'no_permission': False,
    }
    return render(request, 'staff/staff_list.html', context)


def staff_create(request):
    """스텝 추가"""
    # 로그인 확인
    if not request.session.get('staff_user'):
        # 로그아웃 상태에서는 staff_form 템플릿을 깔끔하게 표시
        return render(request, 'staff/staff_form.html', {
            'not_logged_in': True,
            'title': '스텝 추가',
            'action': 'create',
            'current_staff': None
        })

    # 쓰기 권한 확인
    if check_staff_permission(request) != 2:
        messages.error(request, "스텝 추가 권한이 없습니다.")
        return redirect('staff:staff_list')

    current_staff = get_current_staff(request)

    if request.method == 'POST':
        try:
            # 마스터 권한 설정 검증
            requested_master = int(request.POST.get('nMaster', 0))

            # 마스터 권한 설정 제한 확인
            if requested_master > 0 and current_staff:  # 마스터 또는 슈퍼마스터 설정 시도
                if current_staff.nMaster < 1:  # 일반 사용자는 마스터 권한 설정 불가
                    messages.error(request, "마스터 권한을 설정할 권한이 없습니다.")
                    return redirect('staff:staff_list')
                elif requested_master == 2 and current_staff.nMaster != 2:  # 슈퍼마스터는 슈퍼마스터만 설정 가능
                    messages.error(request, "슈퍼마스터 권한은 슈퍼마스터만 설정할 수 있습니다.")
                    return redirect('staff:staff_list')

            staff = Staff.objects.create(
                sNaverID0='',  # 항상 빈값으로 생성
                bApproval=request.POST.get('bApproval') == 'on',
                sNaverID=request.POST.get('sNaverID', ''),
                sName=request.POST.get('sName', ''),
                sTeam=request.POST.get('sTeam', ''),
                sTitle=request.POST.get('sTitle', ''),
                sNick=request.POST.get('sNick', ''),
                sGoogleID=request.POST.get('sGoogleID', ''),
                sPhone1=request.POST.get('sPhone1', ''),
                sPhone2=request.POST.get('sPhone2', ''),
                nMaster=requested_master,
                nStaffAuthority=int(request.POST.get('nStaffAuthority', 0)),
                nCompanyAuthority=int(request.POST.get('nCompanyAuthority', 0)),
                nOrderAuthority=int(request.POST.get('nOrderAuthority', 0)),
                nContractAuthority=int(request.POST.get('nContractAuthority', 0)),
                nEvaluationAuthority=int(request.POST.get('nEvaluationAuthority', 0))
            )
            messages.success(request, f'스텝 "{staff.sName}"이 성공적으로 추가되었습니다.')
            return redirect('staff:staff_list')
        except Exception as e:
            messages.error(request, f'스텝 추가 중 오류가 발생했습니다: {str(e)}')
            return redirect('staff:staff_list')

    return render(request, 'staff/staff_form.html', {
        'title': '스텝 추가',
        'action': 'create',
        'current_staff': current_staff
    })


def staff_update(request, pk):
    """스텝 수정"""
    # 로그인 확인
    if not request.session.get('staff_user'):
        # 로그아웃 상태에서는 staff_form 템플릿을 깔끔하게 표시
        return render(request, 'staff/staff_form.html', {
            'not_logged_in': True,
            'title': '스텝 수정',
            'action': 'update',
            'current_staff': None
        })

    # 쓰기 권한 확인
    if check_staff_permission(request) != 2:
        messages.error(request, "스텝 수정 권한이 없습니다.")
        return redirect('staff:staff_list')

    current_staff = get_current_staff(request)
    staff = get_object_or_404(Staff, pk=pk)

    if request.method == 'POST':
        try:
            # 마스터 권한 수정 검증
            requested_master = int(request.POST.get('nMaster', 0))

            # 마스터 권한 수정 제한 확인
            if current_staff and not check_master_edit_permission(request, staff):
                if requested_master != staff.nMaster:  # 마스터 권한 변경 시도
                    messages.error(request, f"'{staff.sName}'의 마스터 권한을 수정할 권한이 없습니다.")
                    return redirect('staff:staff_list')

            # sNaverID0는 수정하지 않음 (읽기 전용)
            staff.bApproval = request.POST.get('bApproval') == 'on'
            staff.sNaverID = request.POST.get('sNaverID', '')
            staff.sName = request.POST.get('sName', '')
            staff.sTeam = request.POST.get('sTeam', '')
            staff.sTitle = request.POST.get('sTitle', '')
            staff.sNick = request.POST.get('sNick', '')
            staff.sGoogleID = request.POST.get('sGoogleID', '')
            staff.sPhone1 = request.POST.get('sPhone1', '')
            staff.sPhone2 = request.POST.get('sPhone2', '')
            staff.nMaster = requested_master
            staff.nStaffAuthority = int(request.POST.get('nStaffAuthority', 0))
            staff.nCompanyAuthority = int(request.POST.get('nCompanyAuthority', 0))
            staff.nOrderAuthority = int(request.POST.get('nOrderAuthority', 0))
            staff.nContractAuthority = int(request.POST.get('nContractAuthority', 0))
            staff.nEvaluationAuthority = int(request.POST.get('nEvaluationAuthority', 0))
            staff.save()

            messages.success(request, f'스텝 "{staff.sName}"이 성공적으로 수정되었습니다.')
            return redirect('staff:staff_list')
        except Exception as e:
            messages.error(request, f'스텝 수정 중 오류가 발생했습니다: {str(e)}')
            return redirect('staff:staff_list')

    return render(request, 'staff/staff_form.html', {
        'staff': staff,
        'title': '스텝 수정',
        'action': 'update',
        'current_staff': current_staff
    })


def staff_delete(request, pk):
    """스텝 삭제"""
    # 로그인 확인
    if not request.session.get('staff_user'):
        # 로그아웃 상태에서는 staff_list로 리다이렉트
        return redirect('staff:staff_list')

    # 쓰기 권한 확인
    if check_staff_permission(request) != 2:
        messages.error(request, "스텝 삭제 권한이 없습니다.")
        return redirect('staff:staff_list')

    staff = get_object_or_404(Staff, pk=pk)
    staff_name = staff.sName
    staff.delete()
    messages.success(request, f'스텝 "{staff_name}"이 성공적으로 삭제되었습니다.')
    return redirect('staff:staff_list')


def staff_view(request, pk):
    """스텝 상세 보기 (읽기 전용)"""
    # 로그인 확인
    if not request.session.get('staff_user'):
        # 로그아웃 상태에서는 staff_form 템플릿을 깔끔하게 표시
        return render(request, 'staff/staff_form.html', {
            'not_logged_in': True,
            'title': '스텝 정보 보기',
            'action': 'view',
            'current_staff': None,
            'read_only': True
        })

    # 최소 읽기 권한 확인
    staff_permission = check_staff_permission(request)
    if staff_permission == 0:  # 권한없음
        messages.error(request, "스텝 정보 조회 권한이 없습니다.")
        return redirect('demo:home')

    current_staff = get_current_staff(request)
    staff = get_object_or_404(Staff, pk=pk)

    return render(request, 'staff/staff_form.html', {
        'staff': staff,
        'title': f'스텝 정보 보기 - {staff.sName}',
        'action': 'view',
        'current_staff': current_staff,
        'read_only': True
    })