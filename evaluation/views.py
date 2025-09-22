from django.shortcuts import render
from django.http import HttpResponse

def evaluation_list(request):
    """평가 목록 페이지"""
    return HttpResponse("Evaluation List - 평가 관리 페이지입니다.")
