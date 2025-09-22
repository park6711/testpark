from django.contrib import admin
from .models import Company, ContractFile

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('no', 'sCompanyName', 'sName1', 'nType', 'nCondition', 'nLevel', 'nGrade', 'nApplyGrade')
    list_filter = ('nType', 'nCondition', 'nLevel', 'nGrade', 'nApplyGrade')
    search_fields = ('sCompanyName', 'sName1', 'sName2', 'sName3')
    readonly_fields = ('no',)

    fieldsets = (
        ('기본 정보', {
            'fields': ('no', 'sName1', 'sName2', 'sName3', 'sNaverID', 'sCompanyName', 'nType', 'nCondition')
        }),
        ('연락처 정보', {
            'fields': ('sAddress', 'sCeoName', 'sCeoPhone', 'sCeoMail', 'sSaleName', 'sSalePhone', 'sSaleMail',
                      'sAccoutName', 'sAccoutPhone', 'sAccoutMail', 'sEmergencyName', 'sEmergencyPhone', 'sEmergencyRelation')
        }),
        ('업체 상세', {
            'fields': ('noMemberMaster', 'noLicenseRepresent', 'nMember', 'sBuildLicense', 'sStrength')
        }),
        ('재정 정보', {
            'fields': ('dateJoin', 'nJoinFee', 'nDeposit', 'nFixFee', 'dateFixFeeStart', 'fFeePercent', 'nOrderFee', 'nReportPeriod', 'nRefund')
        }),
        ('서비스 분야', {
            'fields': ('bAptAll', 'bAptPart', 'bHouseAll', 'bHousePart', 'bCommerceAll', 'bCommercePart', 'bBuild', 'bExtra')
        }),
        ('할당 및 평가', {
            'fields': ('nLevel', 'nGrade', 'nApplyGrade', 'sApplyGradeReason', 'nAssignAll2', 'nAssignPart2',
                      'nAssignAllTerm', 'nAssignPartTerm', 'nAssignMax', 'fAssignPercent', 'fAssignLack')
        }),
        ('일시정지', {
            'fields': ('sStop', 'dateStopStart', 'dateStopEnd')
        }),
        ('기타', {
            'fields': ('bPrivacy', 'bCompetition', 'bUnion', 'bMentor', 'sMentee', 'sManager', 'sMemo')
        }),
        ('탈퇴', {
            'fields': ('dateWithdraw', 'sWithdraw')
        }),
        ('파일', {
            'fields': ('fileBuildLicense', 'fileCeo', 'fileSale', 'fileLicense', 'fileCampaignAgree')
        }),
        ('기타 정보', {
            'fields': ('sPicture', 'sGallery', 'sEstimate')
        })
    )

@admin.register(ContractFile)
class ContractFileAdmin(admin.ModelAdmin):
    list_display = ('company', 'name', 'uploaded_at')
    list_filter = ('uploaded_at',)
    search_fields = ('company__sCompanyName', 'name')
