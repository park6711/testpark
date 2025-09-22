from django.db import models
from django.utils import timezone


class CompanyReport(models.Model):
    """업체계약보고(CompanyReport) 모델"""

    # 보고구분 선택지
    TYPE_CHOICES = [
        (0, '가계약'),
        (1, '계약(입금X)'),
        (2, '계약(입금O)'),
        (3, '증액(입금X)'),
        (4, '증액(입금O)'),
        (5, '감액(환불X)'),
        (6, '감액(환불O)'),
        (7, '취소(환불X)'),
        (8, '취소(환불O)'),
    ]

    # 공사유형 선택지
    CONSTRUCTION_TYPE_CHOICES = [
        (0, '[카페건]인테리어/리모델링/기타'),
        (1, '[카테건]신축/증축/개축'),
        (2, '[소개건]인테리어/리모델링/기타'),
        (3, '[소개건]신축/증축/개축'),
    ]

    # 환불방식 선택지
    REFUND_TYPE_CHOICES = [
        (0, '계좌이체'),
        (1, '포인트적립'),
    ]

    # 기본 정보
    no = models.AutoField(primary_key=True, verbose_name='업체계약보고ID')
    time = models.DateTimeField(auto_now_add=True, verbose_name='보고일시')
    noCompany = models.IntegerField(verbose_name='업체ID')

    # 보고 정보
    nType = models.IntegerField(
        choices=TYPE_CHOICES,
        default=0,
        verbose_name='보고구분'
    )
    noPre = models.IntegerField(null=True, blank=True, verbose_name='관련 이전보고 ID')
    noNext = models.IntegerField(null=True, blank=True, verbose_name='관련 이후보고 ID')

    # 공사 정보
    noConType = models.IntegerField(
        choices=CONSTRUCTION_TYPE_CHOICES,
        default=0,
        verbose_name='공사유형'
    )
    sPost = models.CharField(max_length=200, blank=True, verbose_name='게시글 번호')
    noAssign = models.IntegerField(null=True, blank=True, verbose_name='할당ID')

    # 고객 정보
    sName = models.CharField(max_length=50, blank=True, verbose_name='고객 이름')
    sPhone = models.CharField(max_length=20, blank=True, verbose_name='고객 핸드폰 번호')
    sArea = models.TextField(blank=True, verbose_name='공사 주소')

    # 계약 정보
    dateContract = models.DateField(null=True, blank=True, verbose_name='공사 계약일')
    dateSchedule = models.DateField(null=True, blank=True, verbose_name='공사 완료예정일')
    nConMoney = models.IntegerField(default=0, verbose_name='공사 금액(원)')
    bVat = models.BooleanField(default=False, verbose_name='vat포함 여부')

    # 수수료 및 정산 정보
    nFee = models.IntegerField(default=0, verbose_name='수수료(원)')
    nAppPoint = models.IntegerField(default=0, verbose_name='적용포인트')
    nDemand = models.IntegerField(default=0, verbose_name='청구액/환불액(원)')

    # 입금/환불 정보
    dateDeposit = models.DateField(null=True, blank=True, verbose_name='입금일/환불일')
    nDeposit = models.IntegerField(default=0, verbose_name='입금액/환불액')
    nExcess = models.IntegerField(default=0, verbose_name='과/미입금(+ or -)')
    nRefund = models.IntegerField(
        choices=REFUND_TYPE_CHOICES,
        default=0,
        verbose_name='환불방식'
    )

    # 업체 및 계좌 정보
    sCompanyName = models.CharField(max_length=200, blank=True, verbose_name='전자세금계산서 발행 사업자')
    sAccount = models.CharField(max_length=100, blank=True, verbose_name='환불 통장계좌')

    # 파일 및 메모
    file = models.FileField(upload_to='company_reports/', blank=True, null=True, verbose_name='증빙자료')
    sCompanyMemo = models.TextField(blank=True, verbose_name='남긴 말씀')
    sStaffMemo = models.TextField(blank=True, verbose_name='메모')
    sWorker = models.CharField(max_length=50, blank=True, verbose_name='보고자')

    # 자동 생성 필드
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일시')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일시')

    class Meta:
        db_table = 'company_report'
        verbose_name = '업체계약보고'
        verbose_name_plural = '업체계약보고'
        ordering = ['-no']  # 최신순 정렬

    def __str__(self):
        return f"보고 {self.no} - {self.sName} ({self.get_nType_display()})"

    def get_company_name(self):
        """연결된 업체명 반환"""
        try:
            from company.models import Company
            company = Company.objects.get(no=self.noCompany)
            return company.sCompanyName or f"업체{self.noCompany}"
        except:
            return f"업체{self.noCompany}"

    def get_assign_info(self):
        """연결된 할당 정보 반환"""
        if not self.noAssign:
            return None
        try:
            from order.models import Assign
            assign = Assign.objects.get(no=self.noAssign)
            return assign
        except:
            return None

    def get_type_display_with_color(self):
        """보고구분과 색상 정보 반환"""
        type_colors = {
            0: ('가계약', 'warning'),       # 노란색
            1: ('계약(입금X)', 'info'),      # 파란색
            2: ('계약(입금O)', 'success'),   # 초록색
            3: ('증액(입금X)', 'info'),      # 파란색
            4: ('증액(입금O)', 'success'),   # 초록색
            5: ('감액(환불X)', 'warning'),   # 노란색
            6: ('감액(환불O)', 'secondary'), # 회색
            7: ('취소(환불X)', 'danger'),    # 빨간색
            8: ('취소(환불O)', 'dark'),      # 검은색
        }
        type_name, color = type_colors.get(self.nType, ('알 수 없음', 'secondary'))
        return {'type': type_name, 'color': color}

    def get_construction_type_short(self):
        """공사유형 짧은 표시"""
        type_map = {
            0: '카페-인테리어', 1: '카테-신축', 2: '소개-인테리어', 3: '소개-신축'
        }
        return type_map.get(self.noConType, '기타')

    def get_money_summary(self):
        """금액 요약 정보 반환"""
        return {
            'contract_money': self.nConMoney,
            'fee': self.nFee,
            'demand': self.nDemand,
            'deposit': self.nDeposit,
            'excess': self.nExcess
        }

    def get_profit_margin(self):
        """수익률 계산 (수수료/공사금액*100)"""
        if self.nConMoney > 0:
            return round((self.nFee / self.nConMoney) * 100, 2)
        return 0

    def is_paid(self):
        """입금 완료 여부"""
        return self.nType in [2, 4, 6, 8]  # 입금O 상태들

    def is_contract_completed(self):
        """계약 완료 여부 (가계약 제외)"""
        return self.nType >= 1

    def is_cancelled(self):
        """취소 여부"""
        return self.nType in [7, 8]

    def get_schedule_status(self):
        """공사 일정 상태 반환"""
        if not self.dateSchedule:
            return "일정 미정"

        today = timezone.localtime().date()
        diff_days = (self.dateSchedule - today).days

        if diff_days < 0:
            return f"완료 예정일 지남 ({abs(diff_days)}일)"
        elif diff_days == 0:
            return "완료 예정일 당일"
        elif diff_days <= 7:
            return f"완료 예정일 {diff_days}일 전"
        else:
            return f"완료까지 {diff_days}일"

    def get_contract_duration(self):
        """계약일부터 완료예정일까지 기간"""
        if self.dateContract and self.dateSchedule:
            return (self.dateSchedule - self.dateContract).days
        return None

    def get_related_reports(self):
        """관련 보고서들 반환 (이전/이후)"""
        related = {}
        if self.noPre:
            try:
                related['previous'] = CompanyReport.objects.get(no=self.noPre)
            except CompanyReport.DoesNotExist:
                pass
        if self.noNext:
            try:
                related['next'] = CompanyReport.objects.get(no=self.noNext)
            except CompanyReport.DoesNotExist:
                pass
        return related

    def get_vat_display(self):
        """VAT 포함 여부 표시"""
        return "VAT 포함" if self.bVat else "VAT 별도"


