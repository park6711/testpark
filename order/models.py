from django.db import models
from django.utils import timezone


class Order(models.Model):
    """의뢰(Order) 모델"""

    # 기본 정보
    no = models.AutoField(primary_key=True, verbose_name='의뢰ID')
    time = models.DateTimeField(auto_now_add=True, verbose_name='타임스탬프')

    # 업체 및 고객 정보
    sAppoint = models.CharField(max_length=100, blank=True, verbose_name='업체공구지정')
    sNick = models.CharField(max_length=50, blank=True, verbose_name='별명')
    sNaverID = models.CharField(max_length=50, blank=True, verbose_name='네이버 ID')
    sName = models.CharField(max_length=50, blank=True, verbose_name='성명')
    sPhone = models.CharField(max_length=20, blank=True, verbose_name='고객 핸드폰')

    # 의뢰 내용
    sPost = models.CharField(max_length=200, blank=True, verbose_name='의뢰게시글')
    sArea = models.TextField(blank=True, verbose_name='공사지역')
    dateSchedule = models.DateField(null=True, blank=True, verbose_name='공사예정일')
    sConstruction = models.TextField(blank=True, verbose_name='공사내용')

    # 동의 사항
    bPrivacy1 = models.BooleanField(default=False, verbose_name='개인정보 동의')
    bPrivacy2 = models.BooleanField(default=False, verbose_name='3자제공 동의')

    # 자동 생성 필드
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일시')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일시')

    class Meta:
        db_table = 'order'
        verbose_name = '의뢰'
        verbose_name_plural = '의뢰'
        ordering = ['-no']  # 최신순 정렬

    def __str__(self):
        return f"의뢰 {self.no} - {self.sName} ({self.sArea})"

    def get_privacy_status(self):
        """개인정보 동의 상태 반환"""
        if self.bPrivacy1 and self.bPrivacy2:
            return "전체 동의"
        elif self.bPrivacy1:
            return "개인정보만 동의"
        elif self.bPrivacy2:
            return "3자제공만 동의"
        else:
            return "미동의"

    def get_schedule_status(self):
        """공사예정일 상태 반환"""
        if not self.dateSchedule:
            return "미정"

        today = timezone.localtime().date()
        diff_days = (self.dateSchedule - today).days

        if diff_days < 0:
            return f"지난 일정 ({abs(diff_days)}일 전)"
        elif diff_days == 0:
            return "오늘"
        elif diff_days <= 7:
            return f"{diff_days}일 후"
        else:
            return f"{diff_days}일 후"

    def is_urgent(self):
        """긴급 의뢰 여부 (3일 이내 공사예정)"""
        if not self.dateSchedule:
            return False

        today = timezone.localtime().date()
        diff_days = (self.dateSchedule - today).days
        return 0 <= diff_days <= 3


