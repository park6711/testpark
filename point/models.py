from django.db import models
from django.utils import timezone
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from company.models import Company
from contract.models import CompanyReport


class Point(models.Model):
    TYPE_CHOICES = [
        (0, '기타'),
        (1, '취소환불액'),
        (2, '과/미입금'),
        (3, '페이백 적립'),
        (4, '닷컴포인트 전환'),
        (5, '포인트 소멸'),
    ]

    no = models.AutoField(primary_key=True, verbose_name='포인트내역ID')
    noCompany = models.ForeignKey(
        Company,
        on_delete=models.SET_NULL,  # Company 삭제 시 NULL로 설정
        null=True,  # NULL 허용
        blank=True,
        verbose_name='업체ID',
        related_name='point_records',
        db_column='noCompany'  # 기존 컬럼명 유지
    )
    time = models.DateTimeField(default=timezone.now, verbose_name='타임스탬프')
    nType = models.IntegerField(choices=TYPE_CHOICES, default=0, verbose_name='구분')
    noCompanyReport = models.ForeignKey(
        CompanyReport,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='업체계약보고ID',
        related_name='point_records'
    )
    sWorker = models.CharField(max_length=50, blank=True, verbose_name='작업자')
    nPrePoint = models.IntegerField(default=0, verbose_name='이전 포인트')
    nUsePoint = models.IntegerField(default=0, verbose_name='사용 포인트')
    nRemainPoint = models.IntegerField(default=0, verbose_name='잔액 포인트')
    sMemo = models.TextField(blank=True, verbose_name='메모')

    class Meta:
        verbose_name = '포인트'
        verbose_name_plural = '포인트'
        db_table = 'point'
        ordering = ['-time', '-no']

    def __str__(self):
        company_name = self.noCompany.sName2 if self.noCompany else '삭제된 업체'
        return f"포인트 {self.no} - {company_name} ({self.get_nType_display()})"

    def get_type_display_with_icon(self):
        """포인트 타입을 아이콘과 함께 표시"""
        icons = {
            0: '🔄',  # 기타
            1: '💰',  # 취소환불액
            2: '⚖️',  # 과/미입금
            3: '📈',  # 페이백 적립
            4: '🔄',  # 닷컴포인트 전환
            5: '❌',  # 포인트 소멸
        }
        icon = icons.get(self.nType, '🔄')
        return format_html(
            '<span title="{}">{} {}</span>',
            self.get_nType_display(),
            icon,
            self.get_nType_display()
        )

    def get_type_display_with_color(self):
        """포인트 타입을 색상과 함께 표시"""
        colors = {
            0: '#6c757d',  # 기타 - 회색
            1: '#28a745',  # 취소환불액 - 초록
            2: '#ffc107',  # 과/미입금 - 노랑
            3: '#007bff',  # 페이백 적립 - 파랑
            4: '#17a2b8',  # 닷컴포인트 전환 - 청록
            5: '#dc3545',  # 포인트 소멸 - 빨강
        }
        return {
            'type': self.get_nType_display(),
            'color': colors.get(self.nType, '#6c757d')
        }

    def get_point_change(self):
        """포인트 변동량 계산"""
        return self.nRemainPoint - self.nPrePoint

    def get_point_change_display(self):
        """포인트 변동량을 색상과 함께 표시"""
        change = self.get_point_change()
        if change > 0:
            return format_html(
                '<span style="color: #28a745; font-weight: bold;">+{}</span>',
                f'{change:,}'
            )
        elif change < 0:
            return format_html(
                '<span style="color: #dc3545; font-weight: bold;">{}</span>',
                f'{change:,}'
            )
        else:
            return format_html(
                '<span style="color: #6c757d;">0</span>'
            )

    def get_company_name(self):
        """업체명 반환"""
        return self.noCompany.sName1 if self.noCompany else 'N/A'

    def get_company_report_info(self):
        """업체계약보고 정보 반환"""
        if self.noCompanyReport:
            return f"계약보고 {self.noCompanyReport.no} - {self.noCompanyReport.get_nType_display()}"
        return 'N/A'

    def get_point_summary(self):
        """포인트 요약 정보"""
        return {
            'point_id': self.no,
            'company_name': self.get_company_name(),
            'type': self.get_nType_display(),
            'type_info': self.get_type_display_with_color(),
            'worker': self.sWorker or 'N/A',
            'pre_point': self.nPrePoint,
            'use_point': self.nUsePoint,
            'remain_point': self.nRemainPoint,
            'point_change': self.get_point_change(),
            'company_report': self.get_company_report_info(),
            'memo': self.sMemo or 'N/A',
            'timestamp': self.time.strftime('%Y-%m-%d %H:%M:%S')
        }

    def is_point_increase(self):
        """포인트 증가 여부"""
        return self.get_point_change() > 0

    def is_point_decrease(self):
        """포인트 감소 여부"""
        return self.get_point_change() < 0

    def get_memo_preview(self, length=50):
        """메모 미리보기"""
        if not self.sMemo:
            return 'N/A'
        if len(self.sMemo) <= length:
            return self.sMemo
        return f"{self.sMemo[:length]}..."

    @classmethod
    def get_company_current_points(cls, company):
        """업체의 현재 포인트 조회"""
        latest_record = cls.objects.filter(noCompany=company).first()
        return latest_record.nRemainPoint if latest_record else 0

    @classmethod
    def get_company_point_history(cls, company, limit=10):
        """업체의 포인트 히스토리 조회"""
        return cls.objects.filter(noCompany=company)[:limit]

    @classmethod
    def get_type_statistics(cls):
        """타입별 통계"""
        from django.db.models import Count, Sum
        return cls.objects.values('nType').annotate(
            count=Count('no'),
            total_use=Sum('nUsePoint'),
            total_change=Sum('nRemainPoint') - Sum('nPrePoint')
        ).order_by('nType')
