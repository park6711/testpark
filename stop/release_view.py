from django.shortcuts import get_object_or_404
from django.views import View
from django.http import JsonResponse
from datetime import timedelta
from .models import Stop


class StopReleaseView(View):
    """일시정지 해제 (종료일을 어제로 변경)"""

    def post(self, request, stop_id):
        """일시정지 해제 처리"""
        # 로그인 확인
        if not request.session.get('staff_user'):
            return JsonResponse({'success': False, 'error': '로그인이 필요합니다.'})

        try:
            stop = get_object_or_404(Stop, no=stop_id)
            today = self.get_today()
            yesterday = today - timedelta(days=1)

            # 시작일과 종료일을 모두 어제로 변경
            stop.dateStart = yesterday
            stop.dateEnd = yesterday
            stop.save()

            return JsonResponse({'success': True, 'message': '일시정지가 해제되었습니다.'})

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    def get_today(self):
        """오늘 날짜 반환 (한국 시간 기준)"""
        from django.utils import timezone
        return timezone.localtime().date()