class Assign(models.Model):
    """할당(Assign) 모델"""

    # 공사종류 선택지
    CONSTRUCTION_TYPE_CHOICES = [
        (0, '아파트 올수리'),
        (1, '아파트 부분수리'),
        (2, '주택 올수리'),
        (3, '주택 부분수리'),
        (4, '상가 올수리'),
        (5, '상가 부분수리'),
        (6, '신축/증축'),
        (7, '부가서비스'),
    ]

    # 할당상태 선택지
    ASSIGN_TYPE_CHOICES = [
        (0, '대기중'),
        (1, '할당'),
        (2, '반려'),
        (3, '취소'),
        (4, '제외'),
        (5, '업체미비'),
        (6, '중복접수'),
        (7, '가능문의'),
        (8, '불가능답변'),
    ]

    # 지정종류 선택지
    APPOINT_TYPE_CHOICES = [
        (0, '지정없음'),
        (1, '업체지정'),
        (2, '공구지정'),
    ]

    # 기본 정보
    no = models.AutoField(primary_key=True, verbose_name='할당ID')
    noOrder = models.IntegerField(verbose_name='의뢰ID')
    time = models.DateTimeField(auto_now_add=True, verbose_name='타임스탬프')
    noCompany = models.IntegerField(verbose_name='업체ID')

    # 공사 및 할당 정보
    nConstructionType = models.IntegerField(
        choices=CONSTRUCTION_TYPE_CHOICES,
        default=0,
        verbose_name='공사종류'
    )
    nAssignType = models.IntegerField(
        choices=ASSIGN_TYPE_CHOICES,
        default=0,
        verbose_name='할당상태'
    )

    # 연락처 및 메시지
    sCompanyPhone = models.CharField(max_length=20, blank=True, verbose_name='업체폰번호')
    sCompanySMS = models.TextField(blank=True, verbose_name='업체 문자멘트')
    sClientPhone = models.CharField(max_length=20, blank=True, verbose_name='고객폰번호')
    sClientSMS = models.TextField(blank=True, verbose_name='고객문자멘트')

    # 관리 정보
    sWorker = models.CharField(max_length=50, blank=True, verbose_name='작업자')
    noCompanyReport = models.IntegerField(null=True, blank=True, verbose_name='업체계약보고ID')

    # 지정 및 지역 정보
    nAppoint = models.IntegerField(
        choices=APPOINT_TYPE_CHOICES,
        default=0,
        verbose_name='지정종류'
    )
    noGonggu = models.IntegerField(null=True, blank=True, verbose_name='공구ID')
    noArea = models.IntegerField(null=True, blank=True, verbose_name='지역ID')

    # 자동 생성 필드
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일시')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일시')

    class Meta:
        db_table = 'assign'
        verbose_name = '할당'
        verbose_name_plural = '할당'
        ordering = ['-no']  # 최신순 정렬

    def __str__(self):
        return f"할당 {self.no} - 의뢰{self.noOrder} → 업체{self.noCompany}"

    def get_order(self):
        """연결된 Order 객체 반환"""
        try:
            return Order.objects.get(no=self.noOrder)
        except Order.DoesNotExist:
            return None

    def get_company_name(self):
        """연결된 업체명 반환"""
        try:
            from company.models import Company
            company = Company.objects.get(no=self.noCompany)
            return company.sCompanyName or f"업체{self.noCompany}"
        except:
            return f"업체{self.noCompany}"

    def get_area_name(self):
        """연결된 지역명 반환"""
        if not self.noArea:
            return "지역 미지정"
        try:
            from area.models import Area
            area = Area.objects.get(no=self.noArea)
            return area.sArea
        except:
            return f"지역{self.noArea}"

    def is_active_assign(self):
        """활성 할당 여부 (할당 상태가 '할당'인 경우)"""
        return self.nAssignType == 1

    def get_construction_display_short(self):
        """공사종류 짧은 표시"""
        type_map = {
            0: '아파트(올)', 1: '아파트(부분)', 2: '주택(올)', 3: '주택(부분)',
            4: '상가(올)', 5: '상가(부분)', 6: '신축/증축', 7: '부가서비스'
        }
        return type_map.get(self.nConstructionType, '기타')

    def get_status_color(self):
        """할당상태별 색상 반환 (UI용)"""
        color_map = {
            0: 'warning',  # 대기중 - 노란색
            1: 'success',  # 할당 - 초록색
            2: 'danger',   # 반려 - 빨간색
            3: 'secondary', # 취소 - 회색
            4: 'dark',     # 제외 - 검은색
            5: 'info',     # 업체미비 - 파란색
            6: 'warning',  # 중복접수 - 노란색
            7: 'primary',  # 가능문의 - 파란색
            8: 'secondary' # 불가능답변 - 회색
        }
        return color_map.get(self.nAssignType, 'secondary')


