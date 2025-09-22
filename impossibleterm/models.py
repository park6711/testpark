from django.db import models
from django.utils import timezone


class ImpossibleTerm(models.Model):
    """공사 불가능 기간 모델"""

    # 기본 정보
    no = models.AutoField(primary_key=True, help_text="공사 불가능 기간 ID")
    noCompany = models.IntegerField(help_text="업체 ID")
    time = models.DateTimeField(auto_now_add=True, help_text="입력일시")

    # 공사 불가능 기간
    dateStart = models.DateField(help_text="시작일")
    dateEnd = models.DateField(help_text="종료일", null=True, blank=True)

    # 설정자
    sWorker = models.CharField(max_length=100, help_text="설정자")

    # 자동 생성 필드
    created_at = models.DateTimeField(auto_now_add=True, help_text="생성일시")
    updated_at = models.DateTimeField(auto_now=True, help_text="수정일시")

    class Meta:
        db_table = 'impossibleterm'
        verbose_name = '공사 불가능 기간'
        verbose_name_plural = '공사 불가능 기간'
        ordering = ['-no']  # 최신순 정렬

    def __str__(self):
        return f"{self.no} - 업체{self.noCompany} ({self.dateStart} ~ {self.dateEnd})"

    def get_company_name(self):
        """연결된 업체명 반환"""
        try:
            from company.models import Company
            company = Company.objects.filter(no=self.noCompany).first()
            if company:
                # sName2가 있으면 사용, 없으면 sName1 사용
                return company.sName2 or company.sName1 or f"업체{self.noCompany}"
            else:
                return f"업체{self.noCompany}"
        except:
            return f"업체{self.noCompany}"

    def is_active(self):
        """현재 공사불가능 상태인지 확인"""
        today = timezone.localtime().date()
        return self.dateStart <= today <= self.dateEnd

    def get_status_display(self):
        """상태 표시용 텍스트 반환"""
        today = timezone.localtime().date()

        if self.dateStart > today:
            return "예정"
        elif self.dateEnd and self.dateEnd < today:
            return "해제"
        else:
            return "적용 중"

    def get_duration_days(self):
        """총 기간 일수 계산"""
        if self.dateEnd:
            return (self.dateEnd - self.dateStart).days + 1
        else:
            return None