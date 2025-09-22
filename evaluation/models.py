from django.db import models
from django.utils import timezone
from datetime import timedelta


class EvaluationNo(models.Model):
    """업체평가회차(EvaluationNo) 모델"""

    # 기본 정보
    no = models.AutoField(primary_key=True, verbose_name='업체평가회차ID')

    # 평가 기간 정보
    dateStart = models.DateField(verbose_name='평가기간 시작일')
    dateEnd = models.DateField(verbose_name='평가기간 종료일')

    # 포인트 적용 기간
    datePointStart = models.DateField(verbose_name='적용포인트 시작일')
    datePointEnd = models.DateField(verbose_name='적용포인트 종료일')

    # 계약률 정보
    fAverageAll = models.FloatField(default=0.0, verbose_name='평균계약률')
    fAverageExcel = models.FloatField(default=0.0, verbose_name='우수업체 평균계약률')

    # 예약문자 시간 정보
    timeExcel = models.TimeField(null=True, blank=True, verbose_name='우수업체 예약문자시간')
    timeWeek = models.TimeField(null=True, blank=True, verbose_name='미진업체 예약문자시간')

    # 자동 생성 필드
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일시')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일시')

    class Meta:
        db_table = 'evaluation_no'
        verbose_name = '업체평가회차'
        verbose_name_plural = '업체평가회차'
        ordering = ['-no']  # 최신순 정렬

    def __str__(self):
        return f"평가회차 {self.no} ({self.dateStart} ~ {self.dateEnd})"

    def get_evaluation_period_days(self):
        """평가 기간 일수 계산"""
        if self.dateStart and self.dateEnd:
            return (self.dateEnd - self.dateStart).days + 1
        return 0

    def get_point_period_days(self):
        """포인트 적용 기간 일수 계산"""
        if self.datePointStart and self.datePointEnd:
            return (self.datePointEnd - self.datePointStart).days + 1
        return 0

    def is_evaluation_period_active(self):
        """현재가 평가 기간 내인지 확인"""
        today = timezone.localtime().date()
        return self.dateStart <= today <= self.dateEnd

    def is_point_period_active(self):
        """현재가 포인트 적용 기간 내인지 확인"""
        today = timezone.localtime().date()
        return self.datePointStart <= today <= self.datePointEnd

    def get_period_status(self):
        """기간 상태 반환"""
        today = timezone.localtime().date()

        if today < self.dateStart:
            return "대기"
        elif self.dateStart <= today <= self.dateEnd:
            return "평가중"
        elif self.dateEnd < today < self.datePointStart:
            return "평가완료"
        elif self.datePointStart <= today <= self.datePointEnd:
            return "포인트적용중"
        else:
            return "완료"

    def get_average_improvement(self):
        """우수업체와 전체 평균의 차이"""
        return self.fAverageExcel - self.fAverageAll

    def get_formatted_average_all(self):
        """전체 평균계약률 퍼센트 형태로 반환"""
        return f"{self.fAverageAll:.2f}%"

    def get_formatted_average_excel(self):
        """우수업체 평균계약률 퍼센트 형태로 반환"""
        return f"{self.fAverageExcel:.2f}%"

    def is_excel_performance(self):
        """우수업체 기준을 충족하는지 확인"""
        return self.fAverageExcel > self.fAverageAll

    def get_days_until_start(self):
        """평가 시작까지 남은 일수"""
        today = timezone.localtime().date()
        if today < self.dateStart:
            return (self.dateStart - today).days
        return 0

    def get_days_until_end(self):
        """평가 종료까지 남은 일수"""
        today = timezone.localtime().date()
        if today < self.dateEnd:
            return (self.dateEnd - today).days
        return 0

    def get_progress_percentage(self):
        """평가 기간 진행률 (퍼센트)"""
        today = timezone.localtime().date()

        if today < self.dateStart:
            return 0
        elif today > self.dateEnd:
            return 100
        else:
            total_days = self.get_evaluation_period_days()
            elapsed_days = (today - self.dateStart).days + 1
            return round((elapsed_days / total_days) * 100, 1) if total_days > 0 else 0

    def get_notification_times_display(self):
        """예약문자 시간 정보 표시"""
        excel_time = self.timeExcel.strftime('%H:%M') if self.timeExcel else '미설정'
        week_time = self.timeWeek.strftime('%H:%M') if self.timeWeek else '미설정'
        return {
            'excel': excel_time,
            'week': week_time
        }

    def is_overlapping_period(self, other_evaluation):
        """다른 평가회차와 기간이 겹치는지 확인"""
        return not (self.dateEnd < other_evaluation.dateStart or
                   other_evaluation.dateEnd < self.dateStart)

    def get_summary_info(self):
        """평가회차 요약 정보"""
        return {
            'evaluation_no': self.no,
            'period': f"{self.dateStart} ~ {self.dateEnd}",
            'point_period': f"{self.datePointStart} ~ {self.datePointEnd}",
            'status': self.get_period_status(),
            'progress': f"{self.get_progress_percentage()}%",
            'average_all': self.get_formatted_average_all(),
            'average_excel': self.get_formatted_average_excel(),
            'improvement': f"{self.get_average_improvement():.2f}%"
        }


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
        db_table = 'fix_fee'
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
            return company.sCompanyName or f"업체{self.noCompany}"
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
        from django.utils import timezone
        today = timezone.localtime().date()

        if not self.bDeposit and today > self.dateToDo:
            return (today - self.dateToDo).days
        return 0

    def is_overdue(self):
        """연체 여부 확인"""
        return self.get_days_overdue() > 0

    def get_due_status(self):
        """납부 기한 상태"""
        from django.utils import timezone
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
        from django.utils import timezone

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
        from django.utils import timezone
        today = timezone.localtime().date()
        return (self.dateToDo.year == today.year and
                self.dateToDo.month == today.month)


