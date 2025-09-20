from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import PossibleArea
from company.models import Company
from area.models import Area
import json


def getHierarchyIcon(area_id):
    """지역 ID를 기반으로 계층 아이콘 반환"""
    if area_id == 0:
        return '🌍'  # 전국
    elif 1000 <= area_id < 10000 and area_id % 1000 == 0:
        return '🏛️'  # 광역지역
    else:
        return '🏢'  # 시군구/구


def get_current_staff(request):
    """현재 로그인한 스텝 정보 반환"""
    from staff.models import Staff
    staff_user = request.session.get('staff_user')
    if not staff_user:
        return None
    return Staff.objects.filter(no=staff_user['no']).first()


class PossiManageView(View):
    """공사 가능 지역 관리 메인 페이지"""

    def get(self, request):
        """공사 가능 지역 관리 화면 표시"""
        # 로그인 확인
        if not request.session.get('staff_user'):
            messages.error(request, '로그인이 필요합니다.')
            return redirect('accounts:login')

        current_staff = get_current_staff(request)

        # 대상 업체 타입 (0일반토탈, 1고정비토탈, 2순수단종, 3부분단종, 4btoc제휴)
        target_company_types = [0, 1, 2, 3, 4]

        # 업체 목록 조회 (탈퇴업체 nCondition=3, btob제휴 nType=5 제외)
        companies = Company.objects.filter(
            nType__in=target_company_types
        ).exclude(
            nCondition=3  # 탈퇴업체 제외
        ).exclude(
            nType=5  # btob제휴업체 제외
        ).order_by('no')

        # 지역 목록 조회
        # 추가지역용: 전체 지역 (광역지역 + 시군구지역)
        all_areas = Area.objects.all().order_by('no')

        # 제외지역용: 시군구지역만
        city_areas = Area.objects.exclude(sCity="").order_by('no')

        # 검색 파라미터 가져오기
        search_query = request.GET.get('search', '').strip()

        context = {
            'title': '공사 가능 지역',
            'current_staff': current_staff,
            'staff_user': request.session.get('staff_user'),
            'companies': companies,
            'all_areas': all_areas,  # 추가지역용 (광역+시군구)
            'city_areas': city_areas,  # 제외지역용 (시군구만)
            'search_query': search_query,  # 검색어 전달
            'all_construction_types': [
                (0, '올수리 가능한 지역'),
                (1, '부분수리 가능한 지역'),
                (2, '신축/증축 가능한 지역'),
                # 부가서비스(3) 제외
            ],
        }

        return render(request, 'possiblearea/possi_manage.html', context)


