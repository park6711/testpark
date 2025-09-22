from django.shortcuts import render
from django.http import HttpResponse

def order_list(request):
    """주문 목록 페이지"""
    return HttpResponse("Order List - 주문 관리 페이지입니다.")

def pplist_view(request):
    """React 의뢰리스트 페이지"""
    # 템플릿 디버깅
    try:
        return render(request, 'order/pplist_inline.html', {})
    except Exception as e:
        from django.http import HttpResponse
        return HttpResponse(f"Error: {str(e)}", status=500)
