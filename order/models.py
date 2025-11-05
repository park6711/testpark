from django.db import models
from django.utils import timezone
import uuid


class Order(models.Model):
    """의뢰(Order) 모델"""

    DESIGNATION_TYPE_CHOICES = [
        ('지정없음', '지정없음'),
        ('업체지정', '업체지정'),
        ('공동구매', '공동구매'),
    ]

    STATUS_CHOICES = [
        ('대기중', '대기중'),
        ('할당', '할당'),
        ('반려', '반려'),
        ('취소', '취소'),
        ('제외', '제외'),
        ('업체미비', '업체미비'),
        ('중복접수', '중복접수'),
        ('연락처오류', '연락처오류'),
        ('가능문의', '가능문의'),
        ('불가능답변(X)', '불가능답변(X)'),
        ('고객문의', '고객문의'),
        ('계약', '계약'),
    ]

    # 기본 정보
    no = models.AutoField(primary_key=True, verbose_name='의뢰ID')
    time = models.DateTimeField(auto_now_add=True, verbose_name='접수일시')
    google_sheet_uuid = models.CharField(max_length=50, blank=True, unique=True, null=True, verbose_name='구글 시트 UUID')

    # 지정 정보
    designation = models.CharField(max_length=200, blank=True, default='', verbose_name='지정')
    designation_type = models.CharField(max_length=20, choices=DESIGNATION_TYPE_CHOICES, default='지정없음', verbose_name='지정타입')

    # 업체 및 고객 정보
    sAppoint = models.CharField(max_length=100, blank=True, verbose_name='업체공구지정')  # Legacy
    sNick = models.CharField(max_length=50, blank=True, verbose_name='별명')
    sNaverID = models.CharField(max_length=50, blank=True, verbose_name='네이버 ID')
    sName = models.CharField(max_length=50, blank=True, verbose_name='성명')
    sPhone = models.CharField(max_length=20, blank=True, verbose_name='고객 핸드폰')

    # 의뢰 내용
    sPost = models.CharField(max_length=200, blank=True, verbose_name='의뢰게시글')
    post_link = models.URLField(max_length=500, blank=True, default='', verbose_name='의뢰게시글 링크')
    sArea = models.TextField(blank=True, verbose_name='공사지역')
    dateSchedule = models.DateField(null=True, blank=True, verbose_name='공사예정일')
    sConstruction = models.TextField(blank=True, verbose_name='공사내용')

    # 할당 정보
    assigned_company = models.CharField(max_length=100, blank=True, default='', verbose_name='할당업체명')
    recent_status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='대기중', verbose_name='최근할당상태')
    re_request_count = models.IntegerField(default=0, verbose_name='재의뢰횟수')

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
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, null=True, blank=True, verbose_name='UUID')
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


class ChangeHistory(models.Model):
    """필드 변경 이력 모델"""

    no = models.AutoField(primary_key=True, verbose_name='변경이력ID')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='change_histories', verbose_name='의뢰')
    field_name = models.CharField(max_length=50, verbose_name='필드명')
    field_label = models.CharField(max_length=50, verbose_name='필드라벨')
    old_value = models.TextField(blank=True, verbose_name='이전값')
    new_value = models.TextField(blank=True, verbose_name='새값')
    author = models.CharField(max_length=50, verbose_name='작업자')
    datetime = models.DateTimeField(auto_now_add=True, verbose_name='변경일시')

    class Meta:
        db_table = 'change_history'
        verbose_name = '변경이력'
        verbose_name_plural = '변경이력'
        ordering = ['-datetime']

    def __str__(self):
        return f"{self.order.no} - {self.field_label} 변경 ({self.author})"


class StatusHistory(models.Model):
    """상태 변경 이력 모델"""

    no = models.AutoField(primary_key=True, verbose_name='상태이력ID')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='status_histories', verbose_name='의뢰')
    old_status = models.CharField(max_length=30, verbose_name='이전상태')
    new_status = models.CharField(max_length=30, verbose_name='새상태')
    message_sent = models.BooleanField(default=False, verbose_name='문자발송여부')
    message_content = models.TextField(blank=True, verbose_name='문자내용')
    author = models.CharField(max_length=50, verbose_name='작업자')
    datetime = models.DateTimeField(auto_now_add=True, verbose_name='변경일시')

    class Meta:
        db_table = 'status_history'
        verbose_name = '상태변경이력'
        verbose_name_plural = '상태변경이력'
        ordering = ['-datetime']

    def __str__(self):
        return f"{self.order.no} - {self.old_status} → {self.new_status} ({self.author})"


