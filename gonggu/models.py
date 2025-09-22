from django.db import models
from django.utils import timezone


class Gonggu(models.Model):
    """공동구매(Gonggu) 모델"""

    # 진행구분 선택지
    STEP_TYPE_CHOICES = [
        (0, '준비중'),
        (1, '진행중'),
        (2, '일시정지'),
        (3, '마감'),
    ]

    # 구분 선택지
    TYPE_CHOICES = [
        (0, '올수리'),
        (1, '부분/기타'),
    ]

    # 기본 정보
    no = models.AutoField(primary_key=True, verbose_name='공동구매ID')
    nStepType = models.IntegerField(
        choices=STEP_TYPE_CHOICES,
        default=0,
        verbose_name='진행구분'
    )
    nType = models.IntegerField(
        choices=TYPE_CHOICES,
        default=0,
        verbose_name='구분'
    )

    # 공구 정보
    sNo = models.CharField(max_length=50, blank=True, verbose_name='공구회차')
    dateStart = models.DateField(null=True, blank=True, verbose_name='시작일')
    dateEnd = models.DateField(null=True, blank=True, verbose_name='마감일')
    sName = models.TextField(blank=True, verbose_name='공구이름')
    sPost = models.CharField(max_length=200, blank=True, verbose_name='공지글')
    sStrength = models.TextField(blank=True, verbose_name='특징')

    # 네이버 댓글 정보
    nCommentPre = models.IntegerField(default=0, verbose_name='네이버 이전 댓글수')
    nCommentNow = models.IntegerField(default=0, verbose_name='네이버 현재 댓글수')

    # 자동 생성 필드
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일시')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일시')

    class Meta:
        db_table = 'gonggu'
        verbose_name = '공동구매'
        verbose_name_plural = '공동구매'
        ordering = ['-no']  # 최신순 정렬

    def __str__(self):
        return f"공구 {self.no} - {self.sName} ({self.sNo})"

    def get_status_display_with_color(self):
        """진행구분 상태와 색상 반환"""
        status_colors = {
            0: ('준비중', 'warning'),   # 노란색
            1: ('진행중', 'success'),   # 초록색
            2: ('일시정지', 'danger'),  # 빨간색
            3: ('마감', 'secondary'),   # 회색
        }
        status, color = status_colors.get(self.nStepType, ('알 수 없음', 'secondary'))
        return {'status': status, 'color': color}

    def get_type_display_short(self):
        """구분 짧은 표시"""
        return '올수리' if self.nType == 0 else '부분/기타'

    def get_duration_days(self):
        """공구 진행 기간 일수 반환"""
        if self.dateStart and self.dateEnd:
            return (self.dateEnd - self.dateStart).days + 1
        return None

    def get_remaining_days(self):
        """마감까지 남은 일수 반환"""
        if not self.dateEnd:
            return None

        today = timezone.localtime().date()
        diff_days = (self.dateEnd - today).days

        if diff_days < 0:
            return f"마감 ({abs(diff_days)}일 지남)"
        elif diff_days == 0:
            return "마감 당일"
        else:
            return f"{diff_days}일 남음"

    def is_active(self):
        """현재 진행중인 공구인지 확인"""
        if not self.dateStart or not self.dateEnd:
            return False

        today = timezone.localtime().date()
        return (self.dateStart <= today <= self.dateEnd and
                self.nStepType == 1)  # 진행중 상태

    def is_urgent(self):
        """긴급 공구 여부 (3일 이내 마감)"""
        if not self.dateEnd or self.nStepType != 1:  # 진행중이 아니면 False
            return False

        today = timezone.localtime().date()
        diff_days = (self.dateEnd - today).days
        return 0 <= diff_days <= 3

    def get_comment_increase(self):
        """댓글 증가수 반환"""
        return max(0, self.nCommentNow - self.nCommentPre)

    def get_comment_increase_rate(self):
        """댓글 증가율 반환 (%)"""
        if self.nCommentPre == 0:
            return 100 if self.nCommentNow > 0 else 0

        increase = self.get_comment_increase()
        return round((increase / self.nCommentPre) * 100, 1)

    def get_popularity_level(self):
        """인기도 레벨 반환 (댓글 증가수 기반)"""
        increase = self.get_comment_increase()

        if increase >= 100:
            return "🔥 폭발적"
        elif increase >= 50:
            return "⭐ 높음"
        elif increase >= 20:
            return "📈 보통"
        elif increase > 0:
            return "📊 낮음"
        else:
            return "😴 관심없음"

    def get_name_preview(self):
        """공구이름 미리보기 (50자 제한)"""
        if len(self.sName) > 50:
            return self.sName[:50] + "..."
        return self.sName


