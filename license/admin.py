from django.contrib import admin
from .models import License


@admin.register(License)
class LicenseAdmin(admin.ModelAdmin):
    list_display = [
        'no', 'noCompany', 'sCompanyName', 'sLicenseNo',
        'sCeoName', 'sAccount', 'created_at'
    ]
    list_filter = ['created_at']
    search_fields = ['sCompanyName', 'sCeoName', 'sLicenseNo', 'sAccount']
    ordering = ['-no']

    fieldsets = (
        ('기본 정보', {
            'fields': ('noCompany', 'sCompanyName', 'sLicenseNo', 'sCeoName')
        }),
        ('계좌 정보', {
            'fields': ('sAccountMail', 'sAccount')
        }),
        ('파일 정보', {
            'fields': ('fileLicense', 'fileAccount')
        }),
    )
