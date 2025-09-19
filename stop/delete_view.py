from django.shortcuts import get_object_or_404
from django.views import View
from django.http import JsonResponse
from .models import Stop


class StopDeleteView(View):
    """일시정지 삭제"""

    def post(self, request, stop_id):
        """일시정지 삭제 처리"""
        # 로그인 확인
        if not request.session.get('staff_user'):
            return JsonResponse({'success': False, 'error': '로그인이 필요합니다.'})

        try:
            stop = get_object_or_404(Stop, no=stop_id)
            stop_no = stop.no
            company_name = stop.get_company_name()

            # 실제 삭제 수행
            stop.delete()

            return JsonResponse({
                'success': True,
                'message': f'일시정지 #{stop_no} ({company_name})이 삭제되었습니다.'
            })

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})