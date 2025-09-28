from django.contrib import admin
from .models import Template

@admin.register(Template)
class TemplateAdmin(admin.ModelAdmin):
    """템플리트(Template) Admin 설정"""

    # 목록 표시 필드
    list_display = [
        'no',
        'sTitle',
        'get_nReceiver_display',
        'get_nType_display',
        'nUse',
        'created_at',
        'updated_at'
    ]

    # 필터 옵션
    list_filter = [
        'nReceiver',
        'nType',
        'created_at',
        'updated_at'
    ]

    # 검색 필드
    search_fields = [
        'sTitle',
        'sContent'
    ]

    # 정렬
    ordering = ['-no']

    # 상세 페이지 필드 구성
    fieldsets = (
        ('기본 정보', {
            'fields': ('sTitle', 'nReceiver', 'nType')
        }),
        ('내용', {
            'fields': ('sContent',)
        }),
        ('통계', {
            'fields': ('nUse',),
            'classes': ('collapse',)
        }),
    )

    # 읽기 전용 필드
    readonly_fields = ['nUse', 'created_at', 'updated_at']

    # 페이지당 항목 수
    list_per_page = 20

    # 액션 메뉴
    actions = ['reset_use_count']

    def reset_use_count(self, request, queryset):
        """사용횟수 초기화"""
        updated = queryset.update(nUse=0)
        self.message_user(request, f'{updated}개 템플리트의 사용횟수가 초기화되었습니다.')
    reset_use_count.short_description = '선택한 템플리트 사용횟수 초기화'