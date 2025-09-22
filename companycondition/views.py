from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from company.models import Company
from staff.views import get_current_staff
import json

def company_condition_list(request):
    # 현재 스텝 정보 가져오기
    current_staff = get_current_staff(request)

    # nType이 0,1,2,3이고 nCondition이 1,2인 업체만 필터링
    companies = Company.objects.filter(
        nType__in=[0, 1, 2, 3],  # 일반토탈, 고정비토탈, 부분단종, 순수단종
        nCondition__in=[1, 2]    # 정상, 일시정지
    ).order_by('-no')

    # 선택된 업체 정보
    selected_company = None
    if request.GET.get('company_id'):
        try:
            selected_company = companies.get(no=request.GET.get('company_id'))
        except Company.DoesNotExist:
            pass

    return render(request, 'companycondition/company_condition_list.html', {
        'companies': companies,
        'selected_company': selected_company,
        'current_staff': current_staff
    })

def search_companies(request):
    """AJAX로 업체 검색"""
    search_query = request.GET.get('q', '').strip()

    # 필터링된 업체에서 검색
    companies = Company.objects.filter(
        nType__in=[0, 1, 2, 3],
        nCondition__in=[1, 2]
    )

    if search_query:
        companies = companies.filter(sName2__icontains=search_query)

    # 검색어가 없으면 전체 표시 (최대 50개), 있으면 최대 20개
    limit = 50 if not search_query else 20
    companies = companies.order_by('sName2')[:limit]

    results = []
    for company in companies:
        results.append({
            'id': company.no,
            'name': company.sName2 or company.sName1,
            'type': company.get_nType_display(),
            'condition': company.get_nCondition_display(),
            'type_value': company.nType,
            'condition_value': company.nCondition
        })

    return JsonResponse({'results': results})

def get_company_detail(request, company_id):
    """AJAX로 업체 상세 정보 조회"""
    company = get_object_or_404(Company, no=company_id)

    # 필터 조건 확인
    if company.nType not in [0, 1, 2, 3] or company.nCondition not in [1, 2]:
        return JsonResponse({'error': '조회할 수 없는 업체입니다.'}, status=400)

    data = {
        'id': company.no,
        'name': company.sName2 or company.sName1,
        'type': company.get_nType_display(),
        'condition': company.get_nCondition_display(),
        'level': company.nLevel if hasattr(company, 'nLevel') else 0,
        'grade': company.nGrade if hasattr(company, 'nGrade') else 0,
        'apply_grade': company.nApplyGrade if hasattr(company, 'nApplyGrade') else 0,
        'apply_grade_reason': company.sApplyGradeReason if hasattr(company, 'sApplyGradeReason') else '',
        'assign_all_2': company.nAssignAll2 if hasattr(company, 'nAssignAll2') else 0,
        'assign_part_2': company.nAssignPart2 if hasattr(company, 'nAssignPart2') else 0,
        'assign_all_term': company.nAssignAllTerm if hasattr(company, 'nAssignAllTerm') else 0,
        'assign_part_term': company.nAssignPartTerm if hasattr(company, 'nAssignPartTerm') else 0,
        'assign_max': company.nAssignMax if hasattr(company, 'nAssignMax') else 0,
        'assign_percent': company.fAssignPercent if hasattr(company, 'fAssignPercent') else 0.0,
        'assign_lack': company.fAssignLack if hasattr(company, 'fAssignLack') else 0
    }

    return JsonResponse(data)

@require_POST
@csrf_exempt
def update_apply_grade(request, company_id):
    """적용등급 변경"""
    try:
        company = get_object_or_404(Company, no=company_id)

        # 필터 조건 확인
        if company.nType not in [0, 1, 2, 3] or company.nCondition not in [1, 2]:
            return JsonResponse({'error': '수정할 수 없는 업체입니다.'}, status=400)

        data = json.loads(request.body)
        apply_grade = data.get('apply_grade')
        apply_grade_reason = data.get('apply_grade_reason', '')

        if apply_grade is not None:
            if hasattr(company, 'nApplyGrade'):
                company.nApplyGrade = apply_grade
            if hasattr(company, 'sApplyGradeReason'):
                company.sApplyGradeReason = apply_grade_reason
            company.save()

            return JsonResponse({
                'success': True,
                'message': '적용등급이 변경되었습니다.',
                'apply_grade': apply_grade,
                'apply_grade_reason': apply_grade_reason
            })
        else:
            return JsonResponse({'error': '적용등급 값이 필요합니다.'}, status=400)

    except json.JSONDecodeError:
        return JsonResponse({'error': '잘못된 데이터 형식입니다.'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
