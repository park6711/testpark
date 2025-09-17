from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, AuthSession


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """CustomUser 관리자 페이지"""

    # 목록 페이지에서 보여줄 필드들
    list_display = [
        'email', 'name', 'username', 'is_naver_linked',
        'department', 'position', 'is_active', 'date_joined'
    ]

    # 필터링 옵션
    list_filter = [
        'is_naver_linked', 'is_active', 'is_staff',
        'department', 'position', 'date_joined'
    ]

    # 검색 가능한 필드들
    search_fields = ['email', 'name', 'username', 'naver_email']

    # 정렬 기준
    ordering = ['-date_joined']

    # 상세 페이지 필드 그룹화
    fieldsets = UserAdmin.fieldsets + (
        ('개인 정보', {
            'fields': ('name', 'phone', 'department', 'position')
        }),
        ('네이버 연동 정보', {
            'fields': ('naver_id', 'naver_email', 'naver_name', 'is_naver_linked')
        }),
        ('인증번호 정보', {
            'fields': ('auth_code', 'auth_code_expires'),
            'classes': ('collapse',)  # 기본적으로 접힌 상태
        }),
        ('타임스탬프', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    # 읽기 전용 필드들
    readonly_fields = ['created_at', 'updated_at', 'last_login', 'date_joined']


@admin.register(AuthSession)
class AuthSessionAdmin(admin.ModelAdmin):
    """AuthSession 관리자 페이지"""

    # 목록 페이지에서 보여줄 필드들
    list_display = [
        'session_key', 'user', 'auth_code',
        'is_verified', 'expires_at', 'created_at'
    ]

    # 필터링 옵션
    list_filter = ['is_verified', 'created_at', 'expires_at']

    # 검색 가능한 필드들
    search_fields = ['session_key', 'user__email', 'user__name']

    # 정렬 기준
    ordering = ['-created_at']

    # 상세 페이지 필드들
    fields = [
        'session_key', 'user', 'naver_data',
        'auth_code', 'expires_at', 'is_verified', 'created_at'
    ]

    # 읽기 전용 필드들
    readonly_fields = ['created_at']

    # 네이버 데이터 JSON 필드를 보기 좋게 표시
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if 'naver_data' in form.base_fields:
            form.base_fields['naver_data'].widget.attrs['rows'] = 10
        return form