@method_decorator(csrf_exempt, name='dispatch')
class PossiDataView(View):
    """공사 가능 지역 데이터 조회/관리 API"""

    def get(self, request):
        """특정 업체의 공사 가능 지역 데이터 조회"""
        company_id = request.GET.get('company_id')

        if not company_id:
            return JsonResponse({'success': False, 'error': '업체 ID가 필요합니다.'})

        try:
            # 해당 업체의 모든 공사 가능 지역 데이터 조회
            possi_data = {}

            # 각 공사종류별로 데이터 구성 (모든 공사종류 포함)
            for const_type_value, const_type_name in PossibleArea.CONSTRUCTION_TYPE_CHOICES:
                possi_data[const_type_value] = {
                    'name': const_type_name,
                    'areas': {
                        'additional': [],  # 추가지역 (0)
                        'company_exclude': [],  # 업체제외지역 (1)
                        'staff_exclude': [],  # 스텝제외지역 (2)
                        'company_request': [],  # 업체요청지역 (3)
                        'actual_assigned': [],  # 실제할당지역 (4)
                    }
                }

                # 추가지역 조회
                additional_areas = PossibleArea.objects.filter(
                    noCompany=company_id,
                    nConstructionType=const_type_value,
                    nAreaType=0  # 추가지역
                ).select_related()

                for area in additional_areas:
                    try:
                        area_obj = Area.objects.get(no=area.noArea)
                        possi_data[const_type_value]['areas']['additional'].append({
                            'id': area.no,
                            'area_id': area.noArea,
                            'area_name': area_obj.get_full_name(),
                            'display_name': f"{getHierarchyIcon(area.noArea)} {area_obj.get_full_name()}"
                        })
                    except Area.DoesNotExist:
                        continue

                # 업체제외지역 조회
                company_exclude_areas = PossibleArea.objects.filter(
                    noCompany=company_id,
                    nConstructionType=const_type_value,
                    nAreaType=1  # 업체제외지역
                ).select_related()

                for area in company_exclude_areas:
                    try:
                        area_obj = Area.objects.get(no=area.noArea)
                        possi_data[const_type_value]['areas']['company_exclude'].append({
                            'id': area.no,
                            'area_id': area.noArea,
                            'area_name': area_obj.get_full_name(),
                            'display_name': f"{getHierarchyIcon(area.noArea)} {area_obj.get_full_name()}"
                        })
                    except Area.DoesNotExist:
                        continue

                # 스텝제외지역 조회
                staff_exclude_areas = PossibleArea.objects.filter(
                    noCompany=company_id,
                    nConstructionType=const_type_value,
                    nAreaType=2  # 스텝제외지역
                ).select_related()

                for area in staff_exclude_areas:
                    try:
                        area_obj = Area.objects.get(no=area.noArea)
                        possi_data[const_type_value]['areas']['staff_exclude'].append({
                            'id': area.no,
                            'area_id': area.noArea,
                            'area_name': area_obj.get_full_name(),
                            'display_name': f"{getHierarchyIcon(area.noArea)} {area_obj.get_full_name()}"
                        })
                    except Area.DoesNotExist:
                        continue

                # 업체요청지역(3) 조회
                company_request_areas = PossibleArea.objects.filter(
                    noCompany=company_id,
                    nConstructionType=const_type_value,
                    nAreaType=3  # 업체요청지역
                ).select_related().order_by('noArea')

                possi_data[const_type_value]['areas']['company_request'] = []
                for area in company_request_areas:
                    try:
                        area_obj = Area.objects.get(no=area.noArea)
                        possi_data[const_type_value]['areas']['company_request'].append({
                            'id': area.no,
                            'area_id': area.noArea,
                            'area_name': area_obj.get_full_name(),
                            'display_name': f"{getHierarchyIcon(area.noArea)} {area_obj.get_full_name()}"
                        })
                    except Area.DoesNotExist:
                        continue

                # 실제할당지역(4) 조회
                actual_assigned_areas = PossibleArea.objects.filter(
                    noCompany=company_id,
                    nConstructionType=const_type_value,
                    nAreaType=4  # 실제할당지역
                ).select_related().order_by('noArea')

                possi_data[const_type_value]['areas']['actual_assigned'] = []
                for area in actual_assigned_areas:
                    try:
                        area_obj = Area.objects.get(no=area.noArea)
                        possi_data[const_type_value]['areas']['actual_assigned'].append({
                            'id': area.no,
                            'area_id': area.noArea,
                            'area_name': area_obj.get_full_name(),
                            'display_name': f"{getHierarchyIcon(area.noArea)} {area_obj.get_full_name()}"
                        })
                    except Area.DoesNotExist:
                        continue

            return JsonResponse({
                'success': True,
                'data': possi_data
            })

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    def post(self, request):
        """공사 가능 지역 추가"""
        try:
            data = json.loads(request.body)
            company_id = data.get('company_id')
            construction_type = data.get('construction_type')
            area_type = data.get('area_type')
            area_id = data.get('area_id')

            if not all([company_id, construction_type is not None, area_type is not None, area_id]):
                return JsonResponse({'success': False, 'error': '필수 데이터가 누락되었습니다.'})

            # 중복 체크
            existing = PossibleArea.objects.filter(
                noCompany=company_id,
                nConstructionType=construction_type,
                nAreaType=area_type,
                noArea=area_id
            ).exists()

            if existing:
                return JsonResponse({'success': False, 'error': '이미 등록된 지역입니다.'})

            # 지역 정보 확인
            try:
                area = Area.objects.get(no=area_id)
            except Area.DoesNotExist:
                return JsonResponse({'success': False, 'error': '존재하지 않는 지역입니다.'})

            # 추가지역이 아닌데 광역지역을 선택한 경우 체크
            if area_type != 0 and area.sCity == "":
                return JsonResponse({'success': False, 'error': '해당 지역 타입에는 시군구지역만 선택할 수 있습니다.'})

            # 업체제외지역(1)과 스텝제외지역(2)에서 통합시 자동 확장
            if area_type in [1, 2]:  # 업체제외지역, 스텝제외지역
                is_integrated_city = ('(' not in area.sCity and ')' not in area.sCity and
                                    area.sCity != '' and area.no > 1000 and
                                    area.is_integrated_city())
                if is_integrated_city:
                    # 통합시의 하위 구들을 모두 추가
                    districts = area.get_all_descendants()
                    added_districts = []

                    for district in districts:
                        # 중복 체크
                        existing = PossibleArea.objects.filter(
                            noCompany=company_id,
                            nConstructionType=construction_type,
                            nAreaType=area_type,
                            noArea=district.no
                        ).exists()

                        if not existing:
                            # 계층 구조 충돌 검사
                            existing_areas = PossibleArea.objects.filter(
                                noCompany=company_id,
                                nConstructionType=construction_type,
                                nAreaType=area_type
                            ).values_list('noArea', flat=True)

                            conflicts = Area.get_hierarchy_conflicts(district.no, list(existing_areas))
                            if not conflicts:
                                PossibleArea.objects.create(
                                    noCompany=company_id,
                                    nConstructionType=construction_type,
                                    nAreaType=area_type,
                                    noArea=district.no
                                )
                                added_districts.append(district)

                    # 계산된 지역 업데이트
                    calculation_result = PossibleArea.update_calculated_areas(company_id, construction_type)
                    print(f"DEBUG: 통합시 자동 확장 - {area.get_full_name()} → {len(added_districts)}개 구 추가")

                    return JsonResponse({
                        'success': True,
                        'auto_expanded': True,
                        'expanded_from': area.get_full_name(),
                        'added_districts': [{'id': d.no, 'name': d.get_full_name()} for d in added_districts],
                        'added_count': len(added_districts)
                    })

            # 계층 구조 충돌 검사
            existing_areas = PossibleArea.objects.filter(
                noCompany=company_id,
                nConstructionType=construction_type,
                nAreaType=area_type
            ).values_list('noArea', flat=True)

            conflicts = Area.get_hierarchy_conflicts(area_id, list(existing_areas))
            if conflicts:
                return JsonResponse({
                    'success': False,
                    'error': '계층 구조 충돌: ' + ', '.join(conflicts)
                })

            # 데이터 생성
            possi = PossibleArea.objects.create(
                noCompany=company_id,
                nConstructionType=construction_type,
                nAreaType=area_type,
                noArea=area_id
            )

            # 추가지역(0), 업체제외지역(1), 스텝제외지역(2) 변경 시 계산된 지역 업데이트
            if area_type in [0, 1, 2]:
                calculation_result = PossibleArea.update_calculated_areas(company_id, construction_type)
                print(f"DEBUG: 계산된 지역 업데이트 - 업체요청: {calculation_result['company_request_count']}개, 실제할당: {calculation_result['actual_assigned_count']}개")

            return JsonResponse({
                'success': True,
                'data': {
                    'id': possi.no,
                    'area_id': area.no,
                    'area_name': area.get_full_name(),
                    'hierarchy_info': {
                        'is_nationwide': area.is_nationwide(),
                        'is_metro': area.is_metro_area(),
                        'is_city': area.is_city_area()
                    }
                }
            })

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    def delete(self, request):
        """공사 가능 지역 삭제"""
        try:
            data = json.loads(request.body)
            possi_id = data.get('possi_id')

            if not possi_id:
                return JsonResponse({'success': False, 'error': 'ID가 필요합니다.'})

            try:
                possi = PossibleArea.objects.get(no=possi_id)
                # 삭제 전에 정보 저장 (계산 업데이트를 위해)
                company_id = possi.noCompany
                construction_type = possi.nConstructionType
                area_type = possi.nAreaType

                possi.delete()

                # 추가지역(0), 업체제외지역(1), 스텝제외지역(2) 삭제 시 계산된 지역 업데이트
                if area_type in [0, 1, 2]:
                    calculation_result = PossibleArea.update_calculated_areas(company_id, construction_type)
                    print(f"DEBUG: 삭제 후 계산된 지역 업데이트 - 업체요청: {calculation_result['company_request_count']}개, 실제할당: {calculation_result['actual_assigned_count']}개")

                return JsonResponse({'success': True, 'message': '삭제되었습니다.'})

            except PossibleArea.DoesNotExist:
                return JsonResponse({'success': False, 'error': '존재하지 않는 데이터입니다.'})

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})