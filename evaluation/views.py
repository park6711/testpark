from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.db.models import Q
import json
from .models import EvaluationNo, Complain
from company.models import Company
from globalvars.models import GlobalVar
from staff.models import Staff


def evaluation_list(request):
    """평가 목록 페이지"""
    return HttpResponse("Evaluation List - 평가 관리 페이지입니다.")


def get_current_evaluation_no():
    """현재 업체평가 회차 가져오기"""
    try:
        global_var = GlobalVar.objects.get(key='G_N_EVALUATION_NO')
        return global_var.get_typed_value()
    except GlobalVar.DoesNotExist:
        # 기본값 설정 - 가장 최근 평가회차
        latest = EvaluationNo.objects.order_by('-no').first()
        if latest:
            return latest.no
        return 1


def evaluation_no_list(request):
    """업체평가 회차 리스트"""
    current_no = get_current_evaluation_no()

    # 현재 로그인한 스태프 정보 가져오기
    current_staff = None
    if 'staff_user' in request.session:
        try:
            current_staff = Staff.objects.get(no=request.session['staff_user']['no'])
        except Staff.DoesNotExist:
            pass

    # 현재 회차 이하만 조회
    evaluations = EvaluationNo.objects.filter(
        no__lte=current_no
    ).order_by('-no')

    context = {
        'current_no': current_no,
        'evaluations': evaluations,
        'current_staff': current_staff,
    }

    return render(request, 'evaluation/evaluation_no_list.html', context)


def evaluation_no_detail(request, pk):
    """업체평가 회차 상세보기"""
    evaluation = get_object_or_404(EvaluationNo, pk=pk)
    current_no = get_current_evaluation_no()

    # 현재 로그인한 스태프 정보 가져오기
    current_staff = None
    if 'staff_user' in request.session:
        try:
            current_staff = Staff.objects.get(no=request.session['staff_user']['no'])
        except Staff.DoesNotExist:
            pass

    context = {
        'current_no': current_no,
        'evaluation': evaluation,
        'mode': 'view',
        'current_staff': current_staff,
    }

    return render(request, 'evaluation/evaluation_no_detail.html', context)


def evaluation_no_edit(request, pk):
    """업체평가 회차 수정"""
    evaluation = get_object_or_404(EvaluationNo, pk=pk)
    current_no = get_current_evaluation_no()

    # 현재 로그인한 스태프 정보 가져오기
    current_staff = None
    if 'staff_user' in request.session:
        try:
            current_staff = Staff.objects.get(no=request.session['staff_user']['no'])
        except Staff.DoesNotExist:
            pass

    if request.method == 'POST':
        try:
            # 수정 가능한 필드만 업데이트
            evaluation.dateNotice = request.POST.get('dateNotice') or None

            # 빈 문자열 처리
            average_all = request.POST.get('fAverageAll', '').strip()
            if average_all:
                evaluation.fAverageAll = float(average_all)
            else:
                evaluation.fAverageAll = 0.0

            average_excel = request.POST.get('fAverageExcel', '').strip()
            if average_excel:
                evaluation.fAverageExcel = float(average_excel)
            else:
                evaluation.fAverageExcel = 0.0

            # 날짜+시간 필드 처리
            from datetime import datetime

            datetime_excel = request.POST.get('timeExcel')
            if datetime_excel:
                try:
                    # HTML datetime-local 형식 파싱
                    evaluation.timeExcel = datetime.strptime(datetime_excel, '%Y-%m-%dT%H:%M')
                except ValueError:
                    evaluation.timeExcel = None
            else:
                evaluation.timeExcel = None

            datetime_weak = request.POST.get('timeWeak')
            if datetime_weak:
                try:
                    # HTML datetime-local 형식 파싱
                    evaluation.timeWeak = datetime.strptime(datetime_weak, '%Y-%m-%dT%H:%M')
                except ValueError:
                    evaluation.timeWeak = None
            else:
                evaluation.timeWeak = None

            evaluation.save()

            messages.success(request, f'평가회차 {pk}번이 수정되었습니다.')
            return redirect('evaluation:evaluation_no_detail', pk=pk)

        except Exception as e:
            messages.error(request, f'수정 중 오류가 발생했습니다: {str(e)}')

    context = {
        'current_no': current_no,
        'evaluation': evaluation,
        'mode': 'edit',
        'current_staff': current_staff,
    }

    return render(request, 'evaluation/evaluation_no_detail.html', context)


