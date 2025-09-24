from django.db import models
from django.utils import timezone


class FixFeeDate(models.Model):
    """고정비납부기준일(FixFeeDate) 모델"""

    no = models.AutoField(primary_key=True, verbose_name='고정비납부기준일ID')
    date = models.DateField(unique=True, verbose_name='납부기준일')

    class Meta:
        db_table = 'fix_fee_date'
        verbose_name = '고정비납부기준일'
        verbose_name_plural = '고정비납부기준일'
        ordering = ['-date']

    def __str__(self):
        return f"납부기준일: {self.date}"


class FixFee(models.Model):
    """고정비납부(FixFee) 모델 - 개편된 구조"""

    # 납부방식 타입
    TYPE_CHOICES = [
        (0, '계좌이체'),
        (1, '우수업체'),
        (2, '최우수업체'),
        (3, '기타'),
    ]

    # 기본 정보
    no = models.AutoField(primary_key=True, verbose_name='고정비납부ID')
    noCompany = models.IntegerField(verbose_name='업체ID', db_index=True)
    noFixFeeDate = models.IntegerField(verbose_name='납부기준일ID', db_index=True)

    # 납부 정보
    dateDeposit = models.DateField(null=True, blank=True, verbose_name='완납일자')
    nFixFee = models.IntegerField(default=0, verbose_name='월고정비(원)')
    nType = models.IntegerField(
        choices=TYPE_CHOICES,
        default=0,
        verbose_name='납부방식'
    )

    # 메모
    sMemo = models.TextField(blank=True, verbose_name='비고', max_length=500)

    # 자동 생성 필드
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일시')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일시')

    class Meta:
        db_table = 'fix_fee'  # 테이블명
        verbose_name = '고정비납부'
        verbose_name_plural = '고정비납부'
        ordering = ['-noFixFeeDate', '-no']
        unique_together = [['noCompany', 'noFixFeeDate']]  # 업체별 납부기준일당 하나의 레코드만

    def __str__(self):
        return f"고정비납부 {self.no} - 업체{self.noCompany} (기준일ID: {self.noFixFeeDate})"

    def get_company_name(self):
        """연결된 업체명 반환"""
        try:
            from company.models import Company
            company = Company.objects.get(no=self.noCompany)
            return company.sName2 or company.sName1 or f"업체{self.noCompany}"
        except:
            return f"업체{self.noCompany}"

    def get_company_condition(self):
        """연결된 업체의 활동상태 반환"""
        try:
            from company.models import Company
            company = Company.objects.get(no=self.noCompany)
            return company.nCondition
        except:
            return None

    def get_fix_fee_date(self):
        """연결된 납부기준일 반환"""
        try:
            fee_date = FixFeeDate.objects.get(no=self.noFixFeeDate)
            return fee_date.date
        except:
            return None

    def get_payment_type_display_custom(self):
        """납부방식 표시명 반환"""
        return dict(self.TYPE_CHOICES).get(self.nType, '기타')

    def is_paid(self):
        """완납 여부 확인"""
        return self.dateDeposit is not None

    def get_payment_status(self):
        """납부 상태 반환"""
        if self.dateDeposit:
            return "완납"
        else:
            return "미납"

    def get_days_overdue(self):
        """연체 일수 계산"""
        if not self.dateDeposit:
            fee_date = self.get_fix_fee_date()
            if fee_date:
                today = timezone.localtime().date()
                if today > fee_date:
                    return (today - fee_date).days
        return 0

    def is_overdue(self):
        """연체 여부 확인"""
        return self.get_days_overdue() > 0

    def get_due_status(self):
        """납부 기한 상태"""
        fee_date = self.get_fix_fee_date()
        if not fee_date:
            return "기준일 없음"

        today = timezone.localtime().date()

        if self.dateDeposit:
            return "완료"
        elif today < fee_date:
            days_until = (fee_date - today).days
            if days_until <= 3:
                return f"임박({days_until}일)"
            else:
                return f"여유({days_until}일)"
        elif today == fee_date:
            return "당일"
        else:
            return f"연체({self.get_days_overdue()}일)"

    def get_payment_delay_days(self):
        """납부 지연 일수 (납부기준일 대비 실제 납부일)"""
        fee_date = self.get_fix_fee_date()
        if self.dateDeposit and fee_date:
            delay = (self.dateDeposit - fee_date).days
            return max(0, delay)  # 음수는 0으로 처리 (조기납부)
        return 0

    def is_early_payment(self):
        """조기납부 여부"""
        fee_date = self.get_fix_fee_date()
        if self.dateDeposit and fee_date:
            return self.dateDeposit < fee_date
        return False

    def get_formatted_fee(self):
        """고정비 포맷팅"""
        return f"{self.nFixFee:,}원" if self.nFixFee else "0원"

    def get_payment_summary(self):
        """납부 요약 정보"""
        return {
            'company_name': self.get_company_name(),
            'due_date': self.get_fix_fee_date(),
            'payment_date': self.dateDeposit,
            'amount': self.get_formatted_fee(),
            'payment_type': self.get_payment_type_display_custom(),
            'status': self.get_payment_status(),
            'due_status': self.get_due_status(),
            'is_overdue': self.is_overdue(),
            'overdue_days': self.get_days_overdue(),
            'is_early': self.is_early_payment()
        }

    def mark_as_paid(self, payment_date=None):
        """완납 처리"""
        if payment_date:
            self.dateDeposit = payment_date
        else:
            self.dateDeposit = timezone.localtime().date()
        self.save()

    def get_status_color(self):
        """상태별 색상 반환"""
        if self.dateDeposit:
            return 'green'
        elif self.is_overdue():
            return 'red'
        else:
            return 'gray'

    def calculate_late_fee(self, daily_rate=0.0001):
        """연체료 계산 (일일 연체료율 기본 0.01%)"""
        if self.is_overdue() and self.nFixFee > 0:
            overdue_days = self.get_days_overdue()
            return int(self.nFixFee * daily_rate * overdue_days)
        return 0

    @classmethod
    def get_overdue_fees(cls):
        """연체된 고정비 목록 조회"""
        today = timezone.localtime().date()
        overdue_list = []

        # 모든 미납 건 조회
        unpaid = cls.objects.filter(dateDeposit__isnull=True)

        for fee in unpaid:
            if fee.is_overdue():
                overdue_list.append(fee)

        return overdue_list

    @classmethod
    def get_upcoming_fees(cls, days=7):
        """향후 납부 예정 고정비 목록"""
        today = timezone.localtime().date()
        end_date = today + timezone.timedelta(days=days)

        # 해당 기간의 납부기준일 찾기
        fee_dates = FixFeeDate.objects.filter(
            dateToDo__range=[today, end_date]
        )

        fee_date_ids = [fd.no for fd in fee_dates]

        return cls.objects.filter(
            noFixFeeDate__in=fee_date_ids,
            dateDeposit__isnull=True
        ).order_by('noFixFeeDate')

    @classmethod
    def get_company_payment_history(cls, company_id):
        """특정 업체의 납부 이력"""
        return cls.objects.filter(noCompany=company_id).order_by('-noFixFeeDate')

    @classmethod
    def get_monthly_summary(cls, year, month):
        """월별 납부 현황 요약"""
        from django.db.models import Count, Sum, Q

        # 해당 월의 납부기준일 찾기
        fee_dates = FixFeeDate.objects.filter(
            dateToDo__year=year,
            dateToDo__month=month
        )

        fee_date_ids = [fd.no for fd in fee_dates]

        return cls.objects.filter(
            noFixFeeDate__in=fee_date_ids
        ).aggregate(
            total_count=Count('no'),
            paid_count=Count('no', filter=Q(dateDeposit__isnull=False)),
            total_amount=Sum('nFixFee'),
            unpaid_count=Count('no', filter=Q(dateDeposit__isnull=True))
        )

    @classmethod
    def create_monthly_fees(cls, fee_date_id, companies, default_amount=165000):
        """월별 고정비 일괄 생성"""
        created_fees = []

        for company_id in companies:
            fee, created = cls.objects.get_or_create(
                noCompany=company_id,
                noFixFeeDate=fee_date_id,
                defaults={
                    'nFixFee': default_amount,
                    'nType': 0  # 기본값: 계좌이체
                }
            )
            if created:
                created_fees.append(fee)

        return created_fees