class QuoteLink(models.Model):
    """견적서 링크 관리 모델"""

    no = models.AutoField(primary_key=True, verbose_name='견적링크ID')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='quote_links', verbose_name='의뢰')
    open_quote_link = models.URLField(max_length=500, blank=True, verbose_name='공개견적서링크')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일시')

    class Meta:
        db_table = 'quote_link'
        verbose_name = '견적링크'
        verbose_name_plural = '견적링크'
        ordering = ['-created_at']

    def __str__(self):
        return f"견적링크 {self.no} - 의뢰{self.order.no}"


class QuoteDraft(models.Model):
    """견적서 초안/차수 관리 모델"""

    DRAFT_TYPE_CHOICES = [
        ('1차', '1차'),
        ('2차', '2차'),
        ('3차', '3차'),
        ('4차', '4차'),
        ('5차', '5차'),
        ('최종', '최종'),
    ]

    no = models.AutoField(primary_key=True, verbose_name='초안ID')
    quote_link = models.ForeignKey(QuoteLink, on_delete=models.CASCADE, related_name='drafts', verbose_name='견적링크')
    draft_type = models.CharField(max_length=10, choices=DRAFT_TYPE_CHOICES, verbose_name='초안타입')
    link = models.URLField(max_length=500, verbose_name='링크')
    datetime = models.DateTimeField(auto_now_add=True, verbose_name='생성일시')

    class Meta:
        db_table = 'quote_draft'
        verbose_name = '견적초안'
        verbose_name_plural = '견적초안'
        ordering = ['datetime']

    def __str__(self):
        return f"{self.draft_type} - {self.quote_link.order.no}"


class Memo(models.Model):
    """메모 관리 모델"""

    no = models.AutoField(primary_key=True, verbose_name='메모ID')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='memos', verbose_name='의뢰')
    author = models.CharField(max_length=50, verbose_name='작성자')
    content = models.TextField(verbose_name='내용')
    datetime = models.DateTimeField(auto_now_add=True, verbose_name='작성일시')

    class Meta:
        db_table = 'memo'
        verbose_name = '메모'
        verbose_name_plural = '메모'
        ordering = ['-datetime']

    def __str__(self):
        return f"메모 {self.no} - 의뢰{self.order.no} ({self.author})"

    def get_preview(self):
        """메모 미리보기 (50자 제한)"""
        if len(self.content) > 50:
            return self.content[:50] + "..."
        return self.content


class GroupPurchase(models.Model):
    """공동구매 관리 모델"""

    no = models.AutoField(primary_key=True, verbose_name='공동구매ID')
    round = models.CharField(max_length=20, verbose_name='회차')
    company = models.ForeignKey('company.Company', on_delete=models.SET_NULL, null=True, verbose_name='업체')
    company_name = models.CharField(max_length=100, verbose_name='업체명')
    unavailable_dates = models.JSONField(default=list, verbose_name='불가능날짜들')
    available_areas = models.JSONField(default=list, verbose_name='가능지역들')
    name = models.CharField(max_length=100, verbose_name='공동구매명')
    link = models.URLField(max_length=500, blank=True, verbose_name='링크')
    is_active = models.BooleanField(default=True, verbose_name='활성여부')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일시')

    class Meta:
        db_table = 'group_purchase'
        verbose_name = '공동구매'
        verbose_name_plural = '공동구매'
        ordering = ['-round']

    def __str__(self):
        return f"{self.round} - {self.name} ({self.company_name})"

    def check_availability(self, scheduled_date, area):
        """날짜와 지역 가능 여부 확인"""
        from datetime import datetime

        # 날짜 체크
        if scheduled_date and self.unavailable_dates:
            scheduled_str = scheduled_date.strftime('%Y-%m-%d')
            if scheduled_str in self.unavailable_dates:
                return {'date_available': False, 'area_available': True}

        # 지역 체크
        if area and self.available_areas:
            area_available = any(
                avail_area.lower() in area.lower()
                for avail_area in self.available_areas
            )
            return {'date_available': True, 'area_available': area_available}

        return {'date_available': True, 'area_available': True}


class MessageTemplate(models.Model):
    """메시지 템플릿 모델"""

    no = models.AutoField(primary_key=True, verbose_name='템플릿ID')
    name = models.CharField(max_length=50, unique=True, verbose_name='템플릿명')
    content = models.TextField(verbose_name='템플릿내용')
    variables = models.JSONField(default=list, verbose_name='변수목록', help_text='예: ["name", "workContent"]')
    is_active = models.BooleanField(default=True, verbose_name='활성여부')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일시')

    class Meta:
        db_table = 'message_template'
        verbose_name = '메시지템플릿'
        verbose_name_plural = '메시지템플릿'
        ordering = ['name']

    def __str__(self):
        return self.name

    def render(self, context):
        """템플릿 렌더링"""
        content = self.content
        for var in self.variables:
            if var in context:
                placeholder = '{' + var + '}'
                content = content.replace(placeholder, str(context[var]))
        return content
