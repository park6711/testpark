from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.http import HttpResponse
import csv
from .models import EvaluationNo, Complain, Satisfy, Evaluation, YearEvaluation


@admin.register(EvaluationNo)
class EvaluationNoAdmin(admin.ModelAdmin):
    list_display = [
        'no',
        'get_period_display',
        'get_point_period_display',
        'get_status_badge',
        'get_progress_bar',
        'get_formatted_average_all',
        'get_formatted_average_excel',
        'get_improvement_display',
        'get_notification_times',
        'created_at'
    ]

    list_filter = [
        'dateStart',
        'dateEnd',
        'datePointStart',
        'datePointEnd',
        'created_at'
    ]

    search_fields = [
        'no',
    ]

    readonly_fields = [
        'no',
        'created_at',
        'updated_at',
        'get_evaluation_period_days',
        'get_point_period_days',
        'get_period_status',
        'get_progress_percentage',
        'get_average_improvement',
        'get_days_until_start',
        'get_days_until_end',
        'get_summary_display'
    ]

    fieldsets = (
        ('기본 정보', {
            'fields': ('no', 'created_at', 'updated_at')
        }),
        ('평가 기간', {
            'fields': ('dateStart', 'dateEnd', 'get_evaluation_period_days', 'get_days_until_start', 'get_days_until_end')
        }),
        ('포인트 적용 기간', {
            'fields': ('datePointStart', 'datePointEnd', 'get_point_period_days')
        }),
        ('계약률 정보', {
            'fields': ('fAverageAll', 'fAverageExcel', 'get_average_improvement')
        }),
        ('예약문자 시간', {
            'fields': ('timeExcel', 'timeWeek')
        }),
        ('상태 정보', {
            'fields': ('get_period_status', 'get_progress_percentage', 'get_summary_display'),
            'classes': ('collapse',)
        })
    )

    ordering = ['-no']
    list_per_page = 25

    actions = ['export_to_csv', 'start_evaluation', 'complete_evaluation']

    def get_period_display(self, obj):
        """평가 기간 표시"""
        return f"{obj.dateStart} ~ {obj.dateEnd}"
    get_period_display.short_description = '평가기간'

    def get_point_period_display(self, obj):
        """포인트 적용 기간 표시"""
        return f"{obj.datePointStart} ~ {obj.datePointEnd}"
    get_point_period_display.short_description = '포인트기간'

    def get_status_badge(self, obj):
        """상태 뱃지 표시"""
        status = obj.get_period_status()
        color_map = {
            '대기': 'blue',
            '평가중': 'green',
            '평가완료': 'orange',
            '포인트적용중': 'purple',
            '완료': 'gray'
        }
        color = color_map.get(status, 'black')

        return format_html(
            '<span style="color: {}; font-weight: bold; padding: 3px 8px; border: 1px solid {}; border-radius: 4px;">{}</span>',
            color,
            color,
            status
        )
    get_status_badge.short_description = '상태'

    def get_progress_bar(self, obj):
        """진행률 프로그레스 바"""
        progress = obj.get_progress_percentage()
        if progress >= 100:
            color = '#28a745'  # 완료 - 녹색
        elif progress >= 75:
            color = '#ffc107'  # 거의 완료 - 노란색
        elif progress >= 50:
            color = '#17a2b8'  # 진행중 - 파란색
        else:
            color = '#6c757d'  # 시작 - 회색

        return format_html(
            '<div style="width: 100px; background-color: #e9ecef; border-radius: 4px; overflow: hidden;">'
            '<div style="width: {}%; height: 20px; background-color: {}; text-align: center; line-height: 20px; color: white; font-size: 11px;">'
            '{}%</div></div>',
            progress,
            color,
            progress
        )
    get_progress_bar.short_description = '진행률'

    def get_improvement_display(self, obj):
        """개선율 표시"""
        improvement = obj.get_average_improvement()
        if improvement > 0:
            color = 'green'
            symbol = '↑'
        elif improvement < 0:
            color = 'red'
            symbol = '↓'
        else:
            color = 'gray'
            symbol = '→'

        return format_html(
            '<span style="color: {}; font-weight: bold;">{} {:.2f}%</span>',
            color,
            symbol,
            abs(improvement)
        )
    get_improvement_display.short_description = '개선율'

    def get_notification_times(self, obj):
        """예약문자 시간 표시"""
        times = obj.get_notification_times_display()
        return format_html(
            '우수: {}<br>미진: {}',
            times['excel'],
            times['week']
        )
    get_notification_times.short_description = '알림시간'

    def get_summary_display(self, obj):
        """요약 정보 표시"""
        summary = obj.get_summary_info()
        return format_html(
            '평가회차: {}<br>'
            '평가기간: {}<br>'
            '포인트기간: {}<br>'
            '상태: {}<br>'
            '진행률: {}<br>'
            '전체평균: {}<br>'
            '우수평균: {}<br>'
            '개선율: {}',
            summary['evaluation_no'],
            summary['period'],
            summary['point_period'],
            summary['status'],
            summary['progress'],
            summary['average_all'],
            summary['average_excel'],
            summary['improvement']
        )
    get_summary_display.short_description = '요약정보'

    def export_to_csv(self, request, queryset):
        """CSV 내보내기"""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="evaluation_rounds.csv"'
        response.write('\ufeff')  # UTF-8 BOM

        writer = csv.writer(response)
        writer.writerow([
            '평가회차ID', '평가시작일', '평가종료일', '포인트시작일', '포인트종료일',
            '전체평균계약률', '우수업체평균계약률', '개선율', '우수업체알림시간', '미진업체알림시간',
            '상태', '진행률', '생성일시'
        ])

        for obj in queryset:
            times = obj.get_notification_times_display()
            writer.writerow([
                obj.no, obj.dateStart, obj.dateEnd, obj.datePointStart, obj.datePointEnd,
                f"{obj.fAverageAll:.2f}%", f"{obj.fAverageExcel:.2f}%", f"{obj.get_average_improvement():.2f}%",
                times['excel'], times['week'], obj.get_period_status(), f"{obj.get_progress_percentage()}%",
                obj.created_at
            ])

        return response
    export_to_csv.short_description = "선택된 평가회차를 CSV로 내보내기"

    def start_evaluation(self, request, queryset):
        """평가 시작"""
        from django.utils import timezone
        today = timezone.localtime().date()

        updated = 0
        for obj in queryset:
            if today >= obj.dateStart and obj.get_period_status() == '대기':
                # 평가가 시작되었음을 알리는 로직 추가 가능
                updated += 1

        self.message_user(request, f"{updated}개 평가회차가 시작 상태로 확인되었습니다.")
    start_evaluation.short_description = "선택된 평가회차 시작 확인"

    def complete_evaluation(self, request, queryset):
        """평가 완료 처리"""
        updated = 0
        for obj in queryset:
            if obj.get_period_status() in ['평가중', '평가완료']:
                # 평가 완료 처리 로직 추가 가능
                updated += 1

        self.message_user(request, f"{updated}개 평가회차가 완료 처리되었습니다.")
    complete_evaluation.short_description = "선택된 평가회차 완료 처리"

    def get_queryset(self, request):
        """쿼리셋 최적화"""
        return super().get_queryset(request)



