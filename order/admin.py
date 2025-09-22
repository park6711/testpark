from django.contrib import admin
from .models import Order, Assign, Estimate, AssignMemo


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('no', 'sName', 'sPhone', 'sArea', 'dateSchedule', 'get_privacy_status', 'time')
    list_filter = ('bPrivacy1', 'bPrivacy2', 'dateSchedule', 'time')
    search_fields = ('sName', 'sPhone', 'sNaverID', 'sNick', 'sArea', 'sConstruction')
    readonly_fields = ('no', 'time', 'created_at', 'updated_at')
    date_hierarchy = 'dateSchedule'

    fieldsets = (
        ('기본 정보', {
            'fields': ('no', 'time', 'sAppoint')
        }),
        ('고객 정보', {
            'fields': ('sName', 'sNick', 'sNaverID', 'sPhone')
        }),
        ('의뢰 내용', {
            'fields': ('sPost', 'sArea', 'dateSchedule', 'sConstruction')
        }),
        ('개인정보 동의', {
            'fields': ('bPrivacy1', 'bPrivacy2')
        }),
        ('시스템 정보', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    def get_privacy_status(self, obj):
        """개인정보 동의 상태 표시"""
        return obj.get_privacy_status()
    get_privacy_status.short_description = '동의상태'


@admin.register(Assign)
class AssignAdmin(admin.ModelAdmin):
    list_display = ('no', 'noOrder', 'get_company_name', 'get_construction_display_short',
                   'get_assign_type_display', 'get_appoint_display', 'sWorker', 'time')
    list_filter = ('nConstructionType', 'nAssignType', 'nAppoint', 'time')
    search_fields = ('noOrder', 'noCompany', 'sCompanyPhone', 'sClientPhone', 'sWorker')
    readonly_fields = ('no', 'time', 'created_at', 'updated_at')
    date_hierarchy = 'time'

    fieldsets = (
        ('기본 정보', {
            'fields': ('no', 'noOrder', 'noCompany', 'time')
        }),
        ('공사 및 할당 정보', {
            'fields': ('nConstructionType', 'nAssignType', 'nAppoint')
        }),
        ('연락처 정보', {
            'fields': ('sCompanyPhone', 'sClientPhone')
        }),
        ('메시지 내용', {
            'fields': ('sCompanySMS', 'sClientSMS'),
            'classes': ('collapse',)
        }),
        ('관리 정보', {
            'fields': ('sWorker', 'noCompanyReport')
        }),
        ('지역 정보', {
            'fields': ('noGonggu', 'noArea')
        }),
        ('시스템 정보', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    def get_company_name(self, obj):
        """업체명 표시"""
        return obj.get_company_name()
    get_company_name.short_description = '업체명'

    def get_construction_display_short(self, obj):
        """공사종류 짧은 표시"""
        return obj.get_construction_display_short()
    get_construction_display_short.short_description = '공사종류'

    def get_assign_type_display(self, obj):
        """할당상태 표시"""
        return obj.get_nAssignType_display()
    get_assign_type_display.short_description = '할당상태'

    def get_appoint_display(self, obj):
        """지정종류 표시"""
        return obj.get_nAppoint_display()
    get_appoint_display.short_description = '지정종류'


@admin.register(Estimate)
class EstimateAdmin(admin.ModelAdmin):
    list_display = ('no', 'noOrder', 'noAssign', 'get_company_name', 'get_client_name',
                   'get_construction_type', 'sPost', 'time')
    list_filter = ('time',)
    search_fields = ('noOrder', 'noAssign', 'sPost')
    readonly_fields = ('no', 'time', 'created_at', 'updated_at')
    date_hierarchy = 'time'

    fieldsets = (
        ('기본 정보', {
            'fields': ('no', 'noOrder', 'noAssign', 'time')
        }),
        ('견적 내용', {
            'fields': ('sPost',)
        }),
        ('연결 정보', {
            'fields': ('get_summary_display',),
            'classes': ('collapse',)
        }),
        ('시스템 정보', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    def get_company_name(self, obj):
        """업체명 표시"""
        return obj.get_company_name()
    get_company_name.short_description = '업체명'

    def get_client_name(self, obj):
        """고객명 표시"""
        return obj.get_client_name()
    get_client_name.short_description = '고객명'

    def get_construction_type(self, obj):
        """공사종류 표시"""
        return obj.get_construction_type()
    get_construction_type.short_description = '공사종류'

    def get_summary_display(self, obj):
        """견적 요약 표시"""
        return obj.get_summary()
    get_summary_display.short_description = '견적 요약'


@admin.register(AssignMemo)
class AssignMemoAdmin(admin.ModelAdmin):
    list_display = ('no', 'noOrder', 'noAssign', 'get_company_name', 'get_client_name',
                   'sWorker', 'get_memo_preview', 'get_important_indicator', 'time')
    list_filter = ('sWorker', 'time')
    search_fields = ('noOrder', 'noAssign', 'sWorker', 'sMemo')
    readonly_fields = ('no', 'time', 'created_at', 'updated_at')
    date_hierarchy = 'time'

    fieldsets = (
        ('기본 정보', {
            'fields': ('no', 'noOrder', 'noAssign', 'time')
        }),
        ('메모 내용', {
            'fields': ('sWorker', 'sMemo')
        }),
        ('연결 정보', {
            'fields': ('get_summary_display', 'get_assign_status_display'),
            'classes': ('collapse',)
        }),
        ('시스템 정보', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    def get_company_name(self, obj):
        """업체명 표시"""
        return obj.get_company_name()
    get_company_name.short_description = '업체명'

    def get_client_name(self, obj):
        """고객명 표시"""
        return obj.get_client_name()
    get_client_name.short_description = '고객명'

    def get_memo_preview(self, obj):
        """메모 미리보기 표시"""
        return obj.get_memo_preview()
    get_memo_preview.short_description = '메모 미리보기'

    def get_important_indicator(self, obj):
        """중요 메모 표시"""
        return "🔥" if obj.is_important() else ""
    get_important_indicator.short_description = '중요'

    def get_summary_display(self, obj):
        """메모 요약 표시"""
        return obj.get_summary()
    get_summary_display.short_description = '메모 요약'

    def get_assign_status_display(self, obj):
        """할당 상태 표시"""
        return obj.get_assign_status()
    get_assign_status_display.short_description = '할당 상태'