@csrf_exempt
@require_http_methods(["POST"])
def evaluation_no_update_field(request):
    """개별 필드 업데이트 (AJAX)"""
    try:
        data = json.loads(request.body)
        pk = data.get('pk')
        field = data.get('field')
        value = data.get('value')

        evaluation = get_object_or_404(EvaluationNo, pk=pk)

        # 수정 가능한 필드만 허용
        editable_fields = ['dateNotice', 'fAverageAll', 'fAverageExcel', 'timeExcel', 'timeWeak']

        if field not in editable_fields:
            return JsonResponse({'success': False, 'error': '수정할 수 없는 필드입니다.'})

        # 필드 업데이트
        if field in ['fAverageAll', 'fAverageExcel']:
            value = float(value) if value else 0.0
        elif field in ['dateNotice', 'timeExcel', 'timeWeak']:
            value = value if value else None

        setattr(evaluation, field, value)
        evaluation.save()

        return JsonResponse({'success': True})

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


def complain_list(request):
    """고객불만 이력 리스트"""
    # 현재 로그인한 스태프 정보 가져오기
    current_staff = None
    if 'staff_user' in request.session:
        try:
            current_staff = Staff.objects.get(no=request.session['staff_user']['no'])
        except Staff.DoesNotExist:
            pass

    # 기본 쿼리셋
    queryset = Complain.objects.select_related().all()

    # 활동상태 필터
    conditions = request.GET.getlist('condition[]')
    if conditions:
        # Company 테이블과 조인하여 nCondition으로 필터링
        company_ids = Company.objects.filter(nCondition__in=conditions).values_list('no', flat=True)
        queryset = queryset.filter(noCompany__in=company_ids)

    # 검색 필터
    search = request.GET.get('search', '').strip()
    if search:
        # Company의 sName1, sName2, sName3 검색 추가
        company_ids = Company.objects.filter(
            Q(sName1__icontains=search) |
            Q(sName2__icontains=search) |
            Q(sName3__icontains=search)
        ).values_list('no', flat=True)

        queryset = queryset.filter(
            Q(sCompanyName__icontains=search) |
            Q(noCompany__in=company_ids) |
            Q(sPass__icontains=search) |
            Q(sComplain__icontains=search) |
            Q(sCheck__icontains=search) |
            Q(sWorker__icontains=search)
        )

    # 정렬
    queryset = queryset.order_by('-no')

    # Company 정보 추가
    complains = []
    for complain in queryset:
        try:
            company = Company.objects.get(no=complain.noCompany)
            company_name = company.sName2 or company.sName1 or f"업체{complain.noCompany}"
            company_sname2 = company.sName2 or "-"  # sName2를 별도로 저장
            company_condition = company.nCondition
        except Company.DoesNotExist:
            company_name = complain.sCompanyName or f"업체{complain.noCompany}"
            company_sname2 = "-"  # Company가 없으면 "-" 표시
            company_condition = 0

        complains.append({
            'complain': complain,
            'company_name': company_name,
            'company_sname2': company_sname2,  # sName2 추가
            'company_condition': company_condition
        })

    context = {
        'complains': complains,
        'current_staff': current_staff,
        'search': search,
        'selected_conditions': conditions,
    }

    return render(request, 'evaluation/complain_list.html', context)


# complain_detail 함수 삭제 - 수정 기능 제거


@csrf_exempt
@require_http_methods(["POST"])
def complain_update_score(request):
    """불만점수 개별 업데이트 (AJAX)"""
    try:
        data = json.loads(request.body)
        pk = data.get('pk')
        score = data.get('score')

        complain = get_object_or_404(Complain, pk=pk)
        complain.fComplain = float(score)
        complain.save()

        return JsonResponse({'success': True})

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@csrf_exempt
@require_http_methods(["POST"])
def complain_update_check(request):
    """계약확인 개별 업데이트 (AJAX)"""
    try:
        data = json.loads(request.body)
        pk = data.get('pk')
        check = data.get('check', '')

        complain = get_object_or_404(Complain, pk=pk)
        complain.sCheck = check
        complain.save()

        return JsonResponse({'success': True})

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@csrf_exempt
@require_http_methods(["POST"])
def complain_delete(request, pk):
    """고객불만 삭제"""
    try:
        complain = get_object_or_404(Complain, pk=pk)
        complain.delete()

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True})
        else:
            messages.success(request, '고객불만 데이터가 삭제되었습니다.')
            return redirect('evaluation:complain_list')

    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': str(e)})
        else:
            messages.error(request, f'삭제 중 오류가 발생했습니다: {str(e)}')
            return redirect('evaluation:complain_list')
