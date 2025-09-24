from django.db import models
from django.utils import timezone


class FixFee(models.Model):
    """고정비납부(FixFee) 모델"""

    # 기본 정보
    no = models.AutoField(primary_key=True, verbose_name='고정비납부ID')
    noCompany = models.IntegerField(verbose_name='업체ID')

    # 납부 정보
    dateToDo = models.DateField(verbose_name='납부기준일')
    dateDeposit = models.DateField(null=True, blank=True, verbose_name='납부일자')
    nDeposit = models.IntegerField(default=0, verbose_name='실납부액(원)')
    bDeposit = models.BooleanField(default=False, verbose_name='완납여부')

    # 메모
    sMemo = models.TextField(blank=True, verbose_name='비고')

    # 자동 생성 필드
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일시')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일시')

    class Meta:
        db_table = 'fix_fee'  # 기존 테이블명 유지
        verbose_name = '고정비납부'
        verbose_name_plural = '고정비납부'
        ordering = ['-no']  # 최신순 정렬

    def __str__(self):
        return f"고정비납부 {self.no} - 업체{self.noCompany} ({self.dateToDo})"

    def get_company_name(self):
        """연결된 업체명 반환"""
        try:
            from company.models import Company
            company = Company.objects.get(no=self.noCompany)
            return company.sName2 or company.sName1 or f"업체{self.noCompany}"
        except:
            return f"업체{self.noCompany}"

    def get_payment_status(self):
        """납부 상태 반환"""
        if self.bDeposit:
            return "완납"
        elif self.dateDeposit and self.nDeposit > 0:
            return "부분납부"
        elif self.dateDeposit:
            return "납부처리"
        else:
            return "미납"

    def get_days_overdue(self):
        """연체 일수 계산"""
        today = timezone.localtime().date()

        if not self.bDeposit and today > self.dateToDo:
            return (today - self.dateToDo).days
        return 0

    def is_overdue(self):
        """연체 여부 확인"""
        return self.get_days_overdue() > 0

    def get_due_status(self):
        """납부 기한 상태"""
        today = timezone.localtime().date()

        if self.bDeposit:
            return "완료"
        elif today < self.dateToDo:
            days_until = (self.dateToDo - today).days
            if days_until <= 3:
                return f"임박({days_until}일)"
            else:
                return f"여유({days_until}일)"
        elif today == self.dateToDo:
            return "당일"
        else:
            return f"연체({self.get_days_overdue()}일)"

    def get_payment_delay_days(self):
        """납부 지연 일수 (납부기준일 대비 실제 납부일)"""
        if self.dateDeposit and self.dateToDo:
            delay = (self.dateDeposit - self.dateToDo).days
            return max(0, delay)  # 음수는 0으로 처리 (조기납부)
        return 0

    def is_early_payment(self):
        """조기납부 여부"""
        if self.dateDeposit and self.dateToDo:
            return self.dateDeposit < self.dateToDo
        return False

    def get_formatted_deposit(self):
        """납부액 포맷팅"""
        return f"{self.nDeposit:,}원" if self.nDeposit else "0원"

    def get_payment_summary(self):
        """납부 요약 정보"""
        return {
            'company_name': self.get_company_name(),
            'due_date': self.dateToDo,
            'payment_date': self.dateDeposit,
            'amount': self.get_formatted_deposit(),
            'status': self.get_payment_status(),
            'due_status': self.get_due_status(),
            'is_overdue': self.is_overdue(),
            'overdue_days': self.get_days_overdue(),
            'is_early': self.is_early_payment()
        }

    def mark_as_paid(self, amount=None, payment_date=None):
        """완납 처리"""
        if amount:
            self.nDeposit = amount
        if payment_date:
            self.dateDeposit = payment_date
        else:
            self.dateDeposit = timezone.localtime().date()

        self.bDeposit = True
        self.save()

    def get_status_color(self):
        """상태별 색상 반환"""
        status = self.get_payment_status()
        color_map = {
            '완납': 'green',
            '부분납부': 'orange',
            '납부처리': 'blue',
            '미납': 'red' if self.is_overdue() else 'gray'
        }
        return color_map.get(status, 'black')

    def calculate_late_fee(self, daily_rate=0.0001):
        """연체료 계산 (일일 연체료율 기본 0.01%)"""
        if self.is_overdue() and self.nDeposit > 0:
            overdue_days = self.get_days_overdue()
            return int(self.nDeposit * daily_rate * overdue_days)
        return 0

    def get_next_due_date(self):
        """다음 납부기준일 (월단위 가정)"""
        from dateutil.relativedelta import relativedelta
        return self.dateToDo + relativedelta(months=1)

    def is_current_month(self):
        """현재 월 납부건인지 확인"""
        today = timezone.localtime().date()
        return (self.dateToDo.year == today.year and
                self.dateToDo.month == today.month)

    @classmethod
    def get_overdue_fees(cls):
        """연체된 고정비 목록 조회"""
        today = timezone.localtime().date()
        return cls.objects.filter(
            bDeposit=False,
            dateToDo__lt=today
        ).order_by('dateToDo')

    @classmethod
    def get_upcoming_fees(cls, days=7):
        """향후 납부 예정 고정비 목록"""
        today = timezone.localtime().date()
        end_date = today + timezone.timedelta(days=days)
        return cls.objects.filter(
            bDeposit=False,
            dateToDo__range=[today, end_date]
        ).order_by('dateToDo')

    @classmethod
    def get_company_payment_history(cls, company_id):
        """특정 업체의 납부 이력"""
        return cls.objects.filter(noCompany=company_id).order_by('-dateToDo')

    @classmethod
    def get_monthly_summary(cls, year, month):
        """월별 납부 현황 요약"""
        from django.db.models import Count, Sum, Q

        return cls.objects.filter(
            dateToDo__year=year,
            dateToDo__month=month
        ).aggregate(
            total_count=Count('no'),
            paid_count=Count('no', filter=Q(bDeposit=True)),
            total_amount=Sum('nDeposit'),
            unpaid_count=Count('no', filter=Q(bDeposit=False))
        )