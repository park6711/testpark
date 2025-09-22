#!/usr/bin/env python
import os
import sys
import django

# Django 설정
sys.path.append('/Users/sewookpark/Documents/testpark')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testpark_project.settings')
django.setup()

from company.models import Company

def update_company_sname1():
    """Company DB의 sName1 필드 업데이트"""

    # 모든 Company 객체 가져오기
    companies = Company.objects.all()

    print(f"총 {companies.count()}개의 Company 레코드의 sName1을 업데이트합니다...")

    for company in companies:
        # sName1 = 서울 + Company.no + 호 + 빈칸 + 영등포
        company.sName1 = f"서울{company.no}호 영등포"

        company.save()
        print(f"Company {company.no}: sName1 = {company.sName1}")

    print("Company sName1 필드 업데이트가 완료되었습니다!")

if __name__ == "__main__":
    update_company_sname1()