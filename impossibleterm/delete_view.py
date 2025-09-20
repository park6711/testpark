from django.shortcuts import get_object_or_404
from django.views import View
from django.http import JsonResponse
from .models import ImpossibleTerm


class ImpoDeleteView(View):
    """공사 불가능 기간 삭제"""

    def post(self, request, impo_id):
        """공사 불가능 기간 삭제 처리"""
        # 로그인 확인
        if not request.session.get('staff_user'):
            return JsonResponse({'success': False, 'error': '로그인이 필요합니다.'})

        try:
            impo = get_object_or_404(ImpossibleTerm, no=impo_id)
            impo_no = impo.no
            company_name = impo.get_company_name()

            # 실제 삭제 수행
            impo.delete()

            return JsonResponse({
                'success': True,
                'message': f'공사 불가능 기간 #{impo_no} ({company_name})이 삭제되었습니다.'
            })

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})