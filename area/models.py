from django.db import models


class Area(models.Model):
    """지역 모델"""
    no = models.AutoField(primary_key=True, help_text="지역 ID")
    sState = models.CharField(max_length=50, help_text="광역지역명")
    sCity = models.CharField(max_length=50, help_text="시군구지역명")

    class Meta:
        db_table = 'area'
        verbose_name = '지역'
        verbose_name_plural = '지역'
        ordering = ['no']

    def __str__(self):
        return f"{self.sState} {self.sCity}"

    def get_full_name(self):
        """전체 지역명 반환"""
        if self.no == 0:
            return "전국"
        return f"{self.sState} {self.sCity}"

    def get_display_name_with_level(self):
        """계층 레벨을 표시하는 이름 반환"""
        base_name = self.get_full_name()

        if self.is_nationwide():
            return f"🌍 {base_name} (모든 지역 포함)"
        elif self.is_metro_area():
            return f"🏛️ {base_name} (광역지역)"
        elif self.is_integrated_city():
            child_count = self.get_child_districts().count()
            return f"🏢 {base_name} ({child_count}개 구 포함)"
        elif self.is_district_area():
            return f"🏢 {base_name} (구)"
        else:
            return f"🏢 {base_name}"

    def is_nationwide(self):
        """전국 지역인지 확인"""
        return self.no == 0

    def is_metro_area(self):
        """광역지역인지 확인 (시군구명이 비어있음)"""
        return self.sCity == "" and self.no != 0

    def is_city_area(self):
        """시군구지역인지 확인"""
        return self.sCity != ""

    def is_integrated_city(self):
        """통합시 상위인지 확인 (고양시, 성남시 등)"""
        if not self.is_city_area():
            return False
        # 시군구이면서 하위 구가 있는지 확인
        return Area.objects.filter(
            no__gt=self.no,
            no__lt=self.no + 10,
            sState=self.sState
        ).exists()

    def is_district_area(self):
        """통합시 하위 구인지 확인 (덕양구, 분당구 등)"""
        if not self.is_city_area():
            return False
        # 구 이름이 포함되어 있고, 상위 통합시가 있는지 확인
        return '(' in self.sCity and ')' in self.sCity

    def get_parent_metro(self):
        """해당 시군구의 상위 광역지역 반환"""
        if self.is_city_area():
            # ID 범위로 상위 광역지역 찾기 (예: 1010 -> 1000)
            metro_id = (self.no // 1000) * 1000
            try:
                return Area.objects.get(no=metro_id)
            except Area.DoesNotExist:
                return None
        return None

    def get_parent_integrated_city(self):
        """하위 구의 상위 통합시 반환 (덕양구 -> 고양시)"""
        if self.is_district_area():
            # 하위 구의 상위 통합시 찾기 (예: 2021 -> 2020)
            integrated_city_id = (self.no // 10) * 10
            try:
                return Area.objects.get(no=integrated_city_id)
            except Area.DoesNotExist:
                return None
        return None

    def get_child_cities(self):
        """해당 광역지역의 하위 시군구들 반환"""
        if self.is_metro_area():
            start_id = self.no
            end_id = self.no + 999
            return Area.objects.filter(no__gt=start_id, no__lte=end_id).exclude(sCity="")
        return Area.objects.none()

    def get_child_districts(self):
        """해당 통합시의 하위 구들 반환"""
        if self.is_integrated_city():
            start_id = self.no
            end_id = self.no + 9
            return Area.objects.filter(no__gt=start_id, no__lte=end_id, sState=self.sState)
        return Area.objects.none()

    def get_all_descendants(self):
        """모든 하위 지역들 반환 (재귀적)"""
        descendants = []

        if self.is_nationwide():
            # 전국: 모든 지역
            descendants = list(Area.objects.exclude(no=0))
        elif self.is_metro_area():
            # 광역지역: 하위 모든 시군구 및 구
            descendants = list(self.get_child_cities())
        elif self.is_integrated_city():
            # 통합시: 하위 구들
            descendants = list(self.get_child_districts())

        return descendants

    def contains_area(self, other_area):
        """다른 지역을 포함하는지 확인"""
        if self.no == 0:  # 전국은 모든 지역 포함
            return True

        if self.is_metro_area() and other_area.is_city_area():
            # 광역지역이 시군구지역을 포함하는지 확인
            return other_area.no > self.no and other_area.no <= self.no + 999

        if self.is_integrated_city() and other_area.is_district_area():
            # 통합시가 하위 구를 포함하는지 확인
            return (other_area.no > self.no and
                   other_area.no <= self.no + 9 and
                   other_area.sState == self.sState)

        return False

    def is_contained_by(self, other_area):
        """다른 지역에 포함되는지 확인"""
        return other_area.contains_area(self)

    @classmethod
    def get_hierarchy_conflicts(cls, area_id, existing_area_ids):
        """계층 구조 충돌 검사"""
        conflicts = []
        try:
            new_area = cls.objects.get(no=area_id)
            existing_areas = cls.objects.filter(no__in=existing_area_ids)

            for existing in existing_areas:
                # 단순하고 명확한 계층 관계 확인

                # 0. 전국(0)은 모든 다른 지역과 충돌
                if new_area.no == 0 and existing.no != 0:
                    conflicts.append(f"{new_area.get_full_name()}이 {existing.get_full_name()}을 포함합니다")
                    continue
                elif existing.no == 0 and new_area.no != 0:
                    conflicts.append(f"{new_area.get_full_name()}이 {existing.get_full_name()}에 포함됩니다")
                    continue

                # 1. 광역지역(1000대)과 시군구지역 간의 관계
                new_is_metro = new_area.no % 1000 == 0 and new_area.no < 10000
                existing_is_metro = existing.no % 1000 == 0 and existing.no < 10000

                new_contains_existing_metro = (new_is_metro and not existing_is_metro and
                                             existing.no > new_area.no and existing.no < new_area.no + 1000)
                existing_contains_new_metro = (existing_is_metro and not new_is_metro and
                                             new_area.no > existing.no and new_area.no < existing.no + 1000)

                # 2. 통합시(2020)와 구(2021, 2022, 2023) 간의 관계
                new_is_parent_city = ('(' not in new_area.sCity and ')' not in new_area.sCity and
                                    new_area.sCity != '' and new_area.no > 1000)
                existing_is_parent_city = ('(' not in existing.sCity and ')' not in existing.sCity and
                                         existing.sCity != '' and existing.no > 1000)

                new_contains_existing_city = (new_is_parent_city and not existing_is_parent_city and
                                            existing.no > new_area.no and existing.no <= new_area.no + 9 and
                                            existing.sState == new_area.sState)
                existing_contains_new_city = (existing_is_parent_city and not new_is_parent_city and
                                            new_area.no > existing.no and new_area.no <= existing.no + 9 and
                                            new_area.sState == existing.sState)

                if new_contains_existing_metro or new_contains_existing_city:
                    conflicts.append(f"{new_area.get_full_name()}이 {existing.get_full_name()}을 포함합니다")
                elif existing_contains_new_metro or existing_contains_new_city:
                    conflicts.append(f"{new_area.get_full_name()}이 {existing.get_full_name()}에 포함됩니다")

        except cls.DoesNotExist:
            pass

        return conflicts

    def get_hierarchy_level(self):
        """계층 레벨 반환 (0: 전국, 1: 광역, 2: 시군구, 3: 구)"""
        if self.is_nationwide():
            return 0
        elif self.is_metro_area():
            return 1
        elif self.is_district_area():
            return 3
        elif self.is_city_area():
            return 2
        return -1

    def get_hierarchy_path(self):
        """계층 경로 반환 [전국, 광역, 시군구, 구]"""
        path = []

        if self.is_district_area():
            # 구 -> 통합시 -> 광역 -> 전국
            path.append(self)
            integrated_city = self.get_parent_integrated_city()
            if integrated_city:
                path.append(integrated_city)
            metro = self.get_parent_metro()
            if metro:
                path.append(metro)
        elif self.is_integrated_city():
            # 통합시 -> 광역 -> 전국
            path.append(self)
            metro = self.get_parent_metro()
            if metro:
                path.append(metro)
        elif self.is_city_area():
            # 일반 시군구 -> 광역 -> 전국
            path.append(self)
            metro = self.get_parent_metro()
            if metro:
                path.append(metro)
        elif self.is_metro_area():
            # 광역 -> 전국
            path.append(self)
        elif self.is_nationwide():
            # 전국
            path.append(self)

        # 전국 추가 (맨 마지막에)
        if not self.is_nationwide():
            try:
                nationwide = Area.objects.get(no=0)
                path.append(nationwide)
            except Area.DoesNotExist:
                pass

        return list(reversed(path))  # 전국부터 시작하도록 역순