from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import Q
from .models import Gonggu, GongguArea
from company.models import Company
from staff.views import get_current_staff
import json

def gonggu_list(request):
    """공동구매 리스트"""
    # 현재 스텝 정보 가져오기
    current_staff = get_current_staff(request)

    # 필요한 모델들 import
    from .models import GongguCompany, GongguArea
    from company.models import Company
    from area.models import Area

    # 필터링 파라미터
    selected_step_types = request.GET.getlist('nStepType')
    selected_types = request.GET.getlist('nType')
    search_query = request.GET.get('search', '').strip()

    # 기본값: 파라미터가 아예 없으면 진행중(nStepType=1)만 표시
    # 단, URL에 파라미터가 있다면 사용자가 의도적으로 필터링한 것으로 간주
    if not request.GET:  # GET 파라미터가 아예 없는 경우에만 기본값 적용
        selected_step_types = ['1']  # 진행중

    # 기본 쿼리셋
    gonggus = Gonggu.objects.all()

    # nStepType 필터링
    if selected_step_types:
        gonggus = gonggus.filter(nStepType__in=selected_step_types)

    # nType 필터링
    if selected_types:
        gonggus = gonggus.filter(nType__in=selected_types)

    # 통합 검색 (업체명, 지역명 포함)
    if search_query:
        # 기본 Gonggu 필드 검색
        gonggu_q = Q(sNo__icontains=search_query) | Q(sName__icontains=search_query) | Q(sStrength__icontains=search_query)

        # 업체명으로 검색된 GongguCompany의 공구 ID 찾기
        company_ids = Company.objects.filter(
            Q(sName1__icontains=search_query) | Q(sName2__icontains=search_query)
        ).values_list('no', flat=True)

        if company_ids:
            gonggu_ids_from_companies = GongguCompany.objects.filter(
                noCompany__in=company_ids
            ).values_list('noGonggu', flat=True)
            gonggu_q |= Q(no__in=gonggu_ids_from_companies)

        # 지역명으로 검색된 GongguArea의 공구 ID 찾기
        area_ids = Area.objects.filter(
            Q(sState__icontains=search_query) | Q(sCity__icontains=search_query)
        ).values_list('no', flat=True)

        if area_ids:
            gonggu_company_ids_from_areas = GongguArea.objects.filter(
                noArea__in=area_ids
            ).values_list('noGongguCompany', flat=True)

            gonggu_ids_from_areas = GongguCompany.objects.filter(
                no__in=gonggu_company_ids_from_areas
            ).values_list('noGonggu', flat=True)

            gonggu_q |= Q(no__in=gonggu_ids_from_areas)

        gonggus = gonggus.filter(gonggu_q).distinct()

    # 최신순 정렬
    gonggus = gonggus.order_by('-no')

    # 공동구매 데이터에 업체와 지역 정보 추가 (업체별로 분리하여 표시)

    gonggu_data = []
    for gonggu in gonggus:
        # 해당 공구의 모든 참여업체 가져오기
        gonggu_companies = GongguCompany.objects.filter(noGonggu=gonggu.no)

        if gonggu_companies.exists():
            # 각 참여업체별로 별도의 행 생성
            for gonggu_company in gonggu_companies:
                # 업체 정보 가져오기
                try:
                    company = Company.objects.get(no=gonggu_company.noCompany)
                    company_name = company.sName2 or company.sName1 or f"업체{gonggu_company.noCompany}"
                except Company.DoesNotExist:
                    company_name = f"업체{gonggu_company.noCompany}"

                # 해당 공구업체의 실제할당지역(nType=2) 가져오기
                assigned_areas = GongguArea.objects.filter(noGongguCompany=gonggu_company.no, nType=2)

                area_names = []
                for area_entry in assigned_areas:
                    try:
                        area = Area.objects.get(no=area_entry.noArea)
                        area_name = area.get_full_name()
                        area_names.append(area_name)
                    except Area.DoesNotExist:
                        area_names.append(f"지역{area_entry.noArea}")

                # 지역 정보 포매팅
                areas_text = ', '.join(sorted(set(area_names))) if area_names else '-'

                gonggu_data.append({
                    'gonggu': gonggu,
                    'company': company_name,
                    'areas': areas_text,
                    'gonggu_company_id': gonggu_company.no
                })
        else:
            # 참여업체가 없는 경우 공구만 표시
            gonggu_data.append({
                'gonggu': gonggu,
                'company': '-',
                'areas': '-',
                'gonggu_company_id': None
            })

    context = {
        'gonggu_data': gonggu_data,
        'selected_step_types': selected_step_types,
        'selected_types': selected_types,
        'search_query': search_query,
        'current_staff': current_staff,
    }

    return render(request, 'gonggu/gonggu_list.html', context)