class Complain(models.Model):
    """고객불만(Complain) 모델"""

    # 기본 정보
    no = models.AutoField(primary_key=True, verbose_name='고객불만ID')
    noEvaluation = models.IntegerField(verbose_name='업체평가회수ID')
    noCompany = models.IntegerField(verbose_name='업체ID')

    # 불만 정보
    sTime = models.CharField(max_length=50, blank=True, verbose_name='타임스탬프')
    sComName = models.CharField(max_length=100, blank=True, verbose_name='업체명')
    sPass = models.CharField(max_length=50, blank=True, verbose_name='경로')
    sComplain = models.TextField(blank=True, verbose_name='불만 내용')
    sComplainPost = models.TextField(blank=True, verbose_name='링크')
    sPost = models.CharField(max_length=100, blank=True, verbose_name='의뢰글')
    sFile = models.TextField(blank=True, verbose_name='고객불만 파일')
    sCheck = models.CharField(max_length=50, blank=True, verbose_name='계약 확인 여부')
    sWorker = models.CharField(max_length=50, blank=True, verbose_name='작성자')
    fComplain = models.FloatField(default=0.0, verbose_name='불만점수')

    # 자동 생성 필드
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일시')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일시')

    class Meta:
        db_table = 'complain'
        verbose_name = '고객불만'
        verbose_name_plural = '고객불만'
        ordering = ['-no']

    def __str__(self):
        return f"고객불만 {self.no} - {self.sComName}"

    def get_evaluation_info(self):
        """평가회차 정보"""
        try:
            evaluation = EvaluationNo.objects.get(no=self.noEvaluation)
            return evaluation
        except EvaluationNo.DoesNotExist:
            return None

    def get_company_name(self):
        """업체명 반환"""
        try:
            from company.models import Company
            company = Company.objects.get(no=self.noCompany)
            return company.sCompanyName or self.sComName
        except:
            return self.sComName or f"업체{self.noCompany}"

    def get_severity_level(self):
        """불만 심각도 레벨"""
        if self.fComplain >= 8.0:
            return "매우심각"
        elif self.fComplain >= 6.0:
            return "심각"
        elif self.fComplain >= 4.0:
            return "보통"
        elif self.fComplain >= 2.0:
            return "경미"
        else:
            return "미미"

    def get_severity_color(self):
        """심각도별 색상"""
        level = self.get_severity_level()
        color_map = {
            "매우심각": "red",
            "심각": "orange",
            "보통": "yellow",
            "경미": "blue",
            "미미": "green"
        }
        return color_map.get(level, "gray")


class Satisfy(models.Model):
    """고객만족도(Satisfy) 모델"""

    # 기본 정보
    no = models.AutoField(primary_key=True, verbose_name='고객만족도ID')
    noEvaluation = models.IntegerField(verbose_name='업체평가회수ID')
    noCompany = models.IntegerField(verbose_name='업체ID')

    # 만족도 정보
    sCompanyName = models.CharField(max_length=100, blank=True, verbose_name='업체명')
    sTime = models.CharField(max_length=50, blank=True, verbose_name='타임스탬프')
    sAddress = models.TextField(blank=True, verbose_name='공사 주소')
    sMemo = models.TextField(blank=True, verbose_name='추가 의견')
    fSatisfy = models.FloatField(default=0.0, verbose_name='점수합계')

    # 자동 생성 필드
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일시')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일시')

    class Meta:
        db_table = 'satisfy'
        verbose_name = '고객만족도'
        verbose_name_plural = '고객만족도'
        ordering = ['-no']

    def __str__(self):
        return f"고객만족도 {self.no} - {self.sCompanyName}"

    def get_satisfaction_level(self):
        """만족도 레벨"""
        if self.fSatisfy >= 9.0:
            return "매우만족"
        elif self.fSatisfy >= 7.0:
            return "만족"
        elif self.fSatisfy >= 5.0:
            return "보통"
        elif self.fSatisfy >= 3.0:
            return "불만족"
        else:
            return "매우불만족"

    def get_satisfaction_color(self):
        """만족도별 색상"""
        level = self.get_satisfaction_level()
        color_map = {
            "매우만족": "green",
            "만족": "blue",
            "보통": "yellow",
            "불만족": "orange",
            "매우불만족": "red"
        }
        return color_map.get(level, "gray")


