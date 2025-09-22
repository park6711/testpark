from django.shortcuts import render
from django.http import HttpResponse

def template_list(request):
    """템플릿 목록 페이지"""
    return HttpResponse("Template List - 템플릿 관리 페이지입니다.")
