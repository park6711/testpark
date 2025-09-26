from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.db.models import Q
import json
from .models import EvaluationNo, Complain, Satisfy
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

    # Company 정보 추가 및 날짜 포맷팅
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

        # sTimeStamp를 YYMMDD 형식으로 변환 및 툴팁 포맷
        if complain.sTimeStamp and not complain.timeStamp:
            s = complain.sTimeStamp
            formatted_date = ""
            formatted_tooltip = ""

            # 영어 형식: "Fri Sep 26 2025 23:13:11 GMT+0900"
            if "GMT" in s:
                month_map = {'Jan':'01','Feb':'02','Mar':'03','Apr':'04','May':'05','Jun':'06',
                           'Jul':'07','Aug':'08','Sep':'09','Oct':'10','Nov':'11','Dec':'12'}
                parts = s.split()
                if len(parts) >= 5:
                    year = parts[3][2:4] if len(parts[3]) == 4 else parts[3]
                    month = month_map.get(parts[1], '00')
                    day = parts[2].zfill(2)
                    formatted_date = f"{year}{month}{day}"

                    # 시간 파싱 및 오전/오후 변환
                    time_parts = parts[4].split(':')
                    if len(time_parts) >= 3:
                        hour = int(time_parts[0])
                        minute = time_parts[1]
                        second = time_parts[2]
                        period = "오후" if hour >= 12 else "오전"
                        display_hour = hour - 12 if hour > 12 else hour
                        display_hour = 12 if hour == 12 else display_hour
                        display_hour = 12 if hour == 0 else display_hour
                        formatted_tooltip = f"{formatted_date} {period} {display_hour}:{minute}:{second}"

            # 한국어 형식: "2025. 9. 26. 오후 11:10:39"
            elif ". " in s and ("오전" in s or "오후" in s):
                period = "오전" if "오전" in s else "오후"
                s_clean = s.replace(" 오전", "").replace(" 오후", "")
                parts = s_clean.split(". ")
                if len(parts) >= 4:
                    year = parts[0][2:4] if len(parts[0]) == 4 else parts[0]
                    month = parts[1].zfill(2)
                    day = parts[2].zfill(2)
                    formatted_date = f"{year}{month}{day}"
                    time = parts[3].strip()
                    formatted_tooltip = f"{formatted_date} {period} {time}"

            # 기본: 날짜 부분만 추출 (앞 10자)
            else:
                try:
                    date_part = s[:10].replace("-", "").replace(".", "").replace("/", "")
                    if len(date_part) >= 8:
                        year = date_part[2:4] if len(date_part[:4]) == 4 else date_part[:2]
                        month = date_part[4:6] if len(date_part[:4]) == 4 else date_part[2:4]
                        day = date_part[6:8] if len(date_part[:4]) == 4 else date_part[4:6]
                        formatted_date = f"{year}{month}{day}"
                        formatted_tooltip = s
                    else:
                        formatted_date = s[:10]
                        formatted_tooltip = s
                except:
                    formatted_date = s[:10]
                    formatted_tooltip = s

            # complain 객체에 속성 추가
            complain.formatted_date = formatted_date
            complain.formatted_tooltip = formatted_tooltip

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