class Estimate(models.Model):
    """할당견적(Estimate) 모델"""

    # 기본 정보
    no = models.AutoField(primary_key=True, verbose_name='할당견적ID')
    noOrder = models.IntegerField(verbose_name='의뢰ID')
    noAssign = models.IntegerField(verbose_name='할당ID')
    time = models.DateTimeField(auto_now_add=True, verbose_name='타임스탬프')

    # 견적 내용
    sPost = models.CharField(max_length=200, blank=True, verbose_name='견적서 게시글')

    # 자동 생성 필드
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일시')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일시')

    class Meta:
        db_table = 'estimate'
        verbose_name = '할당견적'
        verbose_name_plural = '할당견적'
        ordering = ['-no']  # 최신순 정렬

    def __str__(self):
        return f"견적 {self.no} - 의뢰{self.noOrder} (할당{self.noAssign})"

    def get_order(self):
        """연결된 Order 객체 반환"""
        try:
            return Order.objects.get(no=self.noOrder)
        except Order.DoesNotExist:
            return None

    def get_assign(self):
        """연결된 Assign 객체 반환"""
        try:
            return Assign.objects.get(no=self.noAssign)
        except Assign.DoesNotExist:
            return None

    def get_company_name(self):
        """연결된 업체명 반환 (Assign을 통해)"""
        assign = self.get_assign()
        if assign:
            return assign.get_company_name()
        return "업체 정보 없음"

    def get_client_name(self):
        """연결된 고객명 반환 (Order를 통해)"""
        order = self.get_order()
        if order:
            return order.sName or "고객명 없음"
        return "고객 정보 없음"

    def get_construction_type(self):
        """공사종류 반환 (Assign을 통해)"""
        assign = self.get_assign()
        if assign:
            return assign.get_nConstructionType_display()
        return "공사종류 없음"

    def get_summary(self):
        """견적 요약 정보 반환"""
        order = self.get_order()
        assign = self.get_assign()

        if order and assign:
            return f"{order.sName} - {assign.get_construction_display_short()} ({order.sArea})"
        return "정보 불완전"

    def is_recent(self):
        """최근 견적 여부 (1일 이내)"""
        from datetime import timedelta
        return (timezone.now() - self.time) <= timedelta(days=1)


class AssignMemo(models.Model):
    """할당메모(AssignMemo) 모델"""

    # 기본 정보
    no = models.AutoField(primary_key=True, verbose_name='할당메모ID')
    noOrder = models.IntegerField(verbose_name='의뢰ID')
    noAssign = models.IntegerField(verbose_name='할당ID')
    time = models.DateTimeField(auto_now_add=True, verbose_name='타임스탬프')

    # 메모 내용
    sWorker = models.CharField(max_length=50, blank=True, verbose_name='작업자')
    sMemo = models.TextField(blank=True, verbose_name='메모')

    # 자동 생성 필드
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일시')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일시')

    class Meta:
        db_table = 'assign_memo'
        verbose_name = '할당메모'
        verbose_name_plural = '할당메모'
        ordering = ['-no']  # 최신순 정렬

    def __str__(self):
        return f"메모 {self.no} - 의뢰{self.noOrder} (할당{self.noAssign}) by {self.sWorker}"

    def get_order(self):
        """연결된 Order 객체 반환"""
        try:
            return Order.objects.get(no=self.noOrder)
        except Order.DoesNotExist:
            return None

    def get_assign(self):
        """연결된 Assign 객체 반환"""
        try:
            return Assign.objects.get(no=self.noAssign)
        except Assign.DoesNotExist:
            return None

    def get_company_name(self):
        """연결된 업체명 반환 (Assign을 통해)"""
        assign = self.get_assign()
        if assign:
            return assign.get_company_name()
        return "업체 정보 없음"

    def get_client_name(self):
        """연결된 고객명 반환 (Order를 통해)"""
        order = self.get_order()
        if order:
            return order.sName or "고객명 없음"
        return "고객 정보 없음"

    def get_memo_preview(self):
        """메모 미리보기 (50자 제한)"""
        if len(self.sMemo) > 50:
            return self.sMemo[:50] + "..."
        return self.sMemo

    def get_assign_status(self):
        """할당 상태 반환 (Assign을 통해)"""
        assign = self.get_assign()
        if assign:
            return assign.get_nAssignType_display()
        return "할당 정보 없음"

    def get_summary(self):
        """메모 요약 정보 반환"""
        order = self.get_order()
        assign = self.get_assign()

        if order and assign:
            return f"{order.sName} - {assign.get_construction_display_short()} ({self.sWorker})"
        return "정보 불완전"

    def is_recent(self):
        """최근 메모 여부 (1일 이내)"""
        from datetime import timedelta
        return (timezone.now() - self.time) <= timedelta(days=1)

    def is_important(self):
        """중요 메모 여부 (메모에 '중요', '긴급', '주의' 키워드 포함)"""
        important_keywords = ['중요', '긴급', '주의', '문제', '이슈']
        return any(keyword in self.sMemo for keyword in important_keywords)