class ClientReport(models.Model):
    """고객계약보고(ClientReport) 모델"""

    # 기본 정보
    no = models.AutoField(primary_key=True, verbose_name='고객계약보고ID')
    time = models.DateTimeField(auto_now_add=True, verbose_name='타임스탬프')
    noCompany = models.IntegerField(verbose_name='업체 ID')

    # 업체 및 고객 정보
    sCompanyName = models.CharField(max_length=200, blank=True, verbose_name='업체명')
    sName = models.CharField(max_length=50, blank=True, verbose_name='고객 성함')
    sPhone = models.CharField(max_length=20, blank=True, verbose_name='고객 핸드폰 번호')

    # 보고 내용
    sExplain = models.TextField(blank=True, verbose_name='소명 내용')
    sPunish = models.TextField(blank=True, verbose_name='징계 내용')

    # 자동 생성 필드
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일시')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일시')

    class Meta:
        db_table = 'client_report'
        verbose_name = '고객계약보고'
        verbose_name_plural = '고객계약보고'
        ordering = ['-no']  # 최신순 정렬

    def __str__(self):
        return f"고객보고 {self.no} - {self.sName} ({self.sCompanyName})"

    def get_company_name(self):
        """연결된 업체명 반환"""
        try:
            from company.models import Company
            company = Company.objects.get(no=self.noCompany)
            return company.sCompanyName or f"업체{self.noCompany}"
        except:
            return self.sCompanyName or f"업체{self.noCompany}"

    def has_punishment(self):
        """징계 여부 확인"""
        return bool(self.sPunish.strip()) if self.sPunish else False

    def has_explanation(self):
        """소명 여부 확인"""
        return bool(self.sExplain.strip()) if self.sExplain else False

    def get_report_summary(self):
        """보고서 요약 정보"""
        return {
            'company_name': self.get_company_name(),
            'client_name': self.sName,
            'has_explanation': self.has_explanation(),
            'has_punishment': self.has_punishment(),
            'report_date': self.time.date() if self.time else None
        }

    def get_status_display(self):
        """보고서 상태 표시"""
        if self.has_punishment():
            return "징계"
        elif self.has_explanation():
            return "소명"
        else:
            return "접수"

    def get_phone_masked(self):
        """전화번호 마스킹 처리"""
        if not self.sPhone:
            return ""

        phone = self.sPhone.replace("-", "").replace(" ", "")
        if len(phone) >= 8:
            return f"{phone[:3]}-****-{phone[-4:]}"
        return self.sPhone
