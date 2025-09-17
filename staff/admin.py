from django.contrib import admin
from .models import Staff


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ['no', 'sName', 'sTeam', 'sTitle', 'nMaster', 'bApproval']
    list_filter = ['nMaster', 'bApproval', 'sTeam']
    search_fields = ['sName', 'sNaverID', 'sTeam']
    ordering = ['no']

    fieldsets = (
        ('기본 정보', {
            'fields': ('sNaverID0', 'sNaverID', 'sName', 'sTeam', 'sTitle', 'sNick')
        }),
        ('연락처', {
            'fields': ('sPhone1', 'sPhone2', 'sGoogleID')
        }),
        ('권한 설정', {
            'fields': ('bApproval', 'nMaster')
        }),
        ('세부 권한', {
            'fields': ('nStaffAuthority', 'nCompanyAuthority', 'nOrderAuthority', 'nContractAuthority', 'nEvaluationAuthority')
        }),
    )