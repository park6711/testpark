from django.db import models
from django.utils import timezone


class Stop(models.Model):
    """일시정지 모델"""

    # 기본 정보
    no = models.AutoField(primary_key=True, help_text="일시정지 ID")
    noCompany = models.IntegerField(help_text="업체 ID")
    time = models.DateTimeField(auto_now_add=True, help_text="입력일시")

    # 일시정지 기간
    dateStart = models.DateField(help_text="시작일")
    dateEnd = models.DateField(help_text="종료일", null=True, blank=True)

    # 일시정지 세부 정보
    sStop = models.TextField(help_text="사유")
    bShow = models.BooleanField(default=True, help_text="공개 여부 (0: 비공개, 1: 공개)")
    sWorker = models.CharField(max_length=100, help_text="설정자")

    # 자동 생성 필드
    created_at = models.DateTimeField(auto_now_add=True, help_text="생성일시")
    updated_at = models.DateTimeField(auto_now=True, help_text="수정일시")

    class Meta:
        db_table = 'stop'
        verbose_name = '일시정지'
        verbose_name_plural = '일시정지'
        ordering = ['-no']  # 최신순 정렬

    def __str__(self):
        return f"{self.no} - 업체{self.noCompany} ({self.dateStart} ~ {self.dateEnd})"

    def get_company_name(self):
        """연결된 업체명 반환 (sName2 우선, 없으면 sName1)"""
        try:
            from company.models import Company
            company = Company.objects.get(no=self.noCompany)

            # sName2를 우선 사용, 없으면 sName1, 그것도 없으면 업체번호
            sname2 = getattr(company, 'sName2', None)
            sname1 = getattr(company, 'sName1', None)

            if sname2 and sname2.strip():
                return sname2
            elif sname1 and sname1.strip():
                return sname1
            else:
                return f"업체번호: {self.noCompany}"
        except Exception:
            return f"업체번호: {self.noCompany}"

    def is_active(self):
        """현재 일시정지 상태인지 확인"""
        today = timezone.localtime().date()
        return self.dateStart <= today <= self.dateEnd

    def get_status_display(self):
        """상태 표시 텍스트 반환"""
        today = timezone.localtime().date()
        if self.is_active():
            return "정지"
        elif today < self.dateStart:
            return "예정"
        else:
            return "해제"

    def get_show_display(self):
        """공개 여부 표시 텍스트 반환"""
        return "공개" if self.bShow else "비공개"

    def get_duration_days(self):
        """일시정지 총 기간 일수 반환 (+1일로 계산)"""
        return (self.dateEnd - self.dateStart).days + 1

    def save(self, *args, **kwargs):
        """모델 저장 시 종료일 자동 설정"""
        if not self.dateEnd:
            # 종료일이 설정되지 않은 경우 2099년 오늘 날짜로 설정 (한국 시간 기준)
            today = timezone.localtime().date()
            from datetime import date
            self.dateEnd = date(2099, today.month, today.day)
        super().save(*args, **kwargs)

# Create your models here.
