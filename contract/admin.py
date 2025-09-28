from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.http import HttpResponse
import csv
from .models import CompanyReport, ClientReport


@admin.register(CompanyReport)
class CompanyReportAdmin(admin.ModelAdmin):
    list_display = [
        'no',
        'get_type_badge',
        'sName',
        'get_company_name',
        'get_construction_type_short',
        'nConMoney',
        'nFee',
        'get_profit_margin_display',
        'dateContract',
        'dateSchedule',
        'get_schedule_status_badge',
        'is_paid',
        'time',
        'sWorker'
    ]

    list_filter = [
        'nType',
        'noConType',
        'bVat',
        'nRefund',
        'dateContract',
        'dateSchedule',
        'time',
        'sWorker'
    ]

    search_fields = [
        'no',
        'sName',
        'sPhone',
        'sArea',
        'sCompanyName',
        'sCompanyMemo',
        'sStaffMemo',
        'sWorker'
    ]

    readonly_fields = [
        'no',
        'time',
        'created_at',
        'updated_at',
        'get_company_name',
        'get_assign_info',
        'get_profit_margin_display',
        'get_money_summary_display',
        'get_schedule_status_badge',
        'get_contract_duration_display',
        'get_related_reports_display'
    ]

    fieldsets = (
        ('기본 정보', {
            'fields': ('no', 'time', 'noCompany', 'sWorker')
        }),
        ('보고 정보', {
            'fields': ('nType', 'noPre', 'noNext')
        }),
        ('공사 정보', {
            'fields': ('noConType', 'sPost', 'noAssign', 'sArea', 'dateContract', 'dateSchedule')
        }),
        ('고객 정보', {
            'fields': ('sName', 'sPhone')
        }),
        ('계약 정보', {
            'fields': ('nConMoney', 'bVat', 'get_contract_duration_display')
        }),
        ('수수료 및 정산', {
            'fields': ('nFee', 'nAppPoint', 'nDemand', 'get_profit_margin_display', 'get_money_summary_display')
        }),
        ('입금/환불 정보', {
            'fields': ('dateDeposit', 'nDeposit', 'nExcess', 'nRefund')
        }),
        ('업체 및 계좌 정보', {
            'fields': ('sCompanyName', 'sAccount')
        }),
        ('파일 및 메모', {
            'fields': ('file', 'sCompanyMemo', 'sStaffMemo')
        }),
        ('관련 정보', {
            'fields': ('get_company_name', 'get_assign_info', 'get_related_reports_display'),
            'classes': ('collapse',)
        }),
        ('시스템 정보', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    ordering = ['-no']
    list_per_page = 25

    actions = ['export_to_csv', 'mark_as_paid', 'mark_as_cancelled']

    def get_type_badge(self, obj):
        """보고구분 뱃지 표시"""
        type_info = obj.get_type_display_with_color()
        return format_html(
            '<span class="badge badge-{}">{}</span>',
            type_info['color'],
            type_info['type']
        )
    get_type_badge.short_description = '보고구분'

    def get_profit_margin_display(self, obj):
        """수익률 표시"""
        margin = obj.get_profit_margin()
        if margin > 15:
            color = 'green'
        elif margin > 10:
            color = 'orange'
        else:
            color = 'red'
        return format_html(
            '<span style="color: {};">{:.2f}%</span>',
            color,
            margin
        )
    get_profit_margin_display.short_description = '수익률'

    def get_schedule_status_badge(self, obj):
        """일정 상태 뱃지"""
        status = obj.get_schedule_status()
        if '지남' in status:
            color = 'red'
        elif '당일' in status:
            color = 'orange'
        elif '7일' in status:
            color = 'yellow'
        else:
            color = 'green'
        return format_html(
            '<span style="color: {};">{}</span>',
            color,
            status
        )
    get_schedule_status_badge.short_description = '일정상태'

    def get_money_summary_display(self, obj):
        """금액 요약 정보"""
        summary = obj.get_money_summary()
        return format_html(
            '계약: {:,}원<br>수수료: {:,}원<br>청구: {:,}원<br>입금: {:,}원<br>과/미입금: {:,}원',
            summary['contract_money'],
            summary['fee'],
            summary['demand'],
            summary['deposit'],
            summary['excess']
        )
    get_money_summary_display.short_description = '금액요약'

    def get_contract_duration_display(self, obj):
        """계약 기간 표시"""
        duration = obj.get_contract_duration()
        if duration:
            return f"{duration}일"
        return "기간 미정"
    get_contract_duration_display.short_description = '계약기간'

    def get_related_reports_display(self, obj):
        """관련 보고서 표시"""
        related = obj.get_related_reports()
        html = []
        if 'previous' in related:
            prev = related['previous']
            html.append(f"이전: 보고{prev.no} ({prev.get_nType_display()})")
        if 'next' in related:
            next_report = related['next']
            html.append(f"이후: 보고{next_report.no} ({next_report.get_nType_display()})")
        return mark_safe('<br>'.join(html)) if html else "관련 보고서 없음"
    get_related_reports_display.short_description = '관련보고서'

    def export_to_csv(self, request, queryset):
        """CSV 내보내기"""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="company_reports.csv"'
        response.write('\ufeff')  # UTF-8 BOM

        writer = csv.writer(response)
        writer.writerow([
            '보고ID', '보고일시', '업체ID', '보고구분', '공사유형', '고객명', '고객전화',
            '공사주소', '계약일', '완료예정일', '계약금액', 'VAT포함', '수수료', '청구액',
            '입금일', '입금액', '과/미입금', '수익률', '보고자', '메모'
        ])

        for obj in queryset:
            writer.writerow([
                obj.no, obj.time, obj.noCompany, obj.get_nType_display(),
                obj.get_noConType_display(), obj.sName, obj.sPhone, obj.sArea,
                obj.dateContract, obj.dateSchedule, obj.nConMoney, obj.get_vat_display(),
                obj.nFee, obj.nDemand, obj.dateDeposit, obj.nDeposit, obj.nExcess,
                f"{obj.get_profit_margin()}%", obj.sWorker, obj.sStaffMemo
            ])

        return response
    export_to_csv.short_description = "선택된 보고서를 CSV로 내보내기"

    def mark_as_paid(self, request, queryset):
        """입금 완료로 변경"""
        updated = 0
        for obj in queryset:
            if obj.nType in [1, 3]:  # 계약(입금X), 증액(입금X)
                obj.nType += 1  # 입금O로 변경
                obj.save()
                updated += 1

        self.message_user(request, f"{updated}개 보고서가 입금 완료로 변경되었습니다.")
    mark_as_paid.short_description = "선택된 보고서를 입금 완료로 변경"

    def mark_as_cancelled(self, request, queryset):
        """취소로 변경"""
        updated = 0
        for obj in queryset:
            if obj.nType < 7:  # 취소가 아닌 경우
                obj.nType = 7  # 취소(환불X)로 변경
                obj.save()
                updated += 1

        self.message_user(request, f"{updated}개 보고서가 취소로 변경되었습니다.")
    mark_as_cancelled.short_description = "선택된 보고서를 취소로 변경"

    def get_queryset(self, request):
        """쿼리셋 최적화"""
        return super().get_queryset(request).select_related()


@admin.register(ClientReport)
class ClientReportAdmin(admin.ModelAdmin):
    list_display = [
        'no',
        'timeStamp',
        'get_check_status_badge',
        'get_company_name',
        'sName',
        'sArea',
        'sConMoney',
        'dateContract',
        'get_phone_masked',
        'get_status_badge',
        'has_explanation',
        'has_punishment',
        'created_at'
    ]

    list_filter = [
        'nCheck',
        'timeStamp',
        'dateContract',
        'dateExplain0',
        'dateExplain1',
        'noCompany',
        'created_at'
    ]

    search_fields = [
        'no',
        'sCompanyName',
        'sName',
        'sPhone',
        'sArea',
        'sExplain',
        'sPunish',
        'sMemo',
        'sClientMemo'
    ]

    readonly_fields = [
        'no',
        'timeStamp',
        'created_at',
        'updated_at',
        'get_company_name',
        'get_status_display',
        'get_phone_masked',
        'get_report_summary_display',
        'get_check_status_badge',
        'get_company_report',
        'get_assign',
        'get_explain_days_remaining',
        'is_explain_overdue'
    ]

    fieldsets = (
        ('기본 정보', {
            'fields': ('no', 'timeStamp', 'nCheck', 'get_check_status_badge')
        }),
        ('업체 정보', {
            'fields': ('noCompany', 'sCompanyName', 'get_company_name')
        }),
        ('고객 정보', {
            'fields': ('sName', 'sPhone', 'get_phone_masked', 'sArea')
        }),
        ('계약 정보', {
            'fields': ('sConMoney', 'dateContract', 'sFile')
        }),
        ('메모 및 링크', {
            'fields': ('sClientMemo', 'sMemo', 'sPost')
        }),
        ('관련 정보', {
            'fields': ('noAssign', 'get_assign', 'noCompanyReport', 'get_company_report')
        }),
        ('소명 관련', {
            'fields': ('dateExplain0', 'dateExplain1', 'get_explain_days_remaining', 'is_explain_overdue', 'sExplain', 'sPunish')
        }),
        ('보고서 상태', {
            'fields': ('get_status_display', 'get_report_summary_display'),
            'classes': ('collapse',)
        }),
        ('시스템 정보', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    ordering = ['-no']
    list_per_page = 25

    actions = ['export_to_csv', 'mark_as_resolved']

    def get_check_status_badge(self, obj):
        """확인 상태 뱃지 표시"""
        status_info = obj.get_check_status_color()
        color_map = {
            'warning': '#FFC107',
            'secondary': '#6C757D',
            'success': '#28A745',
            'danger': '#DC3545'
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; border-radius: 4px;">{}</span>',
            color_map.get(status_info['color'], '#6C757D'),
            status_info['status']
        )
    get_check_status_badge.short_description = '확인상태'

    def get_status_badge(self, obj):
        """상태 뱃지 표시"""
        status = obj.get_status_display()
        if status == "징계":
            color = 'red'
        elif status == "소명":
            color = 'orange'
        elif status == "계약확정":
            color = 'green'
        elif status == "계약취소":
            color = 'darkred'
        elif status == "불필요":
            color = 'gray'
        else:
            color = 'blue'

        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            status
        )
    get_status_badge.short_description = '상태'

    def get_report_summary_display(self, obj):
        """보고서 요약 정보"""
        summary = obj.get_report_summary()
        return format_html(
            '업체: {}<br>고객: {}<br>소명: {}<br>징계: {}<br>보고일: {}',
            summary['company_name'],
            summary['client_name'],
            '있음' if summary['has_explanation'] else '없음',
            '있음' if summary['has_punishment'] else '없음',
            summary['report_date'] or '미정'
        )
    get_report_summary_display.short_description = '보고서요약'

    def export_to_csv(self, request, queryset):
        """CSV 내보내기"""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="client_reports.csv"'
        response.write('\ufeff')  # UTF-8 BOM

        writer = csv.writer(response)
        writer.writerow([
            '보고ID', '타임스탬프', '업체ID', '업체명', '고객명', '고객전화',
            '공사지역', '공사금액', '계약일', '확인상태', '메모', '소명예정일', '소명실제일',
            '소명내용', '징계내용', '상태', '생성일시'
        ])

        for obj in queryset:
            writer.writerow([
                obj.no, obj.timeStamp, obj.noCompany, obj.get_company_name(),
                obj.sName, obj.sPhone, obj.sArea, obj.sConMoney, obj.dateContract,
                obj.get_nCheck_display(), obj.sMemo, obj.dateExplain0, obj.dateExplain1,
                obj.sExplain, obj.sPunish, obj.get_status_display(), obj.created_at
            ])

        return response
    export_to_csv.short_description = "선택된 고객보고서를 CSV로 내보내기"

    def mark_as_resolved(self, request, queryset):
        """해결됨으로 표시 (징계 내용 추가)"""
        updated = 0
        for obj in queryset:
            if not obj.has_punishment():
                obj.sPunish = "해결됨 - 관리자 처리"
                obj.save()
                updated += 1

        self.message_user(request, f"{updated}개 보고서가 해결됨으로 표시되었습니다.")
    mark_as_resolved.short_description = "선택된 보고서를 해결됨으로 표시"