@admin.register(Complain)
class ComplainAdmin(admin.ModelAdmin):
    list_display = [
        'no',
        'noEvaluation',
        'get_company_name',
        'sTime',
        'get_severity_badge',
        'fComplain',
        'sCheck',
        'sWorker',
        'created_at'
    ]

    list_filter = [
        'noEvaluation',
        'noCompany',
        'sCheck',
        'sWorker',
        'created_at'
    ]

    search_fields = [
        'no',
        'sComName',
        'sComplain',
        'sPost',
        'sWorker'
    ]

    fieldsets = (
        ('기본 정보', {
            'fields': ('no', 'noEvaluation', 'noCompany', 'get_company_name')
        }),
        ('불만 정보', {
            'fields': ('sTime', 'sComName', 'sPass', 'sComplain', 'sComplainPost', 'sPost')
        }),
        ('평가 및 처리', {
            'fields': ('fComplain', 'sCheck', 'sWorker', 'sFile')
        })
    )

    readonly_fields = ['no', 'get_company_name']

    def get_severity_badge(self, obj):
        """심각도 뱃지"""
        level = obj.get_severity_level()
        color = obj.get_severity_color()
        return format_html(
            '<span style="color: {}; font-weight: bold;">{} ({:.1f}점)</span>',
            color, level, obj.fComplain
        )
    get_severity_badge.short_description = '심각도'


@admin.register(Satisfy)
class SatisfyAdmin(admin.ModelAdmin):
    list_display = [
        'no',
        'noEvaluation',
        'get_company_name',
        'sTime',
        'get_satisfaction_badge',
        'fSatisfy',
        'created_at'
    ]

    list_filter = [
        'noEvaluation',
        'noCompany',
        'created_at'
    ]

    search_fields = [
        'no',
        'sCompanyName',
        'sAddress',
        'sMemo'
    ]

    fieldsets = (
        ('기본 정보', {
            'fields': ('no', 'noEvaluation', 'noCompany')
        }),
        ('만족도 정보', {
            'fields': ('sCompanyName', 'sTime', 'sAddress', 'fSatisfy')
        }),
        ('추가 정보', {
            'fields': ('sMemo',)
        })
    )

    readonly_fields = ['no']

    def get_company_name(self, obj):
        """업체명 반환"""
        try:
            from company.models import Company
            company = Company.objects.get(no=obj.noCompany)
            return company.sCompanyName or obj.sCompanyName
        except:
            return obj.sCompanyName or f"업체{obj.noCompany}"
    get_company_name.short_description = '업체명'

    def get_satisfaction_badge(self, obj):
        """만족도 뱃지"""
        level = obj.get_satisfaction_level()
        color = obj.get_satisfaction_color()
        return format_html(
            '<span style="color: {}; font-weight: bold;">{} ({:.1f}점)</span>',
            color, level, obj.fSatisfy
        )
    get_satisfaction_badge.short_description = '만족도'