def gonggu_create(request):
    """공동구매 생성"""
    current_staff = get_current_staff(request)

    if not current_staff or current_staff.nOrderAuthority < 2:
        messages.error(request, '공동구매 생성 권한이 없습니다.')
        return redirect('gonggu:gonggu_list')

    if request.method == 'POST':
        # 공동구매 생성 로직
        try:
            gonggu = Gonggu.objects.create(
                nStepType=request.POST.get('nStepType', 0),
                nType=request.POST.get('nType', 0),
                sNo=request.POST.get('sNo', ''),
                dateStart=request.POST.get('dateStart') if request.POST.get('dateStart') else None,
                dateEnd=request.POST.get('dateEnd') if request.POST.get('dateEnd') else None,
                sName=request.POST.get('sName', ''),
                sPost=request.POST.get('sPost', ''),
                sStrength=request.POST.get('sStrength', ''),
                nCommentPre=request.POST.get('nCommentPre', 0),
                nCommentNow=request.POST.get('nCommentNow', 0)
            )
            messages.success(request, '공동구매가 생성되었습니다.')
            return redirect('gonggu:gonggu_detail', pk=gonggu.no)
        except Exception as e:
            messages.error(request, f'공동구매 생성 중 오류가 발생했습니다: {str(e)}')

    return render(request, 'gonggu/gonggu_form.html', {
        'current_staff': current_staff,
        'form_type': 'create'
    })

def gonggu_detail(request, pk):
    """공동구매 상세보기/수정"""
    current_staff = get_current_staff(request)
    gonggu = get_object_or_404(Gonggu, no=pk)

    # 권한 체크
    can_edit = current_staff and current_staff.nOrderAuthority >= 2

    # 편집 모드 확인
    is_edit_mode = request.GET.get('edit') == '1' and can_edit

    if request.method == 'POST' and can_edit:
        # 수정 로직
        try:
            gonggu.nStepType = request.POST.get('nStepType', gonggu.nStepType)
            gonggu.nType = request.POST.get('nType', gonggu.nType)
            gonggu.sNo = request.POST.get('sNo', gonggu.sNo)
            # 날짜 필드 처리 (빈 값이면 None으로 설정)
            date_start = request.POST.get('dateStart')
            date_end = request.POST.get('dateEnd')
            gonggu.dateStart = date_start if date_start else None
            gonggu.dateEnd = date_end if date_end else None
            gonggu.sName = request.POST.get('sName', gonggu.sName)
            gonggu.sPost = request.POST.get('sPost', gonggu.sPost)
            gonggu.sStrength = request.POST.get('sStrength', gonggu.sStrength)
            gonggu.nCommentPre = request.POST.get('nCommentPre', gonggu.nCommentPre)
            gonggu.nCommentNow = request.POST.get('nCommentNow', gonggu.nCommentNow)
            gonggu.save()

            messages.success(request, '공동구매가 수정되었습니다.')
            return redirect('gonggu:gonggu_detail', pk=gonggu.no)
        except Exception as e:
            messages.error(request, f'공동구매 수정 중 오류가 발생했습니다: {str(e)}')

    # 관련 업체 및 지역 정보
    from .models import GongguCompany, GongguArea
    gonggu_companies = GongguCompany.objects.filter(noGonggu=gonggu.no)

    # 모든 관련 지역 정보 (모든 참여업체의 지역)
    gonggu_company_ids = [gc.no for gc in gonggu_companies]
    areas = GongguArea.objects.filter(noGongguCompany__in=gonggu_company_ids)

    # 편집 모드일 때 사용 가능한 업체 목록 제공
    available_companies = []
    if is_edit_mode:
        # 이미 참여 중인 업체 ID 목록
        existing_company_ids = [gc.noCompany for gc in gonggu_companies]

        # 참여하지 않은 업체들만 선택 가능하도록 필터링
        available_companies = Company.objects.exclude(no__in=existing_company_ids).order_by('sName1', 'sName2')

    context = {
        'gonggu': gonggu,
        'gonggu_companies': gonggu_companies,
        'areas': areas,
        'current_staff': current_staff,
        'can_edit': can_edit,
        'form_type': 'edit' if is_edit_mode else 'view',
        'available_companies': available_companies
    }

    return render(request, 'gonggu/gonggu_detail.html', context)

