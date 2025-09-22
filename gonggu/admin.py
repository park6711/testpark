from django.contrib import admin
from .models import Gonggu, GongguCompany, GongguArea


@admin.register(Gonggu)
class GongguAdmin(admin.ModelAdmin):
    list_display = ('no', 'get_name_preview', 'sNo', 'get_step_type_display', 'get_type_display_short',
                   'dateStart', 'dateEnd', 'get_remaining_days', 'get_popularity_level',
                   'get_comment_increase', 'nCommentNow')
    list_filter = ('nStepType', 'nType', 'dateStart', 'dateEnd')
    search_fields = ('sName', 'sNo', 'sPost', 'sStrength')
    readonly_fields = ('no', 'created_at', 'updated_at')
    date_hierarchy = 'dateStart'

    fieldsets = (
        ('기본 정보', {
            'fields': ('no', 'sNo', 'sName')
        }),
        ('진행 상태', {
            'fields': ('nStepType', 'nType')
        }),
        ('일정 정보', {
            'fields': ('dateStart', 'dateEnd')
        }),
        ('공구 내용', {
            'fields': ('sPost', 'sStrength')
        }),
        ('네이버 댓글 정보', {
            'fields': ('nCommentPre', 'nCommentNow', 'get_comment_stats'),
            'classes': ('collapse',)
        }),
        ('시스템 정보', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    def get_name_preview(self, obj):
        """공구이름 미리보기"""
        return obj.get_name_preview()
    get_name_preview.short_description = '공구이름'

    def get_step_type_display(self, obj):
        """진행구분 표시"""
        status_info = obj.get_status_display_with_color()
        return status_info['status']
    get_step_type_display.short_description = '진행구분'

    def get_type_display_short(self, obj):
        """구분 짧은 표시"""
        return obj.get_type_display_short()
    get_type_display_short.short_description = '구분'

    def get_remaining_days(self, obj):
        """남은 일수 표시"""
        return obj.get_remaining_days() or "-"
    get_remaining_days.short_description = '마감일 상태'

    def get_popularity_level(self, obj):
        """인기도 표시"""
        return obj.get_popularity_level()
    get_popularity_level.short_description = '인기도'

    def get_comment_increase(self, obj):
        """댓글 증가수 표시"""
        increase = obj.get_comment_increase()
        rate = obj.get_comment_increase_rate()
        return f"+{increase} ({rate}%)"
    get_comment_increase.short_description = '댓글 증가'

    def get_comment_stats(self, obj):
        """댓글 통계 표시"""
        increase = obj.get_comment_increase()
        rate = obj.get_comment_increase_rate()
        return f"증가: {increase}개 ({rate}%)"
    get_comment_stats.short_description = '댓글 통계'

    # 리스트 페이지에서 긴급 공구 강조
    def get_queryset(self, request):
        """쿼리셋 최적화"""
        return super().get_queryset(request).select_related()

    # 액션 추가
    actions = ['mark_as_active', 'mark_as_paused', 'mark_as_finished']

    def mark_as_active(self, request, queryset):
        """선택된 공구를 진행중으로 변경"""
        queryset.update(nStepType=1)
        self.message_user(request, f"{queryset.count()}개 공구를 진행중으로 변경했습니다.")
    mark_as_active.short_description = "선택된 공구를 진행중으로 변경"

    def mark_as_paused(self, request, queryset):
        """선택된 공구를 일시정지로 변경"""
        queryset.update(nStepType=2)
        self.message_user(request, f"{queryset.count()}개 공구를 일시정지로 변경했습니다.")
    mark_as_paused.short_description = "선택된 공구를 일시정지로 변경"

    def mark_as_finished(self, request, queryset):
        """선택된 공구를 마감으로 변경"""
        queryset.update(nStepType=3)
        self.message_user(request, f"{queryset.count()}개 공구를 마감으로 변경했습니다.")
    mark_as_finished.short_description = "선택된 공구를 마감으로 변경"


@admin.register(GongguCompany)
class GongguCompanyAdmin(admin.ModelAdmin):
    list_display = ('no', 'get_gonggu_name', 'get_company_name', 'get_gonggu_status_display')
    list_filter = ('noGonggu', 'noCompany')
    search_fields = ('noGonggu', 'noCompany')
    readonly_fields = ('no', 'created_at', 'updated_at')

    fieldsets = (
        ('기본 정보', {
            'fields': ('no', 'noGonggu', 'noCompany')
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

    def get_gonggu_name(self, obj):
        """공구명 표시"""
        return obj.get_gonggu_name()
    get_gonggu_name.short_description = '공구명'

    def get_company_name(self, obj):
        """업체명 표시"""
        return obj.get_company_name()
    get_company_name.short_description = '업체명'

    def get_gonggu_status_display(self, obj):
        """공구 상태 표시"""
        gonggu = obj.get_gonggu()
        if gonggu:
            status_info = gonggu.get_status_display_with_color()
            return status_info['status']
        return '공구 정보 없음'
    get_gonggu_status_display.short_description = '공구 상태'

    def get_summary_display(self, obj):
        """요약 정보 표시"""
        return obj.get_summary()
    get_summary_display.short_description = '요약 정보'

    # 중복 방지를 위한 폼 검증
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj:
            # 수정 시에는 현재 객체 제외하고 중복 검사
            form.base_fields['noGonggu'].help_text = f"현재 설정: 공구 {obj.noGonggu}"
            form.base_fields['noCompany'].help_text = f"현재 설정: 업체 {obj.noCompany}"
        else:
            # 새로 생성 시 안내
            form.base_fields['noGonggu'].help_text = "공구, 업체 조합은 고유해야 합니다."
        return form


@admin.register(GongguArea)
class GongguAreaAdmin(admin.ModelAdmin):
    list_display = ('no', 'get_gonggu_name', 'get_company_name', 'get_area_name',
                   'get_type_display', 'get_gonggu_status_display')
    list_filter = ('nType', 'noGongguCompany')
    search_fields = ('noGongguCompany', 'noArea')
    readonly_fields = ('no', 'created_at', 'updated_at')

    fieldsets = (
        ('기본 정보', {
            'fields': ('no', 'noGongguCompany', 'noArea')
        }),
        ('보관형식', {
            'fields': ('nType',)
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

    def get_gonggu_name(self, obj):
        """공구명 표시"""
        return obj.get_gonggu_name()
    get_gonggu_name.short_description = '공구명'

    def get_company_name(self, obj):
        """업체명 표시"""
        return obj.get_company_name()
    get_company_name.short_description = '업체명'

    def get_area_name(self, obj):
        """지역명 표시"""
        return obj.get_area_name()
    get_area_name.short_description = '지역명'

    def get_type_display(self, obj):
        """보관형식 표시"""
        type_info = obj.get_type_display_with_color()
        return type_info['type']
    get_type_display.short_description = '보관형식'

    def get_gonggu_status_display(self, obj):
        """공구 상태 표시"""
        status_info = obj.get_gonggu_status()
        return status_info['status']
    get_gonggu_status_display.short_description = '공구 상태'

    def get_summary_display(self, obj):
        """요약 정보 표시"""
        return obj.get_summary()
    get_summary_display.short_description = '요약 정보'

    # 액션 추가
    actions = ['mark_as_additional', 'mark_as_excluded', 'mark_as_assigned']

    def mark_as_additional(self, request, queryset):
        """선택된 지역을 추가지역으로 변경"""
        queryset.update(nType=0)
        self.message_user(request, f"{queryset.count()}개 지역을 추가지역으로 변경했습니다.")
    mark_as_additional.short_description = "선택된 지역을 추가지역으로 변경"

    def mark_as_excluded(self, request, queryset):
        """선택된 지역을 제외지역으로 변경"""
        queryset.update(nType=1)
        self.message_user(request, f"{queryset.count()}개 지역을 제외지역으로 변경했습니다.")
    mark_as_excluded.short_description = "선택된 지역을 제외지역으로 변경"

    def mark_as_assigned(self, request, queryset):
        """선택된 지역을 실제할당지역으로 변경"""
        queryset.update(nType=2)
        self.message_user(request, f"{queryset.count()}개 지역을 실제할당지역으로 변경했습니다.")
    mark_as_assigned.short_description = "선택된 지역을 실제할당지역으로 변경"

    # 중복 방지를 위한 폼 검증
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj:
            # 수정 시에는 현재 객체 제외하고 중복 검사
            form.base_fields['noGongguCompany'].help_text = f"현재 설정: 공구업체 {obj.noGongguCompany}"
            form.base_fields['noArea'].help_text = f"현재 설정: 지역 {obj.noArea}"
        else:
            # 새로 생성 시 안내
            form.base_fields['noGongguCompany'].help_text = "공구업체, 지역 조합은 고유해야 합니다."
        return form
