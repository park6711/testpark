#!/usr/bin/env python
"""
Company choices 디버깅 스크립트
"""

import os
import sys
import django

# Django 설정
sys.path.append('/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testpark_project.settings')
django.setup()

from company.models import Company
from stop.forms import StopForm

def debug_company_choices():
    print("=== Company 데이터 확인 ===")
    companies = Company.objects.all().order_by('no')
    print(f"총 Company 개수: {companies.count()}")

    print("\n=== Company 데이터 세부 정보 ===")
    for company in companies[:10]:  # 처음 10개만 확인
        sname2 = getattr(company, 'sName2', None)
        sname1 = getattr(company, 'sName1', None)
        print(f"  {company.no}. sName1='{sname1}', sName2='{sname2}'")

    print("\n=== StopForm의 get_company_choices() 결과 ===")
    form = StopForm()
    choices = form.get_company_choices()

    print(f"총 choices 개수: {len(choices)}")
    for choice in choices[:15]:  # 처음 15개만 표시
        print(f"  {choice}")

if __name__ == '__main__':
    debug_company_choices()