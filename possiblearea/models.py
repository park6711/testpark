from django.db import models


class PossibleArea(models.Model):
    """공사 가능 지역 모델 (업무효율상 possi로 약칭)"""

    # 보관형식 선택지
    AREA_TYPE_CHOICES = [
        (0, '추가지역'),
        (1, '업체제외지역'),
        (2, '스텝제외지역'),
        (3, '업체요청지역'),
        (4, '실제할당지역'),
        (5, '광역가능지역'),
    ]

    # 공사종류 선택지
    CONSTRUCTION_TYPE_CHOICES = [
        (0, '올수리'),
        (1, '부분수리'),
        (2, '신축/증축'),
        (3, '부가서비스'),
    ]

    no = models.AutoField(primary_key=True, help_text="공사 가능 지역 ID")
    noCompany = models.IntegerField(help_text="업체 ID")
    nAreaType = models.IntegerField(choices=AREA_TYPE_CHOICES, help_text="보관형식")
    nConstructionType = models.IntegerField(choices=CONSTRUCTION_TYPE_CHOICES, help_text="공사종류")
    noArea = models.IntegerField(help_text="지역 ID")

    class Meta:
        db_table = 'possiblearea'
        verbose_name = '공사 가능 지역'
        verbose_name_plural = '공사 가능 지역'
        ordering = ['noCompany', 'nAreaType', 'nConstructionType']

    def __str__(self):
        return f"업체{self.noCompany} - {self.get_nAreaType_display()} - {self.get_nConstructionType_display()}"

    def get_company_name(self):
        """업체명 반환"""
        try:
            from company.models import Company
            company = Company.objects.filter(no=self.noCompany).first()
            if company:
                return company.sName2 or company.sName1 or f"업체{self.noCompany}"
            return f"업체{self.noCompany}"
        except:
            return f"업체{self.noCompany}"

    def get_area_name(self):
        """지역명 반환"""
        try:
            from area.models import Area
            area = Area.objects.filter(no=self.noArea).first()
            if area:
                return area.get_full_name()
            return f"지역{self.noArea}"
        except:
            return f"지역{self.noArea}"

    def get_full_description(self):
        """전체 설명 반환"""
        return f"{self.get_company_name()} - {self.get_area_name()} ({self.get_nAreaType_display()}, {self.get_nConstructionType_display()})"

    @classmethod
    def calculate_company_request_areas(cls, company_id, construction_type):
        """업체요청지역(3) 계산: 추가지역(0) - 업체제외지역(1)"""
        from area.models import Area

        # 추가지역(0) 가져오기
        additional_areas = cls.objects.filter(
            noCompany=company_id,
            nConstructionType=construction_type,
            nAreaType=0
        ).values_list('noArea', flat=True)

        # 업체제외지역(1) 가져오기
        company_exclude_areas = cls.objects.filter(
            noCompany=company_id,
            nConstructionType=construction_type,
            nAreaType=1
        ).values_list('noArea', flat=True)

        # 계산된 업체요청지역 = 추가지역에서 업체제외지역에 의해 제외되지 않은 지역들
        result_areas = []

        for additional_area_id in additional_areas:
            try:
                additional_area = Area.objects.get(no=additional_area_id)
                is_excluded = False

                # 업체제외지역들과 비교
                for exclude_area_id in company_exclude_areas:
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
                            for exclude_area_id in company_exclude_areas:
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

        return filtered_areas

    @classmethod
    def calculate_actual_assigned_areas(cls, company_id, construction_type):
        """실제할당지역(4) 계산: 추가지역(0) - 업체제외지역(1) - 스텝제외지역(2)"""
        from area.models import Area

        # 먼저 업체요청지역 계산
        company_request_areas = cls.calculate_company_request_areas(company_id, construction_type)

        # 스텝제외지역(2) 가져오기
        staff_exclude_areas = cls.objects.filter(
            noCompany=company_id,
            nConstructionType=construction_type,
            nAreaType=2
        ).values_list('noArea', flat=True)

        # 계산된 실제할당지역 = 업체요청지역에서 스텝제외지역에 의해 제외되지 않은 지역들
        result_areas = []

        for area_id in company_request_areas:
            try:
                area = Area.objects.get(no=area_id)
                is_excluded = False

                # 스텝제외지역들과 비교
                for exclude_area_id in staff_exclude_areas:
                    try:
                        exclude_area = Area.objects.get(no=exclude_area_id)

                        # 같은 지역이거나 실제로 상위 지역에 포함되는지 확인
                        if (area.no == exclude_area.no or
                            (exclude_area.is_metro_area() and area.is_city_area() and
                             area.no > exclude_area.no and area.no <= exclude_area.no + 999)):
                            is_excluded = True
                            break
                    except Area.DoesNotExist:
                        continue

                if not is_excluded:
                    result_areas.append(area.no)

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

        return filtered_areas

    @classmethod
    def update_calculated_areas(cls, company_id, construction_type):
        """계산된 지역들을 DB에 업데이트"""
        # 기존 계산된 지역들 삭제
        cls.objects.filter(
            noCompany=company_id,
            nConstructionType=construction_type,
            nAreaType__in=[3, 4]  # 업체요청지역(3), 실제할당지역(4)
        ).delete()

        # 업체요청지역(3) 계산 및 저장
        company_request_areas = cls.calculate_company_request_areas(company_id, construction_type)
        for area_id in company_request_areas:
            cls.objects.create(
                noCompany=company_id,
                nConstructionType=construction_type,
                nAreaType=3,  # 업체요청지역
                noArea=area_id
            )

        # 실제할당지역(4) 계산 및 저장
        actual_assigned_areas = cls.calculate_actual_assigned_areas(company_id, construction_type)
        for area_id in actual_assigned_areas:
            cls.objects.create(
                noCompany=company_id,
                nConstructionType=construction_type,
                nAreaType=4,  # 실제할당지역
                noArea=area_id
            )

        return {
            'company_request_count': len(company_request_areas),
            'actual_assigned_count': len(actual_assigned_areas)
        }