class Evaluation(models.Model):
    """업체평가(Evaluation) 모델"""

    # 기본 정보
    no = models.AutoField(primary_key=True, verbose_name='업체평가ID')
    noEvaluationNo = models.IntegerField(verbose_name='업체평가회수ID')
    noCompany = models.IntegerField(verbose_name='업체ID')

    # 평가 결과
    fTotalScore = models.FloatField(default=0.0, verbose_name='종합점수')
    nLevel = models.IntegerField(default=0, verbose_name='업체레벨')
    nGrade = models.IntegerField(default=0, verbose_name='업체등급')
    fPercent = models.FloatField(default=0.0, verbose_name='계약률(%)')
    bWeak = models.BooleanField(default=False, verbose_name='미진업체')

    # 업무 실적
    nReturn = models.IntegerField(default=0, verbose_name='반려')
    nCancel = models.IntegerField(default=0, verbose_name='취소')
    nExcept = models.IntegerField(default=0, verbose_name='제외')
    nPart = models.IntegerField(default=0, verbose_name='부분수리')
    nAll = models.IntegerField(default=0, verbose_name='올수리')
    nSum = models.IntegerField(default=0, verbose_name='합계')
    nContract = models.IntegerField(default=0, verbose_name='계약')

    # 금액 정보
    nFee = models.IntegerField(default=0, verbose_name='수수료(원)')
    nFixFee = models.IntegerField(default=0, verbose_name='고정비(원)')
    nDotCom = models.IntegerField(default=0, verbose_name='닷컴(원)')
    nBtoB = models.IntegerField(default=0, verbose_name='BtoB 공구(원)')

    # 고객 관련
    fReview = models.FloatField(default=0.0, verbose_name='고객후기')
    fComplain = models.FloatField(default=0.0, verbose_name='고객불만')
    nSatisfy = models.IntegerField(default=0, verbose_name='고객조사건수')
    fSatisfy = models.FloatField(default=0.0, verbose_name='고객만족도조사 평균값')

    # 활동 실적
    nAnswer1 = models.IntegerField(default=0, verbose_name='카페지식답변')
    nAnswer2 = models.IntegerField(default=0, verbose_name='지식공유활동')
    nSeminar = models.IntegerField(default=0, verbose_name='세미나참석')
    bMento = models.BooleanField(default=False, verbose_name='멘토')

    # 보증 관련
    nWarranty1 = models.IntegerField(default=0, verbose_name='이행보증서')
    nWarranty2 = models.IntegerField(default=0, verbose_name='보증증권 보고')
    nWarranty3 = models.IntegerField(default=0, verbose_name='증권발행 현황')
    nSafe = models.IntegerField(default=0, verbose_name='안전 캠페인')
    fSpecial = models.FloatField(default=0.0, verbose_name='특별점수')

    # 포인트 관련
    nPayBackPoint = models.IntegerField(default=0, verbose_name='적립포인트')
    nPrePoint = models.IntegerField(default=0, verbose_name='이월포인트')
    nSumPoint = models.IntegerField(default=0, verbose_name='합계포인트')
    nUsePoint = models.IntegerField(default=0, verbose_name='사용포인트')
    nRemainPoint = models.IntegerField(default=0, verbose_name='잔액포인트')

    # 세부 점수
    fPercentScore = models.FloatField(default=0.0, verbose_name='A1점수')
    fFeeScore = models.FloatField(default=0.0, verbose_name='A2점수')
    fFixFeeScore = models.FloatField(default=0.0, verbose_name='A3점수')
    fBtoBScore = models.FloatField(default=0.0, verbose_name='A4점수')
    fReviewScore = models.FloatField(default=0.0, verbose_name='B점수')
    fComplainScore = models.FloatField(default=0.0, verbose_name='C점수')
    fSafistyScore = models.FloatField(default=0.0, verbose_name='D점수')
    fAnswer1Score = models.FloatField(default=0.0, verbose_name='E점수')
    fAnswer2Socre = models.FloatField(default=0.0, verbose_name='F점수')
    fSeminarScore = models.FloatField(default=0.0, verbose_name='G점수')
    fMentoScore = models.FloatField(default=0.0, verbose_name='H점수')
    fWarrantyScore = models.FloatField(default=0.0, verbose_name='I점수')
    fSafeScore = models.FloatField(default=0.0, verbose_name='J점수')
    fSpecialScore = models.FloatField(default=0.0, verbose_name='K점수')

    # 제외 여부
    bExcept = models.BooleanField(default=False, verbose_name='평가제외업체 여부')

    # 자동 생성 필드
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일시')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일시')

    class Meta:
        db_table = 'evaluation'
        verbose_name = '업체평가'
        verbose_name_plural = '업체평가'
        ordering = ['-fTotalScore', '-no']

    def __str__(self):
        return f"업체평가 {self.no} - 업체{self.noCompany} ({self.fTotalScore}점)"

    def get_company_name(self):
        """업체명 반환"""
        try:
            from company.models import Company
            company = Company.objects.get(no=self.noCompany)
            return company.sCompanyName or f"업체{self.noCompany}"
        except:
            return f"업체{self.noCompany}"

    def get_grade_display(self):
        """등급 표시"""
        grade_map = {1: "A급", 2: "B급", 3: "C급", 4: "D급"}
        return grade_map.get(self.nGrade, f"{self.nGrade}급")

    def get_performance_summary(self):
        """실적 요약"""
        return {
            'total_work': self.nSum,
            'contract_rate': self.fPercent,
            'contracts': self.nContract,
            'returns': self.nReturn,
            'cancels': self.nCancel
        }

    def calculate_contract_rate(self):
        """계약률 계산"""
        if self.nSum > 0:
            return round((self.nContract / self.nSum) * 100, 2)
        return 0.0

    def is_excellent_company(self):
        """우수업체 여부"""
        return self.fTotalScore >= 80.0 and not self.bWeak

    def get_rank_info(self):
        """순위 정보 (같은 평가회차 내에서)"""
        higher_scores = Evaluation.objects.filter(
            noEvaluationNo=self.noEvaluationNo,
            fTotalScore__gt=self.fTotalScore,
            bExcept=False
        ).count()
        return higher_scores + 1


