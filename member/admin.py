from django.contrib import admin
from .models import Member


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = [
        'no', 'sName', 'sCompanyName', 'sNaverID', 'bApproval',
        'nCompanyAuthority', 'nOrderAuthority', 'nContractAuthority', 'nEvaluationAuthority'
    ]
    list_filter = [
        'bApproval', 'nCafeGrade', 'nCompanyAuthority', 'nOrderAuthority',
        'nContractAuthority', 'nEvaluationAuthority', 'created_at'
    ]
    search_fields = ['sName', 'sCompanyName', 'sNaverID', 'nNick']
    readonly_fields = ['no', 'created_at', 'updated_at']

    fieldsets = (
        ('기본 정보', {
            'fields': ('no', 'sNaverID0', 'bApproval', 'sNaverID')
        }),
        ('회원 정보', {
            'fields': ('sName', 'sName2', 'sCompanyName', 'noCompany', 'sPhone', 'nCafeGrade', 'nNick')
        }),
        ('권한 설정', {
            'fields': ('nCompanyAuthority', 'nOrderAuthority', 'nContractAuthority', 'nEvaluationAuthority')
        }),
        ('시스템 정보', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    ordering = ['no']