class GongguCompany(models.Model):
    """공구업체(GongguCompany) 모델"""

    # 기본 정보
    no = models.AutoField(primary_key=True, verbose_name='공구업체ID')
    noGonggu = models.IntegerField(verbose_name='공동구매ID')
    noCompany = models.IntegerField(verbose_name='업체ID')

    # 자동 생성 필드
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일시')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일시')

    class Meta:
        db_table = 'gonggu_company'
        verbose_name = '공구업체'
        verbose_name_plural = '공구업체'
        ordering = ['-no']  # 최신순 정렬
        # 중복 방지: 같은 공구, 업체 조합은 하나만
        unique_together = ['noGonggu', 'noCompany']

    def __str__(self):
        return f"공구업체 {self.no} - 공구{self.noGonggu} 업체{self.noCompany}"

    def get_gonggu(self):
        """연결된 Gonggu 객체 반환"""
        try:
            return Gonggu.objects.get(no=self.noGonggu)
        except Gonggu.DoesNotExist:
            return None

    def get_company_name(self):
        """연결된 업체명 반환"""
        try:
            from company.models import Company
            company = Company.objects.get(no=self.noCompany)
            return company.sName2 or company.sName1 or f"업체{self.noCompany}"
        except:
            return f"업체{self.noCompany}"

    def get_gonggu_name(self):
        """연결된 공구명 반환"""
        gonggu = self.get_gonggu()
        if gonggu:
            return gonggu.get_name_preview()
        return f"공구{self.noGonggu}"

    def get_summary(self):
        """요약 정보 반환"""
        gonggu_name = self.get_gonggu_name()
        company_name = self.get_company_name()
        return f"{gonggu_name} - {company_name}"

    @classmethod
    def get_companies_by_gonggu(cls, gonggu_id):
        """특정 공구의 모든 참여업체 반환"""
        return cls.objects.filter(noGonggu=gonggu_id)

    @classmethod
    def get_gonggus_by_company(cls, company_id):
        """특정 업체의 모든 참여공구 반환"""
        return cls.objects.filter(noCompany=company_id)


