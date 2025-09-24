from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.conf import settings
from .models import GlobalVar
from staff.models import Staff
import importlib

def globalvar_list(request):
    """전역변수 목록 보기 및 수정"""

    # 현재 스텝 정보 가져오기
    current_staff = None
    if request.session.get('staff_user'):
        try:
            current_staff = Staff.objects.get(no=request.session['staff_user']['no'])
        except Staff.DoesNotExist:
            pass

    # 현재 settings.py에 정의된 전역변수들
    evaluation_vars = [
        ('G_N_EVALUATION_NO', '현재 업체평가 회차', 'int'),
        ('G_F_EVALUATION_A1', '계약률 점수 계수', 'float'),
        ('G_F_EVALUATION_A1_MAX', '계약률 점수 최대값', 'float'),
        ('G_F_EVALUATION_A2', '수수료 점수 계수', 'float'),
        ('G_F_EVALUATION_A3', '고정비 점수 계수', 'float'),
        ('G_F_EVALUATION_A4', '자재구매액 점수 계수', 'float'),
        ('G_F_EVALUATION_B', '후기 점수 계수', 'float'),
        ('G_F_EVALUATION_B_MAX', '후기 점수 최대값', 'float'),
        ('G_F_EVALUATION_C', '고객불만점수 계수', 'float'),
        ('G_F_EVALUATION_D', '고객만족도 점수 계수', 'float'),
        ('G_F_EVALUATION_E', '카페지식활동 점수 계수', 'float'),
        ('G_F_EVALUATION_E_MAX', '카페지식활동 점수 최대값', 'float'),
        ('G_F_EVALUATION_F', '지식공유활동 점수 계수', 'float'),
        ('G_F_EVALUATION_F_MAX', '지식공유활동 점수 최대값', 'float'),
        ('G_F_EVALUATION_G', '세미나참석 점수 계수', 'float'),
        ('G_F_EVALUATION_G_MAX', '세미나참석 점수 최대값', 'float'),
        ('G_F_EVALUATION_H', '멘토 점수 계수', 'float'),
        ('G_F_EVALUATION_I', '이행보증참여 점수 계수', 'float'),
        ('G_F_EVALUATION_J', '안전캠페인 점수 계수', 'float'),
        ('G_F_EVALUATION_J_MAX', '안전캠페인 점수 최대값', 'float'),
        ('G_N_ASSIGN_LACK', '고정비업체 할당부족 개수 계수(최소일수)', 'int'),
        ('G_F_ASSIGN_LACK', '고정비업체 할당부족 개수 계수', 'float'),
    ]

    # DB에서 모든 전역변수 조회
    global_vars_from_db = GlobalVar.objects.all()
    db_vars_dict = {var.key: var for var in global_vars_from_db}

    # settings.py의 현재 값과 DB 값 병합
    global_vars = []
    for key, desc, var_type in evaluation_vars:
        # settings.py에서 현재 값 가져오기
        current_value = getattr(settings, key, None)

        # DB에 저장된 값이 있으면 DB 값 사용
        if key in db_vars_dict:
            db_var = db_vars_dict[key]
            display_value = db_var.value
            db_id = db_var.id
        else:
            # DB에 없으면 settings.py 값 사용
            display_value = str(current_value) if current_value is not None else ''
            db_id = None

        global_vars.append({
            'id': db_id,
            'key': key,
            'value': display_value,
            'current_value': current_value,  # settings.py의 현재 값
            'description': desc,
            'var_type': var_type,
        })

    context = {
        'global_vars': global_vars,
        'current_staff': current_staff,
    }

    return render(request, 'globalvars/globalvar_list.html', context)

@require_http_methods(["POST"])
def globalvar_update(request):
    """전역변수 수정"""

    for key in request.POST:
        if key.startswith('value_'):
            var_key = key.replace('value_', '')
            new_value = request.POST[key]
            var_type = request.POST.get(f'type_{var_key}', 'str')
            description = request.POST.get(f'desc_{var_key}', '')

            # DB에 저장 또는 업데이트
            global_var, created = GlobalVar.objects.update_or_create(
                key=var_key,
                defaults={
                    'value': new_value,
                    'var_type': var_type,
                    'description': description,
                    'category': 'EVALUATION',
                }
            )

            # settings.py 파일 업데이트 (선택사항)
            # 실제로는 settings.py 파일을 직접 수정하기보다는
            # 애플리케이션 시작 시 DB에서 값을 로드하는 방식이 더 안전합니다.

    messages.success(request, '전역변수가 성공적으로 수정되었습니다.')
    return redirect('globalvars:globalvar_list')
