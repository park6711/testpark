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

    # 공지일
    dateNotice = models.DateField(null=True, blank=True, verbose_name='공지일')

    # 계약률 정보
    fAverageAll = models.FloatField(default=0.0, verbose_name='평균계약률')
    fAverageExcel = models.FloatField(default=0.0, verbose_name='우수업체 평균계약률')

    # 예약문자 일시 정보
    timeExcel = models.DateTimeField(null=True, blank=True, verbose_name='우수업체 예약문자일시')
    timeWeak = models.DateTimeField(null=True, blank=True, verbose_name='미진업체 예약문자일시')

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


    def is_evaluation_period_active(self):
        """현재가 평가 기간 내인지 확인"""
        today = timezone.localtime().date()
        return self.dateStart <= today <= self.dateEnd


    def get_period_status(self):
        """기간 상태 반환"""
        today = timezone.localtime().date()

        if today < self.dateStart:
            return "대기"
        elif self.dateStart <= today <= self.dateEnd:
            return "평가중"
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
        """예약문자 일시 정보 표시"""
        excel_time = self.timeExcel.strftime('%Y-%m-%d %H:%M') if self.timeExcel else '미설정'
        weak_time = self.timeWeak.strftime('%Y-%m-%d %H:%M') if self.timeWeak else '미설정'
        return {
            'excel': excel_time,
            'weak': weak_time
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
            'notice_date': self.dateNotice if self.dateNotice else '미정',
            'status': self.get_period_status(),
            'progress': f"{self.get_progress_percentage()}%",
            'average_all': self.get_formatted_average_all(),
            'average_excel': self.get_formatted_average_excel(),
            'improvement': f"{self.get_average_improvement():.2f}%"
        }


# FixFee 모델은 fixfee 앱으로 이동됨


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