def satisfy_list(request):
    """고객만족도 이력 리스트"""
    # 현재 로그인한 스태프 정보
    current_staff = None
    if 'staff_user' in request.session:
        try:
            current_staff = Staff.objects.get(no=request.session['staff_user']['no'])
        except Staff.DoesNotExist:
            pass

    # 필터링 파라미터
    search_query = request.GET.get('search', '')
    condition_filters = request.GET.getlist('condition')  # 체크박스 리스트

    # 기본 쿼리셋
    queryset = Satisfy.objects.all()

    # 활동상태 필터링
    if condition_filters:
        # Company 테이블의 nCondition으로 필터링
        company_nos = Company.objects.filter(
            nCondition__in=condition_filters
        ).values_list('no', flat=True)
        queryset = queryset.filter(noCompany__in=company_nos)
    else:
        # 기본값: 정상(1)과 일시정지(2)만 표시
        company_nos = Company.objects.filter(
            nCondition__in=[1, 2]
        ).values_list('no', flat=True)
        queryset = queryset.filter(noCompany__in=company_nos)

    # 통합 검색
    if search_query:
        # Company 관련 검색을 위한 서브쿼리
        company_search = Company.objects.filter(
            Q(sName1__icontains=search_query) |
            Q(sName2__icontains=search_query) |
            Q(sName3__icontains=search_query)
        ).values_list('no', flat=True)

        queryset = queryset.filter(
            Q(sCompanyName__icontains=search_query) |
            Q(sPhone__icontains=search_query) |
            Q(sArea__icontains=search_query) |
            Q(sS11__icontains=search_query) |
            Q(noCompany__in=company_search)
        )

    # 정렬 (no 기준 내림차순 - 최신 ID 먼저)
    queryset = queryset.order_by('-no')

    # 페이징 처리
    from django.core.paginator import Paginator
    paginator = Paginator(queryset, 20)  # 한 페이지에 20개
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # 각 satisfy 객체에 company 정보 추가 및 날짜 형식 처리
    import re
    from datetime import datetime

    for satisfy in page_obj:
        try:
            company = Company.objects.get(no=satisfy.noCompany)
            satisfy.company = company
        except Company.DoesNotExist:
            satisfy.company = None

        # sTimeStamp를 YYMMDD 형식으로 변환 및 툴팁 포맷
        if satisfy.sTimeStamp and not satisfy.timeStamp:
            s = satisfy.sTimeStamp
            formatted_date = ""
            formatted_tooltip = ""

            # 영어 형식: "Fri Sep 26 2025 23:13:11 GMT+0900"
            if "GMT" in s:
                month_map = {'Jan':'01','Feb':'02','Mar':'03','Apr':'04','May':'05','Jun':'06',
                           'Jul':'07','Aug':'08','Sep':'09','Oct':'10','Nov':'11','Dec':'12'}
                parts = s.split()
                if len(parts) >= 5:
                    year = parts[3][2:4] if len(parts[3]) == 4 else parts[3]
                    month = month_map.get(parts[1], '00')
                    day = parts[2].zfill(2)
                    formatted_date = f"{year}{month}{day}"

                    # 시간 파싱 및 오전/오후 변환
                    time_parts = parts[4].split(':')
                    if len(time_parts) >= 3:
                        hour = int(time_parts[0])
                        minute = time_parts[1]
                        second = time_parts[2]
                        period = "오후" if hour >= 12 else "오전"
                        display_hour = hour - 12 if hour > 12 else hour
                        display_hour = 12 if hour == 12 else display_hour
                        display_hour = 12 if hour == 0 else display_hour
                        formatted_tooltip = f"{formatted_date} {period} {display_hour}:{minute}:{second}"

            # 한국어 형식: "2025. 09. 26. 오후 11:55:00"
            elif "." in s and len(s) >= 12:
                formatted_date = s[2:4] + s[6:8] + s[10:12]
                # 이미 한국어 형식이므로 날짜 부분만 변경
                if "오전" in s or "오후" in s:
                    formatted_tooltip = f"{formatted_date} {s[14:]}"  # 날짜 이후 부분
                else:
                    formatted_tooltip = s
            # 기타 ISO 형식들
            else:
                try:
                    # 다양한 형식 파싱 시도
                    for fmt in ['%Y-%m-%dT%H:%M:%S.%fZ', '%Y-%m-%d %H:%M:%S', '%Y. %m. %d']:
                        try:
                            dt = datetime.strptime(s[:19], fmt[:10])
                            formatted_date = dt.strftime('%y%m%d')
                            break
                        except:
                            continue
                except:
                    formatted_date = s[:10]

            satisfy.formatted_date = formatted_date if formatted_date else s[:10]
            satisfy.formatted_tooltip = formatted_tooltip if formatted_tooltip else s

    # 필터링된 업체 리스트 (드롭다운용) - 현재 선택된 활동상태 반영
    if condition_filters:
        filtered_conditions = [int(c) for c in condition_filters]
    else:
        filtered_conditions = [1, 2]  # 기본값: 정상, 일시정지

    all_companies = Company.objects.filter(
        nCondition__in=filtered_conditions
    ).order_by('sName2', 'sName1')

    context = {
        'current_staff': current_staff,
        'satisfies': page_obj,
        'all_companies': all_companies,
        'search_query': search_query,
        'condition_filters': filtered_conditions,
        'total_count': queryset.count(),
    }

    return render(request, 'evaluation/satisfy_list.html', context)


@csrf_exempt
@require_http_methods(["POST"])
def satisfy_update_company(request):
    """고객만족도 업체 업데이트 (AJAX)"""
    try:
        data = json.loads(request.body)
        satisfy_id = data.get('satisfy_id')
        company_no = data.get('company_no', 0)

        satisfy = get_object_or_404(Satisfy, pk=satisfy_id)
        satisfy.noCompany = company_no
        satisfy.save()

        # 업체명 가져오기
        company_name = ""
        if company_no:
            try:
                company = Company.objects.get(no=company_no)
                company_name = company.sName1
            except Company.DoesNotExist:
                pass

        return JsonResponse({
            'success': True,
            'company_name': company_name
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@csrf_exempt
@require_http_methods(["POST"])
def satisfy_delete(request, pk):
    """Satisfy 데이터 삭제 (AJAX)"""
    try:
        satisfy = Satisfy.objects.get(no=pk)
        satisfy.delete()

        return JsonResponse({
            'success': True,
            'message': '삭제되었습니다.'
        })
    except Satisfy.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': '데이터를 찾을 수 없습니다.'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })
