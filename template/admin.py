from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.http import HttpResponse
import csv
from .models import Template


@admin.register(Template)
class TemplateAdmin(admin.ModelAdmin):
    list_display = [
        'no',
        'get_type_display_with_icon',
        'get_type_display_badge',
        'get_receiver_display_with_icon',
        'sTitle',
        'get_content_preview_display',
        'get_usage_badge',
        'nUse',
        'created_at'
    ]

    list_filter = [
        'nType',
        'nReceiver',
        'created_at'
    ]

    search_fields = [
        'no',
        'sTitle',
        'sContent'
    ]

    readonly_fields = [
        'no',
        'nUse',
        'created_at',
        'updated_at',
        'get_usage_level',
        'is_frequently_used',
        'get_template_summary_display',
        'get_similar_templates_display'
    ]

    fieldsets = (
        ('기본 정보', {
            'fields': ('no', 'created_at', 'updated_at')
        }),
        ('분류 정보', {
            'fields': ('nType', 'nReceiver')
        }),
        ('템플릿 내용', {
            'fields': ('sTitle', 'sContent')
        }),
        ('사용 통계', {
            'fields': ('nUse', 'get_usage_level', 'is_frequently_used')
        }),
        ('관련 정보', {
            'fields': ('get_template_summary_display', 'get_similar_templates_display'),
            'classes': ('collapse',)
        })
    )

    ordering = ['-nUse', '-created_at']
    list_per_page = 25

    actions = ['export_to_csv', 'reset_usage_count', 'duplicate_template']

    def get_type_display_with_icon(self, obj):
        """분류 아이콘 표시"""
        return obj.get_type_display_with_icon()
    get_type_display_with_icon.short_description = '분류'

    def get_type_display_badge(self, obj):
        """분류 뱃지 표시"""
        type_info = obj.get_type_display_with_color()
        return format_html(
            '<span style="color: {}; font-weight: bold; padding: 2px 6px; border: 1px solid {}; border-radius: 3px;">{}</span>',
            type_info['color'],
            type_info['color'],
            type_info['type']
        )
    get_type_display_badge.short_description = '분류 색상'

    def get_receiver_display_with_icon(self, obj):
        """수신 대상 아이콘 표시"""
        return obj.get_receiver_display_with_icon()
    get_receiver_display_with_icon.short_description = '수신대상'

    def get_content_preview_display(self, obj):
        """내용 미리보기"""
        preview = obj.get_content_preview(30)
        return format_html('<span title="{}">{}</span>', obj.sContent, preview)
    get_content_preview_display.short_description = '내용미리보기'

    def get_usage_badge(self, obj):
        """사용 빈도 뱃지"""
        level = obj.get_usage_level()
        color = obj.get_usage_color()
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            level
        )
    get_usage_badge.short_description = '사용빈도'

    def get_template_summary_display(self, obj):
        """템플릿 요약 정보"""
        summary = obj.get_template_summary()
        return format_html(
            'ID: {}<br>'
            '분류: {}<br>'
            '분류색상: {}<br>'
            '수신대상: {}<br>'
            '제목: {}<br>'
            '내용: {}<br>'
            '사용횟수: {}<br>'
            '사용수준: {}<br>'
            '인기여부: {}<br>'
            '생성일: {}',
            summary['template_id'],
            summary['type'],
            summary['type_color']['type'],
            summary['receiver'],
            summary['title'] or '제목없음',
            summary['content_preview'],
            summary['usage_count'],
            summary['usage_level'],
            '예' if summary['is_popular'] else '아니오',
            summary['created_date']
        )
    get_template_summary_display.short_description = '템플릿요약'

    def get_similar_templates_display(self, obj):
        """유사한 템플릿 표시"""
        similar = obj.get_similar_templates()
        if not similar:
            return "유사한 템플릿이 없습니다."

        html = []
        for template in similar:
            html.append(f"템플릿 {template.no}: {template.sTitle or '제목없음'} (사용 {template.nUse}회)")
        return mark_safe('<br>'.join(html))
    get_similar_templates_display.short_description = '유사템플릿'

    def export_to_csv(self, request, queryset):
        """CSV 내보내기"""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="templates.csv"'
        response.write('\ufeff')  # UTF-8 BOM

        writer = csv.writer(response)
        writer.writerow([
            '템플릿ID', '분류', '수신대상', '제목', '내용', '사용횟수',
            '사용수준', '생성일시'
        ])

        for obj in queryset:
            writer.writerow([
                obj.no, obj.get_nType_display(),
                obj.get_nReceiver_display(), obj.sTitle, obj.sContent,
                obj.nUse, obj.get_usage_level(), obj.created_at
            ])

        return response
    export_to_csv.short_description = "선택된 템플릿을 CSV로 내보내기"

    def reset_usage_count(self, request, queryset):
        """사용횟수 초기화"""
        updated = queryset.update(nUse=0)
        self.message_user(request, f"{updated}개 템플릿의 사용횟수가 초기화되었습니다.")
    reset_usage_count.short_description = "선택된 템플릿의 사용횟수 초기화"

    def duplicate_template(self, request, queryset):
        """템플릿 복제"""
        duplicated = 0
        for obj in queryset:
            obj.pk = None  # 새로운 객체로 만들기
            obj.sTitle = f"{obj.sTitle} (복사본)" if obj.sTitle else "복사본"
            obj.nUse = 0  # 사용횟수 초기화
            obj.save()
            duplicated += 1

        self.message_user(request, f"{duplicated}개 템플릿이 복제되었습니다.")
    duplicate_template.short_description = "선택된 템플릿 복제"

    def get_queryset(self, request):
        """쿼리셋 최적화"""
        return super().get_queryset(request)

    class Media:
        css = {
            'all': ('admin/css/template_admin.css',)
        }
        js = ('admin/js/template_admin.js',)