@admin.register(Evaluation)
class EvaluationAdmin(admin.ModelAdmin):
    list_display = [
        'no',
        'noEvaluationNo',
        'get_company_name',
        'fTotalScore',
        'get_grade_display',
        'fPercent',
        'get_rank_display',
        'bWeak',
        'bExcept',
        'created_at'
    ]

    list_filter = [
        'noEvaluationNo',
        'nLevel',
        'nGrade',
        'bWeak',
        'bExcept',
        'bMento',
        'created_at'
    ]

    search_fields = [
        'no',
        'noCompany'
    ]

    fieldsets = (
        ('기본 정보', {
            'fields': ('no', 'noEvaluationNo', 'noCompany', 'get_company_name')
        }),
        ('평가 결과', {
            'fields': ('fTotalScore', 'nLevel', 'nGrade', 'fPercent', 'bWeak', 'bExcept')
        }),
        ('업무 실적', {
            'fields': ('nReturn', 'nCancel', 'nExcept', 'nPart', 'nAll', 'nSum', 'nContract')
        }),
        ('금액 정보', {
            'fields': ('nFee', 'nFixFee', 'nDotCom', 'nBtoB')
        }),
        ('고객 관련', {
            'fields': ('fReview', 'fComplain', 'nSatisfy', 'fSatisfy')
        }),
        ('활동 실적', {
            'fields': ('nAnswer1', 'nAnswer2', 'nSeminar', 'bMento')
        }),
        ('보증 관련', {
            'fields': ('nWarranty1', 'nWarranty2', 'nWarranty3', 'nSafe', 'fSpecial')
        }),
        ('포인트 관련', {
            'fields': ('nPayBackPoint', 'nPrePoint', 'nSumPoint', 'nUsePoint', 'nRemainPoint')
        }),
        ('세부 점수', {
            'fields': (
                'fPercentScore', 'fFeeScore', 'fFixFeeScore', 'fBtoBScore',
                'fReviewScore', 'fComplainScore', 'fSafistyScore',
                'fAnswer1Score', 'fAnswer2Socre', 'fSeminarScore',
                'fMentoScore', 'fWarrantyScore', 'fSafeScore', 'fSpecialScore'
            ),
            'classes': ('collapse',)
        })
    )

    readonly_fields = ['no', 'get_company_name']
    ordering = ['-fTotalScore']

    def get_rank_display(self, obj):
        """순위 표시"""
        rank = obj.get_rank_info()
        if rank <= 10:
            color = 'green'
        elif rank <= 30:
            color = 'blue'
        else:
            color = 'gray'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}위</span>',
            color, rank
        )
    get_rank_display.short_description = '순위'


@admin.register(YearEvaluation)
class YearEvaluationAdmin(admin.ModelAdmin):
    list_display = [
        'no',
        'nYear',
        'get_company_name',
        'fScore',
        'get_rank_display',
        'get_award_display',
        'get_percentile_display',
        'created_at'
    ]

    list_filter = [
        'nYear',
        'sAward',
        'created_at'
    ]

    search_fields = [
        'no',
        'noCompany',
        'nYear'
    ]

    fieldsets = (
        ('기본 정보', {
            'fields': ('no', 'nYear', 'noCompany', 'get_company_name')
        }),
        ('평가 결과', {
            'fields': ('fScore', 'nRank', 'sAward', 'get_percentile_display')
        })
    )

    readonly_fields = ['no', 'get_company_name', 'get_percentile_display']
    ordering = ['nYear', 'nRank']

    def get_rank_display(self, obj):
        """순위 표시"""
        if obj.nRank <= 3:
            color = 'gold'
        elif obj.nRank <= 10:
            color = 'green'
        else:
            color = 'gray'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}위</span>',
            color, obj.nRank
        )
    get_rank_display.short_description = '순위'

    def get_award_display(self, obj):
        """상패 표시"""
        return obj.get_award_display_with_icon()
    get_award_display.short_description = '상패'

    def get_percentile_display(self, obj):
        """백분위 표시"""
        percentile = obj.get_percentile_rank()
        return f"상위 {percentile}%"
    get_percentile_display.short_description = '백분위'