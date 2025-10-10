from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import Q
from .models import Gonggu, GongguArea
from company.models import Company
from staff.views import get_current_staff
import json

def gonggu_list(request):
    """공동구매 리스트 - Staff 전용"""
    # Staff 로그인 확인
    if 'staff_user' not in request.session:
        messages.error(request, '스태프 로그인이 필요합니다.')
        return redirect('/auth/login/?next=/gonggu/')

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
                unique_area_names = sorted(set(area_names))
                if len(unique_area_names) > 1:
                    areas_text = f"{unique_area_names[0]}~({len(unique_area_names)})"
                    areas_tooltip = ', '.join(unique_area_names)
                elif len(unique_area_names) == 1:
                    areas_text = unique_area_names[0]
                    areas_tooltip = unique_area_names[0]
                else:
                    areas_text = '-'
                    areas_tooltip = ''

                # 특징 정보 포매팅 (20자 제한)
                strength_full = gonggu.sStrength or ''
                if len(strength_full) > 20:
                    strength_text = strength_full[:20]
                    strength_tooltip = strength_full
                else:
                    strength_text = strength_full
                    strength_tooltip = strength_full

                gonggu_data.append({
                    'gonggu': gonggu,
                    'company': company_name,
                    'areas': areas_text,
                    'areas_tooltip': areas_tooltip,
                    'strength': strength_text,
                    'strength_tooltip': strength_tooltip,
                    'gonggu_company_id': gonggu_company.no
                })
        else:
            # 참여업체가 없는 경우 공구만 표시
            # 특징 정보 포매팅 (20자 제한)
            strength_full = gonggu.sStrength or ''
            if len(strength_full) > 20:
                strength_text = strength_full[:20]
                strength_tooltip = strength_full
            else:
                strength_text = strength_full
                strength_tooltip = strength_full

            gonggu_data.append({
                'gonggu': gonggu,
                'company': '-',
                'areas': '-',
                'areas_tooltip': '',
                'strength': strength_text,
                'strength_tooltip': strength_tooltip,
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
            return redirect(f'/gonggu/{gonggu.no}/?edit=1')
        except Exception as e:
            messages.error(request, f'공동구매 생성 중 오류가 발생했습니다: {str(e)}')

    return render(request, 'gonggu/gonggu_form.html', {
        'current_staff': current_staff,
        'form_type': 'create'
    })

def gonggu_detail(request, pk):
    """공동구매 상세보기/수정 - Staff 전용"""
    # Staff 로그인 확인
    if 'staff_user' not in request.session:
        messages.error(request, '스태프 로그인이 필요합니다.')
        return redirect('/auth/login/?next=/gonggu/')

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

            # AJAX 요청인 경우 JSON 응답 반환
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': '자동 저장되었습니다.'})

            messages.success(request, '공동구매가 수정되었습니다.')
            return redirect('gonggu:gonggu_detail', pk=gonggu.no)
        except Exception as e:
            # AJAX 요청인 경우 JSON 응답 반환
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': f'저장 중 오류가 발생했습니다: {str(e)}'})

            messages.error(request, f'공동구매 수정 중 오류가 발생했습니다: {str(e)}')

    # 관련 업체 및 지역 정보
    from .models import GongguCompany, GongguArea
    gonggu_companies = GongguCompany.objects.filter(noGonggu=gonggu.no)

    # 모든 관련 지역 정보 (모든 참여업체의 지역)
    gonggu_company_ids = [gc.no for gc in gonggu_companies]
    areas = GongguArea.objects.filter(noGongguCompany__in=gonggu_company_ids)

    # 각 참여업체별 실제할당지역 개수 계산 및 객체에 추가
    for gc in gonggu_companies:
        assigned_count = GongguArea.objects.filter(noGongguCompany=gc.no, nType=2).count()
        gc.area_count = assigned_count

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
            from .models import GongguCompany, GongguArea

            gonggu = get_object_or_404(Gonggu, no=pk)

            # 쿼리 파라미터에서 특정 GongguCompany ID 확인
            gonggu_company_id = request.GET.get('gonggu_company_id')

            # 해당 공구와 연결된 GongguCompany 개수 확인
            gonggu_companies = GongguCompany.objects.filter(noGonggu=gonggu.no)
            company_count = gonggu_companies.count()

            if company_count > 1:
                # 여러 개의 GongguCompany가 있으면: 특정 GongguCompany만 삭제
                if gonggu_company_id:
                    try:
                        target_company = GongguCompany.objects.get(no=gonggu_company_id, noGonggu=gonggu.no)
                        # 해당 GongguCompany를 참조하는 모든 GongguArea 삭제
                        GongguArea.objects.filter(noGongguCompany=target_company.no).delete()
                        target_company.delete()
                        return JsonResponse({'success': True, 'message': '참여업체가 삭제되었습니다.'})
                    except GongguCompany.DoesNotExist:
                        return JsonResponse({'error': '해당 참여업체를 찾을 수 없습니다.'}, status=404)
                else:
                    return JsonResponse({'error': '삭제할 참여업체가 지정되지 않았습니다.'}, status=400)
            elif company_count == 1:
                # 1개의 GongguCompany가 있으면: GongguCompany, 관련 GongguArea, Gonggu 모두 삭제
                for company in gonggu_companies:
                    # 해당 GongguCompany를 참조하는 모든 GongguArea 삭제
                    GongguArea.objects.filter(noGongguCompany=company.no).delete()
                gonggu_companies.delete()
                gonggu.delete()
                return JsonResponse({'success': True, 'message': '공동구매와 참여업체가 삭제되었습니다.'})
            else:
                # GongguCompany가 없으면: Gonggu만 삭제
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
    """공동구매 가능 지역 관리 - Staff 전용"""
    # Staff 로그인 확인
    if 'staff_user' not in request.session:
        messages.error(request, '스태프 로그인이 필요합니다.')
        return redirect('/auth/login/?next=/gonggu/')

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
                    # 직접 매치가 안되는 경우, 통합시 확장된 하위 구일 수 있음
                    if area_type == 1:  # 제외지역인 경우만
                        # 통합시 역매핑 (하위 구 -> 통합시 본체)
                        integrated_city_reverse_mapping = {
                            2021: 2020, 2022: 2020, 2023: 2020,  # 덕양구, 일산동구, 일산서구 -> 고양시
                            2121: 2120, 2122: 2120, 2123: 2120,  # 분당구, 수정구, 중원구 -> 성남시
                            2171: 2170, 2172: 2170,              # 동안구, 만안구 -> 안양시
                            2151: 2150, 2152: 2150,              # 단원구, 상록구 -> 안산시
                            2131: 2130, 2132: 2130, 2133: 2130, 2134: 2130,  # 권선구, 영통구, 장안구, 팔달구 -> 수원시
                            2231: 2230, 2232: 2230, 2233: 2230,  # 기흥구, 수지구, 처인구 -> 용인시
                            5131: 5130, 5132: 5130, 5133: 5130, 5134: 5130, 5135: 5130  # 창원시 하위 구들 -> 창원시
                        }

                        # 통합시 매핑
                        integrated_city_mapping = {
                            2020: [2021, 2022, 2023],  # 고양시 -> [덕양구, 일산동구, 일산서구]
                            2120: [2121, 2122, 2123],  # 성남시 -> [분당구, 수정구, 중원구]
                            2170: [2171, 2172],        # 안양시 -> [동안구, 만안구]
                            2150: [2151, 2152],        # 안산시 -> [단원구, 상록구]
                            2130: [2131, 2132, 2133, 2134],  # 수원시 -> [권선구, 영통구, 장안구, 팔달구]
                            2230: [2231, 2232, 2233],  # 용인시 -> [기흥구, 수지구, 처인구]
                            5130: [5131, 5132, 5133, 5134, 5135]  # 창원시 -> [마산합포구, 마산회원구, 성산구, 의창구, 진해구]
                        }

                        parent_city_id = integrated_city_reverse_mapping.get(area_id)
                        if parent_city_id:
                            try:
                                # 통합시 본체 레코드 확인
                                gonggu_area = GongguArea.objects.get(
                                    noGongguCompany=gonggu_company_id,
                                    nType=area_type,
                                    noArea=parent_city_id
                                )

                                # 통합시의 하위 구 목록에서 현재 삭제하려는 구를 제외한 나머지 구들을 개별 등록
                                remaining_sub_areas = [sub for sub in integrated_city_mapping[parent_city_id] if sub != area_id]

                                # 기존 통합시 레코드 삭제
                                gonggu_area.delete()

                                # 나머지 하위 구들을 개별적으로 추가
                                for sub_area_id in remaining_sub_areas:
                                    GongguArea.objects.create(
                                        noGongguCompany=gonggu_company_id,
                                        nType=area_type,
                                        noArea=sub_area_id
                                    )

                                # 실제할당지역 자동 계산
                                calculate_assigned_areas_auto(gonggu_company_id)

                                return JsonResponse({'success': True, 'message': '삭제되었습니다.'})

                            except GongguArea.DoesNotExist:
                                pass

                    return JsonResponse({'success': False, 'error': '존재하지 않는 데이터입니다.'})

            return JsonResponse({'success': False, 'error': '잘못된 요청입니다.'})

        except Exception as e:
            return JsonResponse({'error': f'처리 중 오류가 발생했습니다: {str(e)}'}, status=500)

    # GET 요청 - 지역 관리 페이지 표시
    # 모든 지역 가져오기 (추가지역용) - 특정 순서로 정렬
    # 1. 전국 (no=0)
    nationwide = Area.objects.filter(no=0)

    # 2. 광역지역 - 요청된 순서대로
    metropolitan_order = [1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000, 10000, 12000, 13000, 14000, 15000, 16000]
    # 서울, 경기, 인천, 부산, 경남, 울산, 대구, 경북, 대전, 충남, 광주광역시, 전남, 전북, 강원, 제주
    metropolitan_areas = []
    for area_no in metropolitan_order:
        try:
            area = Area.objects.get(no=area_no)
            metropolitan_areas.append(area)
        except Area.DoesNotExist:
            pass

    # 3. 나머지 시군구지역 (no 순서대로)
    city_areas = Area.objects.exclude(no=0).exclude(no__in=metropolitan_order).order_by('no')

    # 전체 리스트 조합
    all_areas = list(nationwide) + metropolitan_areas + list(city_areas)

    # 제외지역용 필터링된 지역 (전국, 광역지역만 제외)
    # 제외할 지역 목록: 전국과 광역지역만
    exclude_ids = [0]  # 전국

    # 광역지역 제외 (서울, 경기, 인천, 부산, 경남, 울산, 대구, 경북, 대전, 충남, 충북, 광주광역시, 전남, 전북, 강원, 제주)
    metropolitan_ids = [1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000, 10000, 11000, 12000, 13000, 14000, 15000, 16000]
    exclude_ids.extend(metropolitan_ids)

    # 모든 시군구지역만 필터링, Area.no 올림차순 정렬
    # (통합시 본체, 통합시 하위 구, 일반 시군구 모두 포함)
    filtered_areas = Area.objects.exclude(no__in=exclude_ids).order_by('no')

    # 현재 저장된 지역들 (추가된 순서대로 표시)
    additional_areas = GongguArea.objects.filter(noGongguCompany=gonggu_company_id, nType=0).order_by('no')
    excluded_areas_raw = GongguArea.objects.filter(noGongguCompany=gonggu_company_id, nType=1).order_by('no')
    assigned_areas = GongguArea.objects.filter(noGongguCompany=gonggu_company_id, nType=2).order_by('noArea')  # 지역 ID 올림차순

    # 제외지역에서 통합시를 하위 구들로 확장하여 표시
    excluded_areas_expanded = []
    integrated_city_mapping = {
        2020: [2021, 2022, 2023],  # 고양시 -> [덕양구, 일산동구, 일산서구]
        2120: [2121, 2122, 2123],  # 성남시 -> [분당구, 수정구, 중원구]
        2170: [2171, 2172],        # 안양시 -> [동안구, 만안구]
        2150: [2151, 2152],        # 안산시 -> [단원구, 상록구]
        2130: [2131, 2132, 2133, 2134],  # 수원시 -> [권선구, 영통구, 장안구, 팔달구]
        2230: [2231, 2232, 2233],  # 용인시 -> [기흥구, 수지구, 처인구]
        5130: [5131, 5132, 5133, 5134, 5135]  # 창원시 -> [마산합포구, 마산회원구, 성산구, 의창구, 진해구]
    }

    for excluded_area in excluded_areas_raw:
        area_id = excluded_area.noArea
        if area_id in integrated_city_mapping:
            # 통합시인 경우 하위 구들로 확장
            for sub_area_id in integrated_city_mapping[area_id]:
                try:
                    sub_area = Area.objects.get(no=sub_area_id)
                    # 가짜 GongguArea 객체 생성 (표시용)
                    class FakeGongguArea:
                        def __init__(self, area_id, area_name):
                            self.noArea = area_id
                            self.nType = 1
                            self._area_name = area_name

                        def get_area_name(self):
                            return self._area_name

                    fake_gonggu_area = FakeGongguArea(sub_area_id, sub_area.get_full_name())
                    excluded_areas_expanded.append(fake_gonggu_area)
                except Area.DoesNotExist:
                    pass
        else:
            # 일반 지역인 경우 그대로 추가
            excluded_areas_expanded.append(excluded_area)

    excluded_areas = excluded_areas_expanded

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
    """실제할당지역 자동 계산 및 저장 - 새로운 로직"""
    from .models import GongguArea
    from area.models import Area

    # 기존 실제할당지역 삭제
    GongguArea.objects.filter(noGongguCompany=gonggu_company_id, nType=2).delete()

    # 추가지역(0) 가져오기
    additional_area_ids = list(GongguArea.objects.filter(
        noGongguCompany=gonggu_company_id,
        nType=0
    ).values_list('noArea', flat=True))

    # 제외지역(1) 가져오기
    excluded_area_ids = list(GongguArea.objects.filter(
        noGongguCompany=gonggu_company_id,
        nType=1
    ).values_list('noArea', flat=True))

    # 1단계: 추가지역을 하위 시군구지역으로 확장
    expanded_additional_areas = set()

    # 통합시 매핑
    integrated_city_mapping = {
        2020: [2021, 2022, 2023],  # 고양시 -> [덕양구, 일산동구, 일산서구]
        2120: [2121, 2122, 2123],  # 성남시 -> [분당구, 수정구, 중원구]
        2170: [2171, 2172],        # 안양시 -> [동안구, 만안구]
        2150: [2151, 2152],        # 안산시 -> [단원구, 상록구]
        2130: [2131, 2132, 2133, 2134],  # 수원시 -> [권선구, 영통구, 장안구, 팔달구]
        2230: [2231, 2232, 2233],  # 용인시 -> [기흥구, 수지구, 처인구]
        5130: [5131, 5132, 5133, 5134, 5135]  # 창원시 -> [마산합포구, 마산회원구, 성산구, 의창구, 진해구]
    }

    # 광역지역 매핑
    metropolitan_areas = [1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000, 10000, 11000, 12000, 13000, 14000, 15000, 16000]

    for area_id in additional_area_ids:
        if area_id == 0:
            # 전국: 전국과 광역지역을 제외한 모든 시군구지역
            all_areas = Area.objects.exclude(no__in=[0] + metropolitan_areas).order_by('no')
            for area in all_areas:
                # 통합시 본체는 하위 구들로 확장
                if area.no in integrated_city_mapping:
                    expanded_additional_areas.update(integrated_city_mapping[area.no])
                else:
                    expanded_additional_areas.add(area.no)
        elif area_id in metropolitan_areas:
            # 광역지역: 해당 광역지역 하위의 모든 시군구지역
            metro_areas = Area.objects.filter(no__gt=area_id, no__lt=area_id+1000).order_by('no')
            for area in metro_areas:
                # 통합시 본체는 하위 구들로 확장
                if area.no in integrated_city_mapping:
                    expanded_additional_areas.update(integrated_city_mapping[area.no])
                else:
                    expanded_additional_areas.add(area.no)
        elif area_id in integrated_city_mapping:
            # 통합시: 하위 구들로 확장
            expanded_additional_areas.update(integrated_city_mapping[area_id])
        else:
            # 일반 시군구지역: 그대로 추가
            expanded_additional_areas.add(area_id)

    # 2단계: 제외지역을 하위 시군구지역으로 확장
    expanded_excluded_areas = set()

    for area_id in excluded_area_ids:
        if area_id == 0:
            # 전국: 전국과 광역지역을 제외한 모든 시군구지역
            all_areas = Area.objects.exclude(no__in=[0] + metropolitan_areas).order_by('no')
            for area in all_areas:
                # 통합시 본체는 하위 구들로 확장
                if area.no in integrated_city_mapping:
                    expanded_excluded_areas.update(integrated_city_mapping[area.no])
                else:
                    expanded_excluded_areas.add(area.no)
        elif area_id in metropolitan_areas:
            # 광역지역: 해당 광역지역 하위의 모든 시군구지역
            metro_areas = Area.objects.filter(no__gt=area_id, no__lt=area_id+1000).order_by('no')
            for area in metro_areas:
                # 통합시 본체는 하위 구들로 확장
                if area.no in integrated_city_mapping:
                    expanded_excluded_areas.update(integrated_city_mapping[area.no])
                else:
                    expanded_excluded_areas.add(area.no)
        elif area_id in integrated_city_mapping:
            # 통합시: 하위 구들로 확장
            expanded_excluded_areas.update(integrated_city_mapping[area_id])
        else:
            # 일반 시군구지역: 그대로 추가
            expanded_excluded_areas.add(area_id)

    # 3단계: 실제할당지역 = 확장된 추가지역 - 확장된 제외지역
    final_assigned_areas = expanded_additional_areas - expanded_excluded_areas

    # 4단계: 실제할당지역(nType=2) 저장
    for area_id in final_assigned_areas:
        try:
            # 해당 지역이 실제로 존재하는지 확인
            Area.objects.get(no=area_id)
            GongguArea.objects.create(
                noGongguCompany=gonggu_company_id,
                nType=2,
                noArea=area_id
            )
        except Area.DoesNotExist:
            # 존재하지 않는 지역은 건너뛰기
            continue

    return len(final_assigned_areas)


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


def remove_gonggu_company(request, gonggu_company_id):
    """공동구매 참여업체 제거"""
    current_staff = get_current_staff(request)

    if not current_staff or current_staff.nOrderAuthority < 2:
        return JsonResponse({'error': '참여업체 제거 권한이 없습니다.'}, status=403)

    if request.method == 'POST':
        try:
            # 필요한 모델들 import
            from .models import GongguCompany, GongguArea

            # GongguCompany 조회
            gonggu_company = get_object_or_404(GongguCompany, no=gonggu_company_id)

            # 관련된 모든 GongguArea 삭제 (추가지역, 제외지역, 실제할당지역)
            GongguArea.objects.filter(noGongguCompany=gonggu_company_id).delete()

            # GongguCompany 삭제
            gonggu_company.delete()

            return JsonResponse({
                'success': True,
                'message': '참여업체가 제거되었습니다.'
            })

        except Exception as e:
            return JsonResponse({'error': f'업체 제거 중 오류가 발생했습니다: {str(e)}'}, status=500)

    return JsonResponse({'error': '잘못된 요청입니다.'}, status=400)