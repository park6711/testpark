from django.shortcuts import render
from django.http import HttpResponse

def order_list(request):
    """주문 목록 페이지"""
    return HttpResponse("Order List - 주문 관리 페이지입니다.")
