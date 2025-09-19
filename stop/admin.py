from django.contrib import admin
from .models import Stop


@admin.register(Stop)
class StopAdmin(admin.ModelAdmin):
    """Stop 관리자 페이지"""

    list_display = [
        'no', 'noCompany', 'get_company_name', 'dateStart', 'dateEnd',
        'get_status_display', 'get_show_display', 'sWorker', 'time'
    ]
    list_filter = ['bShow', 'dateStart', 'dateEnd', 'sWorker']
    search_fields = ['noCompany', 'sStop', 'sWorker']
    date_hierarchy = 'dateStart'
    ordering = ['-no']

    fieldsets = (
        ('기본 정보', {
            'fields': ('noCompany', 'sWorker')
        }),
        ('일시정지 기간', {
            'fields': ('dateStart', 'dateEnd')
        }),
        ('세부 정보', {
            'fields': ('sStop', 'bShow')
        }),
        ('시스템 정보', {
            'fields': ('time', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ['time', 'created_at', 'updated_at']

    def get_company_name(self, obj):
        """업체명 표시"""
        return obj.get_company_name()
    get_company_name.short_description = '업체명'

    def get_status_display(self, obj):
        """상태 표시"""
        return obj.get_status_display()
    get_status_display.short_description = '상태'

    def get_show_display(self, obj):
        """공개여부 표시"""
        return obj.get_show_display()
    get_show_display.short_description = '공개여부'

# Register your models here.
