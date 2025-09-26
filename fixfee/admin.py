from django.contrib import admin
from .models import FixFee, FixFeeDate


@admin.register(FixFeeDate)
class FixFeeDateAdmin(admin.ModelAdmin):
    """FixFeeDate 관리자 페이지 설정"""

    list_display = [
        'no',
        'get_formatted_date',
        'get_year',
        'get_month',
        'get_fees_count',
        'get_paid_count',
        'get_unpaid_count',
    ]

    list_filter = [
        'date',
    ]

    search_fields = [
        'date',
    ]

    ordering = ['no']

    list_per_page = 50

    def get_formatted_date(self, obj):
        """날짜 포맷팅"""
        return obj.date.strftime('%Y년 %m월 %d일')
    get_formatted_date.short_description = '납부기준일'

    def get_year(self, obj):
        """연도 표시"""
        return f'{obj.date.year}년'
    get_year.short_description = '연도'

    def get_month(self, obj):
        """월 표시"""
        return f'{obj.date.month}월'
    get_month.short_description = '월'

    def get_fees_count(self, obj):
        """해당 기준일의 고정비 총 건수"""
        from .models import FixFee
        count = FixFee.objects.filter(noFixFeeDate=obj.no).count()
        return count
    get_fees_count.short_description = '전체건수'

    def get_paid_count(self, obj):
        """해당 기준일의 완납 건수"""
        from .models import FixFee
        count = FixFee.objects.filter(noFixFeeDate=obj.no, dateDeposit__isnull=False).count()
        if count > 0:
            return f'<span style="color:green;font-weight:bold;">{count}</span>'
        return count
    get_paid_count.short_description = '완납건수'
    get_paid_count.allow_tags = True

    def get_unpaid_count(self, obj):
        """해당 기준일의 미납 건수"""
        from .models import FixFee
        count = FixFee.objects.filter(noFixFeeDate=obj.no, dateDeposit__isnull=True).count()
        if count > 0:
            return f'<span style="color:red;font-weight:bold;">{count}</span>'
        return count
    get_unpaid_count.short_description = '미납건수'
    get_unpaid_count.allow_tags = True


@admin.register(FixFee)
class FixFeeAdmin(admin.ModelAdmin):
    """FixFee 관리자 페이지 설정"""

    list_display = [
        'no',
        'get_company_display',
        'get_fee_date_display',
        'dateDeposit',
        'formatted_fee',
        'get_payment_type_display',
        'payment_status_badge',
        'due_status_badge',
        'created_at'
    ]

    list_filter = [
        'dateDeposit',
        'nType',
        'created_at'
    ]

    search_fields = [
        'noCompany',
        'sMemo'
    ]

    ordering = ['-noFixFeeDate', '-no']

    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('기본 정보', {
            'fields': ('noCompany', 'noFixFeeDate')
        }),
        ('납부 정보', {
            'fields': ('dateDeposit', 'nFixFee', 'nType')
        }),
        ('추가 정보', {
            'fields': ('sMemo',)
        }),
        ('시스템 정보', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    def get_company_display(self, obj):
        """업체명 표시"""
        return obj.get_company_name()
    get_company_display.short_description = '업체명'

    def get_fee_date_display(self, obj):
        """납부기준일 표시"""
        fee_date = obj.get_fix_fee_date()
        return fee_date if fee_date else '-'
    get_fee_date_display.short_description = '납부기준일'

    def formatted_fee(self, obj):
        """고정비 포맷팅"""
        return obj.get_formatted_fee()
    formatted_fee.short_description = '월고정비'

    def get_payment_type_display(self, obj):
        """납부방식 표시"""
        return obj.get_payment_type_display_custom()
    get_payment_type_display.short_description = '납부방식'

    def payment_status_badge(self, obj):
        """납부 상태 배지"""
        status = obj.get_payment_status()
        colors = {
            '완납': 'green',
            '미납': 'red'
        }
        color = colors.get(status, 'gray')
        return f'<span style="background-color:{color};color:white;padding:3px 6px;border-radius:3px;">{status}</span>'
    payment_status_badge.short_description = '납부상태'
    payment_status_badge.allow_tags = True

    def due_status_badge(self, obj):
        """기한 상태 배지"""
        status = obj.get_due_status()
        if '연체' in status:
            color = 'red'
        elif '임박' in status:
            color = 'orange'
        elif '당일' in status:
            color = 'yellow'
        elif '완료' in status:
            color = 'green'
        else:
            color = 'blue'
        return f'<span style="background-color:{color};padding:3px 6px;border-radius:3px;">{status}</span>'
    due_status_badge.short_description = '기한상태'
    due_status_badge.allow_tags = True

    def get_queryset(self, request):
        """연체 건수 우선 표시"""
        qs = super().get_queryset(request)
        return qs.select_related()

    actions = ['mark_as_paid_action']

    def mark_as_paid_action(self, request, queryset):
        """선택한 항목 완납 처리"""
        count = 0
        for fee in queryset:
            if not fee.dateDeposit:
                fee.mark_as_paid()
                count += 1
        self.message_user(request, f'{count}건이 완납 처리되었습니다.')
    mark_as_paid_action.short_description = '선택한 항목 완납 처리'