class GongguArea(models.Model):
    """공구가능지역(GongguArea) 모델"""

    # 보관형식 선택지
    TYPE_CHOICES = [
        (0, '추가지역'),
        (1, '제외지역'),
        (2, '실제할당지역'),
    ]

    # 기본 정보
    no = models.AutoField(primary_key=True, verbose_name='공구가능지역ID')
    noGongguCompany = models.IntegerField(null=True, blank=True, verbose_name='공구업체ID')
    nType = models.IntegerField(
        choices=TYPE_CHOICES,
        default=0,
        verbose_name='보관형식'
    )
    noArea = models.IntegerField(verbose_name='지역ID')

    # 자동 생성 필드
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일시')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일시')

    class Meta:
        db_table = 'gonggu_area'
        verbose_name = '공구가능지역'
        verbose_name_plural = '공구가능지역'
        ordering = ['-no']  # 최신순 정렬
        # 중복 방지: 같은 공구업체, 지역 조합은 하나만 (임시 비활성화)
        # unique_together = ['noGongguCompany', 'noArea']

    def __str__(self):
        return f"공구지역 {self.no} - 공구업체{self.noGongguCompany} 지역{self.noArea}"

    def get_gonggu_company(self):
        """연결된 GongguCompany 객체 반환"""
        try:
            return GongguCompany.objects.get(no=self.noGongguCompany)
        except GongguCompany.DoesNotExist:
            return None

    def get_gonggu(self):
        """연결된 Gonggu 객체 반환 (GongguCompany를 통해)"""
        gonggu_company = self.get_gonggu_company()
        if gonggu_company:
            return gonggu_company.get_gonggu()
        return None

    def get_company_name(self):
        """연결된 업체명 반환 (GongguCompany를 통해)"""
        gonggu_company = self.get_gonggu_company()
        if gonggu_company:
            return gonggu_company.get_company_name()
        return "업체 정보 없음"

    def get_area_name(self):
        """연결된 지역명 반환"""
        try:
            from area.models import Area
            area = Area.objects.get(no=self.noArea)
            return area.get_full_name()
        except:
            return f"지역{self.noArea}"

    def get_gonggu_name(self):
        """연결된 공구명 반환"""
        gonggu = self.get_gonggu()
        if gonggu:
            return gonggu.get_name_preview()
        return f"공구{self.noGonggu}"

    def get_type_display_with_color(self):
        """보관형식과 색상 정보 반환"""
        type_colors = {
            0: ('추가지역', 'success'),    # 초록색
            1: ('제외지역', 'danger'),     # 빨간색
            2: ('실제할당지역', 'primary'), # 파란색
        }
        type_name, color = type_colors.get(self.nType, ('알 수 없음', 'secondary'))
        return {'type': type_name, 'color': color}

    def get_summary(self):
        """요약 정보 반환"""
        gonggu = self.get_gonggu()
        company_name = self.get_company_name()
        area_name = self.get_area_name()
        type_info = self.get_type_display_with_color()

        if gonggu:
            return f"{gonggu.get_name_preview()} - {company_name} ({area_name}) [{type_info['type']}]"
        return f"공구{self.noGonggu} - {company_name} ({area_name}) [{type_info['type']}]"

    def is_excluded_area(self):
        """제외지역인지 확인"""
        return self.nType == 1

    def is_additional_area(self):
        """추가지역인지 확인"""
        return self.nType == 0

    def is_assigned_area(self):
        """실제할당지역인지 확인"""
        return self.nType == 2

    def get_gonggu_status(self):
        """연결된 공구의 진행상태 반환"""
        gonggu = self.get_gonggu()
        if gonggu:
            return gonggu.get_status_display_with_color()
        return {'status': '공구 정보 없음', 'color': 'secondary'}

    @classmethod
    def get_areas_by_gonggu_company(cls, gonggu_company_id):
        """특정 공구업체의 모든 지역 정보 반환"""
        return cls.objects.filter(noGongguCompany=gonggu_company_id)

    @classmethod
    def get_areas_by_gonggu(cls, gonggu_id):
        """특정 공구의 모든 지역 정보 반환 (모든 참여업체 포함)"""
        # 먼저 해당 공구의 모든 공구업체를 찾고, 그 공구업체들의 지역을 반환
        gonggu_companies = GongguCompany.objects.filter(noGonggu=gonggu_id)
        gonggu_company_ids = [gc.no for gc in gonggu_companies]
        return cls.objects.filter(noGongguCompany__in=gonggu_company_ids)

    @classmethod
    def get_excluded_areas(cls, gonggu_company_id):
        """특정 공구업체의 제외지역 목록 반환"""
        return cls.objects.filter(
            noGongguCompany=gonggu_company_id,
            nType=1  # 제외지역
        )

    @classmethod
    def get_additional_areas(cls, gonggu_company_id):
        """특정 공구업체의 추가지역 목록 반환"""
        return cls.objects.filter(
            noGongguCompany=gonggu_company_id,
            nType=0  # 추가지역
        )

    @classmethod
    def get_assigned_areas(cls, gonggu_company_id):
        """특정 공구업체의 실제할당지역 목록 반환"""
        return cls.objects.filter(
            noGongguCompany=gonggu_company_id,
            nType=2  # 실제할당지역
        )