class YearEvaluation(models.Model):
    """년간업체평가(YearEvaluation) 모델"""

    # 수상 구분 선택지
    AWARD_CHOICES = [
        ('대상', '대상'),
        ('최우수상', '최우수상'),
        ('우수상', '우수상'),
        ('장려상', '장려상'),
        ('참여상', '참여상'),
    ]

    # 기본 정보
    no = models.AutoField(primary_key=True, verbose_name='년간업체평가ID')
    nYear = models.IntegerField(verbose_name='평가 기준년도')
    noCompany = models.IntegerField(verbose_name='업체ID')

    # 평가 결과
    fScore = models.FloatField(default=0.0, verbose_name='종합점수')
    nRank = models.IntegerField(default=0, verbose_name='순위')
    sAward = models.CharField(
        max_length=20,
        choices=AWARD_CHOICES,
        blank=True,
        verbose_name='상패구분'
    )

    # 자동 생성 필드
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일시')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일시')

    class Meta:
        db_table = 'year_evaluation'
        verbose_name = '년간업체평가'
        verbose_name_plural = '년간업체평가'
        ordering = ['nYear', 'nRank']
        unique_together = ['nYear', 'noCompany']  # 연도별 업체당 하나의 평가

    def __str__(self):
        return f"{self.nYear}년 업체평가 {self.nRank}위 - 업체{self.noCompany}"

    def get_company_name(self):
        """업체명 반환"""
        try:
            from company.models import Company
            company = Company.objects.get(no=self.noCompany)
            return company.sCompanyName or f"업체{self.noCompany}"
        except:
            return f"업체{self.noCompany}"

    def get_award_display_with_icon(self):
        """상패 표시 (아이콘 포함)"""
        award_icons = {
            '대상': '🏆',
            '최우수상': '🥇',
            '우수상': '🥈',
            '장려상': '🥉',
            '참여상': '🎖️'
        }
        icon = award_icons.get(self.sAward, '')
        return f"{icon} {self.sAward}" if self.sAward else ""

    def is_top_performer(self):
        """상위 성과자 여부 (10위 이내)"""
        return self.nRank <= 10

    def get_percentile_rank(self):
        """백분위 순위"""
        total_companies = YearEvaluation.objects.filter(nYear=self.nYear).count()
        if total_companies > 0:
            return round((self.nRank / total_companies) * 100, 1)
        return 0.0
