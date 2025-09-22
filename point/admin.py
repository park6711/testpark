from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.http import HttpResponse
import csv
from .models import Point


@admin.register(Point)
class PointAdmin(admin.ModelAdmin):
    list_display = [
        'no',
        'get_company_name_display',
        'get_type_display_with_icon',
        'sWorker',
        'get_point_change_display',
        'get_pre_point_formatted',
        'get_use_point_formatted',
        'get_remain_point_formatted',
        'get_company_report_display',
        'get_memo_preview_display',
        'time'
    ]

    list_filter = [
        'nType',
        'time',
        'noCompany',
        'sWorker'
    ]

    search_fields = [
        'no',
        'noCompany__sName1',
        'sWorker',
        'sMemo',
        'noCompanyReport__no'
    ]

    readonly_fields = [
        'no',
        'time',
        'get_point_change',
        'get_point_summary_display',
        'get_company_point_history_display'
    ]

    fieldsets = (
        ('기본 정보', {
            'fields': ('no', 'time')
        }),
        ('포인트 정보', {
            'fields': ('noCompany', 'nType', 'sWorker')
        }),
        ('포인트 내역', {
            'fields': ('nPrePoint', 'nUsePoint', 'nRemainPoint', 'get_point_change')
        }),
        ('연관 정보', {
            'fields': ('noCompanyReport', 'sMemo')
        }),
        ('상세 정보', {
            'fields': ('get_point_summary_display', 'get_company_point_history_display'),
            'classes': ('collapse',)
        })
    )

    ordering = ['-time', '-no']
    list_per_page = 25

    actions = ['export_to_csv', 'calculate_company_totals']

    def get_company_name_display(self, obj):
        """업체명 표시"""
        return obj.get_company_name()
    get_company_name_display.short_description = '업체명'

    def get_type_display_with_icon(self, obj):
        """포인트 타입 아이콘 표시"""
        return obj.get_type_display_with_icon()
    get_type_display_with_icon.short_description = '구분'

    def get_point_change_display(self, obj):
        """포인트 변동량 표시"""
        return obj.get_point_change_display()
    get_point_change_display.short_description = '변동량'

    def get_pre_point_formatted(self, obj):
        """이전 포인트 포맷팅"""
        return format_html(
            '<span style="color: #6c757d;">{:,}</span>',
            obj.nPrePoint
        )
    get_pre_point_formatted.short_description = '이전포인트'

    def get_use_point_formatted(self, obj):
        """사용 포인트 포맷팅"""
        if obj.nUsePoint > 0:
            return format_html(
                '<span style="color: #dc3545; font-weight: bold;">-{:,}</span>',
                obj.nUsePoint
            )
        return format_html(
            '<span style="color: #6c757d;">0</span>'
        )
    get_use_point_formatted.short_description = '사용포인트'

    def get_remain_point_formatted(self, obj):
        """잔액 포인트 포맷팅"""
        return format_html(
            '<span style="color: #28a745; font-weight: bold;">{:,}</span>',
            obj.nRemainPoint
        )
    get_remain_point_formatted.short_description = '잔액포인트'

    def get_company_report_display(self, obj):
        """업체계약보고 표시"""
        if obj.noCompanyReport:
            return format_html(
                '<a href="/admin/contract/companyreport/{}/change/" target="_blank">계약보고 {}</a>',
                obj.noCompanyReport.no,
                obj.noCompanyReport.no
            )
        return 'N/A'
    get_company_report_display.short_description = '계약보고'

    def get_memo_preview_display(self, obj):
        """메모 미리보기"""
        preview = obj.get_memo_preview(30)
        if obj.sMemo:
            return format_html('<span title="{}">{}</span>', obj.sMemo, preview)
        return 'N/A'
    get_memo_preview_display.short_description = '메모'

    def get_point_summary_display(self, obj):
        """포인트 요약 정보"""
        summary = obj.get_point_summary()
        return format_html(
            'ID: {}<br>'
            '업체: {}<br>'
            '구분: {}<br>'
            '작업자: {}<br>'
            '이전포인트: {:,}<br>'
            '사용포인트: {:,}<br>'
            '잔액포인트: {:,}<br>'
            '변동량: {:,}<br>'
            '계약보고: {}<br>'
            '메모: {}<br>'
            '시간: {}',
            summary['point_id'],
            summary['company_name'],
            summary['type'],
            summary['worker'],
            summary['pre_point'],
            summary['use_point'],
            summary['remain_point'],
            summary['point_change'],
            summary['company_report'],
            summary['memo'],
            summary['timestamp']
        )
    get_point_summary_display.short_description = '포인트요약'

    def get_company_point_history_display(self, obj):
        """업체 포인트 히스토리"""
        if not obj.noCompany:
            return "업체 정보가 없습니다."

        history = Point.get_company_point_history(obj.noCompany, 5)
        if not history:
            return "포인트 히스토리가 없습니다."

        html = []
        for point in history:
            html.append(
                f"포인트 {point.no}: {point.get_nType_display()} "
                f"({point.nPrePoint:,} → {point.nRemainPoint:,}) "
                f"{point.time.strftime('%Y-%m-%d %H:%M')}"
            )
        return mark_safe('<br>'.join(html))
    get_company_point_history_display.short_description = '업체포인트히스토리'

    def export_to_csv(self, request, queryset):
        """CSV 내보내기"""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="points.csv"'
        response.write('\ufeff')  # UTF-8 BOM

        writer = csv.writer(response)
        writer.writerow([
            '포인트ID', '업체명', '구분', '작업자', '이전포인트', '사용포인트',
            '잔액포인트', '변동량', '계약보고ID', '메모', '시간'
        ])

        for obj in queryset:
            writer.writerow([
                obj.no, obj.get_company_name(), obj.get_nType_display(),
                obj.sWorker, obj.nPrePoint, obj.nUsePoint, obj.nRemainPoint,
                obj.get_point_change(),
                obj.noCompanyReport.no if obj.noCompanyReport else 'N/A',
                obj.sMemo, obj.time
            ])

        return response
    export_to_csv.short_description = "선택된 포인트를 CSV로 내보내기"

    def calculate_company_totals(self, request, queryset):
        """업체별 포인트 합계 계산"""
        from django.db.models import Sum

        company_totals = {}
        for point in queryset:
            if point.noCompany:
                company_name = point.get_company_name()
                if company_name not in company_totals:
                    company_totals[company_name] = {
                        'total_use': 0,
                        'current_points': 0,
                        'record_count': 0
                    }

                company_totals[company_name]['total_use'] += point.nUsePoint
                company_totals[company_name]['current_points'] = point.nRemainPoint
                company_totals[company_name]['record_count'] += 1

        message_parts = []
        for company, totals in company_totals.items():
            message_parts.append(
                f"{company}: 사용 {totals['total_use']:,}pt, "
                f"잔액 {totals['current_points']:,}pt, "
                f"기록 {totals['record_count']}개"
            )

        self.message_user(
            request,
            f"업체별 포인트 현황: {'; '.join(message_parts)}"
        )
    calculate_company_totals.short_description = "선택된 포인트의 업체별 합계 계산"

    def get_queryset(self, request):
        """쿼리셋 최적화"""
        return super().get_queryset(request).select_related(
            'noCompany', 'noCompanyReport'
        )

    class Media:
        css = {
            'all': ('admin/css/point_admin.css',)
        }
        js = ('admin/js/point_admin.js',)
