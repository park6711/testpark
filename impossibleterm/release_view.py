from django.shortcuts import get_object_or_404
from django.views import View
from django.http import JsonResponse
from datetime import timedelta
from .models import ImpossibleTerm


class ImpoReleaseView(View):
    """공사 불가능 기간 해제 (종료일을 어제로 변경)"""

    def post(self, request, impo_id):
        """공사 불가능 기간 해제 처리"""
        # 로그인 확인
        if not request.session.get('staff_user'):
            return JsonResponse({'success': False, 'error': '로그인이 필요합니다.'})

        try:
            impo = get_object_or_404(ImpossibleTerm, no=impo_id)
            today = self.get_today()
            yesterday = today - timedelta(days=1)

            # 시작일과 종료일을 모두 어제로 변경
            impo.dateStart = yesterday
            impo.dateEnd = yesterday
            impo.save()

            return JsonResponse({'success': True, 'message': '공사 불가능 기간이 해제되었습니다.'})

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    def get_today(self):
        """오늘 날짜 반환 (한국 시간 기준)"""
        from django.utils import timezone
        return timezone.localtime().date()