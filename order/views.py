from django.shortcuts import render
from django.http import HttpResponse

def order_list(request):
    """주문 목록 페이지 - React 앱"""
    from django.conf import settings
    context = {
        'debug': settings.DEBUG  # 개발/프로덕션 환경 구분
    }
    return render(request, 'order/react_app.html', context)

def pplist_view(request):
    """React 의뢰리스트 페이지"""
    # React 앱 템플릿으로 렌더링
    from django.conf import settings
    context = {
        'debug': settings.DEBUG  # 개발/프로덕션 환경 구분
    }
    return render(request, 'order/react_app.html', context)