def gonggu_delete(request, pk):
    """공동구매 삭제"""
    current_staff = get_current_staff(request)

    if not current_staff or current_staff.nOrderAuthority < 2:
        return JsonResponse({'error': '삭제 권한이 없습니다.'}, status=403)

    if request.method == 'POST':
        try:
            gonggu = get_object_or_404(Gonggu, no=pk)
            gonggu.delete()
            return JsonResponse({'success': True, 'message': '공동구매가 삭제되었습니다.'})
        except Exception as e:
            return JsonResponse({'error': f'삭제 중 오류가 발생했습니다: {str(e)}'}, status=500)

    return JsonResponse({'error': '잘못된 요청입니다.'}, status=400)

def getHierarchyIcon(area_id):
    """지역 ID를 기반으로 계층 아이콘 반환"""
    if area_id == 0:
        return '🌍'  # 전국
    elif 1000 <= area_id < 10000 and area_id % 1000 == 0:
        return '🏛️'  # 광역지역
    else:
        return '🏢'  # 시군구/구


def area_manage(request, gonggu_company_id):
    """공동구매 가능 지역 관리"""
    current_staff = get_current_staff(request)

    if not current_staff or current_staff.nOrderAuthority < 2:
        messages.error(request, '지역 관리 권한이 없습니다.')
        return redirect('gonggu:gonggu_list')

    # 필요한 모델들 import
    from .models import GongguCompany, GongguArea
    from area.models import Area

    try:
        gonggu_company = get_object_or_404(GongguCompany, no=gonggu_company_id)
        gonggu = get_object_or_404(Gonggu, no=gonggu_company.noGonggu)
    except:
        messages.error(request, '해당 공동구매 업체를 찾을 수 없습니다.')
        return redirect('gonggu:gonggu_list')

    if request.method == 'POST':
        # AJAX 저장 요청 처리 - 개별 지역 추가/삭제
        try:
            data = json.loads(request.body)
            action = data.get('action')  # 'add' 또는 'remove'
            area_type = data.get('area_type')  # 0=추가지역, 1=제외지역
            area_id = data.get('area_id')

            if action == 'add':
                # 중복 체크
                existing = GongguArea.objects.filter(
                    noGongguCompany=gonggu_company_id,
                    nType=area_type,
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

                # 계층 구조 충돌 검사
                existing_areas = GongguArea.objects.filter(
                    noGongguCompany=gonggu_company_id,
                    nType=area_type
                ).values_list('noArea', flat=True)

                conflicts = Area.get_hierarchy_conflicts(area_id, list(existing_areas))
                if conflicts:
                    return JsonResponse({
                        'success': False,
                        'error': '계층 구조 충돌: ' + ', '.join(conflicts)
                    })

                # 데이터 생성
                GongguArea.objects.create(
                    noGongguCompany=gonggu_company_id,
                    nType=area_type,
                    noArea=area_id
                )

                # 실제할당지역 자동 계산
                calculate_assigned_areas_auto(gonggu_company_id)

                return JsonResponse({
                    'success': True,
                    'data': {
                        'area_id': area.no,
                        'area_name': area.get_full_name(),
                        'display_name': f"{getHierarchyIcon(area.no)} {area.get_full_name()}"
                    }
                })

            elif action == 'remove':
                try:
                    gonggu_area = GongguArea.objects.get(
                        noGongguCompany=gonggu_company_id,
                        nType=area_type,
                        noArea=area_id
                    )
                    gonggu_area.delete()

                    # 실제할당지역 자동 계산
                    calculate_assigned_areas_auto(gonggu_company_id)

                    return JsonResponse({'success': True, 'message': '삭제되었습니다.'})

                except GongguArea.DoesNotExist:
                    return JsonResponse({'success': False, 'error': '존재하지 않는 데이터입니다.'})

            return JsonResponse({'success': False, 'error': '잘못된 요청입니다.'})

        except Exception as e:
            return JsonResponse({'error': f'처리 중 오류가 발생했습니다: {str(e)}'}, status=500)

    # GET 요청 - 지역 관리 페이지 표시
    # 모든 지역 가져오기 (추가지역용) - Area.no 올림차순 정렬
    all_areas = Area.objects.all().order_by('no')

    # 시군구지역 중 통합시 제외 (제외지역용) - Area.no 올림차순 정렬
    # 통합시: 하위에 구가 있는 시 (고양시, 성남시, 안양시, 안산시, 수원시, 용인시, 창원시 등)
    # Area 모델의 is_integrated_city() 메서드를 사용하여 동적으로 필터링
    all_city_areas = Area.objects.filter(
        sCity__isnull=False
    ).exclude(
        sCity__exact=''
    )

    # 통합시가 아닌 시군구지역만 필터링
    filtered_areas = []
    for area in all_city_areas:
        if not area.is_integrated_city():
            filtered_areas.append(area)

    # Area.no 올림차순으로 정렬
    filtered_areas = sorted(filtered_areas, key=lambda x: x.no, reverse=False)

    # 현재 저장된 지역들
    additional_areas = GongguArea.objects.filter(noGongguCompany=gonggu_company_id, nType=0)
    excluded_areas = GongguArea.objects.filter(noGongguCompany=gonggu_company_id, nType=1)
    assigned_areas = GongguArea.objects.filter(noGongguCompany=gonggu_company_id, nType=2)

    context = {
        'gonggu': gonggu,
        'gonggu_company': gonggu_company,
        'all_areas': all_areas,
        'filtered_areas': filtered_areas,
        'additional_areas': additional_areas,
        'excluded_areas': excluded_areas,
        'assigned_areas': assigned_areas,
        'current_staff': current_staff,
    }

    return render(request, 'gonggu/area_manage.html', context)

def calculate_assigned_areas_auto(gonggu_company_id):
    """실제할당지역 자동 계산 및 저장 (PossibleArea 방식과 동일)"""
    from .models import GongguArea
    from area.models import Area

    # 기존 실제할당지역 삭제
    GongguArea.objects.filter(noGongguCompany=gonggu_company_id, nType=2).delete()

    # 추가지역(0) 가져오기
    additional_areas = GongguArea.objects.filter(
        noGongguCompany=gonggu_company_id,
        nType=0
    ).values_list('noArea', flat=True)

    # 제외지역(1) 가져오기
    excluded_areas = GongguArea.objects.filter(
        noGongguCompany=gonggu_company_id,
        nType=1
    ).values_list('noArea', flat=True)

    # 계산된 실제할당지역 = 추가지역에서 제외지역에 의해 제외되지 않은 지역들
    result_areas = []

    for additional_area_id in additional_areas:
        try:
            additional_area = Area.objects.get(no=additional_area_id)
            is_excluded = False

            # 제외지역들과 비교
            for exclude_area_id in excluded_areas:
                try:
                    exclude_area = Area.objects.get(no=exclude_area_id)

                    # 추가지역이 제외지역에 포함되거나 같으면 제외
                    if (additional_area.no == exclude_area.no or
                        additional_area.is_contained_by(exclude_area)):
                        is_excluded = True
                        break
                except Area.DoesNotExist:
                    continue

            if not is_excluded:
                # 하위 지역들도 확인 (추가지역이 상위라면 제외되지 않은 하위지역들 포함)
                if additional_area.is_nationwide() or additional_area.is_metro_area() or additional_area.is_integrated_city():
                    descendants = additional_area.get_all_descendants()
                    for desc_area in descendants:
                        # 광역지역이나 통합시는 제외하고 오직 구나 하위지역이 없는 시군구만 포함
                        if desc_area.is_metro_area():
                            continue  # 광역지역 제외

                        is_integrated_city = ('(' not in desc_area.sCity and ')' not in desc_area.sCity and
                                            desc_area.sCity != '' and desc_area.no > 1000 and
                                            desc_area.is_integrated_city())
                        if is_integrated_city:
                            continue  # 통합시 제외

                        desc_excluded = False
                        for exclude_area_id in excluded_areas:
                            try:
                                exclude_area = Area.objects.get(no=exclude_area_id)
                                # 같은 지역이거나 실제로 상위 지역에 포함되는지 확인
                                if (desc_area.no == exclude_area.no or
                                    (exclude_area.is_metro_area() and desc_area.is_city_area() and
                                     desc_area.no > exclude_area.no and desc_area.no <= exclude_area.no + 999)):
                                    desc_excluded = True
                                    break
                            except Area.DoesNotExist:
                                continue

                        if not desc_excluded:
                            result_areas.append(desc_area.no)
                else:
                    # 광역지역이나 통합시가 아닌 일반 지역인 경우에만 추가
                    if not additional_area.is_metro_area():
                        is_integrated_city = ('(' not in additional_area.sCity and ')' not in additional_area.sCity and
                                            additional_area.sCity != '' and additional_area.no > 1000 and
                                            additional_area.is_integrated_city())
                        if not is_integrated_city:
                            result_areas.append(additional_area.no)

        except Area.DoesNotExist:
            continue

    # 중복 제거 및 최종 필터링 (하위지역이 없는 시군구지역과 구만 포함)
    result_areas = list(set(result_areas))
    filtered_areas = []

    for area_id in result_areas:
        try:
            area = Area.objects.get(no=area_id)

            # 광역지역은 완전 제외
            if area.is_metro_area():
                continue

            # 통합시는 완전 제외 (하위 구들은 이미 위에서 추가됨)
            is_integrated_city = ('(' not in area.sCity and ')' not in area.sCity and
                                area.sCity != '' and area.no > 1000 and
                                area.is_integrated_city())
            if is_integrated_city:
                continue

            # 구나 하위지역이 없는 시군구만 포함
            filtered_areas.append(area_id)

        except Area.DoesNotExist:
            # 존재하지 않는 지역은 제외
            continue

    # 최종 중복 제거
    filtered_areas = list(set(filtered_areas))

    # 실제할당지역(nType=2) 저장
    for area_id in filtered_areas:
        GongguArea.objects.create(
            noGongguCompany=gonggu_company_id,
            nType=2,
            noArea=area_id
        )

    return len(filtered_areas)


def calculate_assigned_areas(gonggu_company_id, additional_area_ids, excluded_area_ids):
    """실제할당지역 계산 및 저장"""
    from .models import GongguArea
    from area.models import Area

    # 기존 실제할당지역 삭제
    GongguArea.objects.filter(noGongguCompany=gonggu_company_id, nType=2).delete()

    # 추가지역에서 하위 시군구 지역들을 모두 찾기
    all_assigned_areas = set()

    for area_id in additional_area_ids:
        try:
            area = Area.objects.get(no=area_id)

            # 전국이면 모든 시군구 지역 추가
            if not area.sState:
                all_assigned_areas.update(
                    Area.objects.filter(
                        sState__isnull=False,
                        sCity__isnull=False
                    ).values_list('no', flat=True)
                )
            # 광역지역이면 해당 광역의 모든 시군구 지역 추가
            elif not area.sCity:
                all_assigned_areas.update(
                    Area.objects.filter(
                        sState=area.sState,
                        sCity__isnull=False
                    ).values_list('no', flat=True)
                )
            # 시군구지역이면 해당 지역만 추가
            else:
                all_assigned_areas.add(area_id)

        except Area.DoesNotExist:
            continue

    # 제외지역 제거
    for area_id in excluded_area_ids:
        all_assigned_areas.discard(area_id)

    # 실제할당지역으로 저장
    for area_id in all_assigned_areas:
        GongguArea.objects.create(
            noGongguCompany=gonggu_company_id,
            nType=2,
            noArea=area_id
        )

def add_gonggu_company(request, pk):
    """공동구매에 참여업체 추가"""
    current_staff = get_current_staff(request)

    if not current_staff or current_staff.nOrderAuthority < 2:
        return JsonResponse({'error': '참여업체 추가 권한이 없습니다.'}, status=403)

    if request.method == 'POST':
        try:
            gonggu = get_object_or_404(Gonggu, no=pk)
            data = json.loads(request.body)
            company_id = data.get('company_id')

            if not company_id:
                return JsonResponse({'error': '업체를 선택해주세요.'}, status=400)

            # 필요한 모델들 import
            from .models import GongguCompany

            # 중복 확인
            if GongguCompany.objects.filter(noGonggu=gonggu.no, noCompany=company_id).exists():
                return JsonResponse({'error': '이미 추가된 업체입니다.'}, status=400)

            # GongguCompany 생성
            gonggu_company = GongguCompany.objects.create(
                noGonggu=gonggu.no,
                noCompany=company_id
            )

            return JsonResponse({
                'success': True,
                'message': '참여업체가 추가되었습니다.',
                'gonggu_company_id': gonggu_company.no
            })

        except Exception as e:
            return JsonResponse({'error': f'업체 추가 중 오류가 발생했습니다: {str(e)}'}, status=500)

    return JsonResponse({'error': '잘못된 요청입니다.'}, status=400)