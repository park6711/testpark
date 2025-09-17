from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from .models import Staff


def staff_list(request):
    """스텝 목록 페이지"""
    staff_members = Staff.objects.all().order_by('no')
    context = {
        'staff_members': staff_members,
    }
    return render(request, 'staff/staff_list.html', context)


def staff_create(request):
    """스텝 추가"""
    if request.method == 'POST':
        try:
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
                nMaster=int(request.POST.get('nMaster', 0)),
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
        'action': 'create'
    })


def staff_update(request, pk):
    """스텝 수정"""
    staff = get_object_or_404(Staff, pk=pk)

    if request.method == 'POST':
        try:
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
            staff.nMaster = int(request.POST.get('nMaster', 0))
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

    return render(request, 'staff/staff_form.html', {
        'staff': staff,
        'title': '스텝 수정',
        'action': 'update'
    })


def staff_delete(request, pk):
    """스텝 삭제"""
    staff = get_object_or_404(Staff, pk=pk)
    staff_name = staff.sName
    staff.delete()
    messages.success(request, f'스텝 "{staff_name}"이 성공적으로 삭제되었습니다.')
    return redirect('staff:staff_list')