from django.shortcuts import render
from django.http import HttpResponse

def contract_list(request):
    """계약 목록 페이지"""
    return HttpResponse("Contract List - 계약 관리 페이지입니다.")
