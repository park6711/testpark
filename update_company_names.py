#!/usr/bin/env python
import os
import sys
import django
from faker import Faker

# Django 설정
sys.path.append('/Users/sewookpark/Documents/testpark')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testpark_project.settings')
django.setup()

from company.models import Company

def update_company_names():
    """Company DB의 이름 필드들 업데이트"""
    fake = Faker('ko_KR')

    # 모든 Company 객체 가져오기
    companies = Company.objects.all()

    print(f"총 {companies.count()}개의 Company 레코드를 업데이트합니다...")

    for company in companies:
        # sName1 = 서울 + Company.no + 호 + 영등포
        company.sName1 = f"서울{company.no}호영등포"

        # sName2 = 서울 + Company.no + 호
        company.sName2 = f"서울{company.no}호"

        # sName3 = 서울 + Company.no
        company.sName3 = f"서울{company.no}"

        # sCompany = 임의의 회사명
        company_types = [
            "건설", "인테리어", "리모델링", "시공", "전기", "설비", "도장", "타일", "바닥", "방수",
            "철거", "목공", "유리", "샷시", "석공", "조경", "청소", "이사", "운송", "배관"
        ]
        company_names = [
            "대한", "한국", "서울", "경기", "인천", "부산", "대구", "광주", "대전", "울산",
            "세종", "강원", "충북", "충남", "전북", "전남", "경북", "경남", "제주", "성원",
            "태평", "동양", "서원", "진흥", "발전", "협성", "대성", "한성", "동부", "서부"
        ]

        company_type = fake.random_element(company_types)
        company_name = fake.random_element(company_names)
        company.sCompany = f"{company_name}{company_type}"

        company.save()
        print(f"Company {company.no}: {company.sName1}, {company.sName2}, {company.sName3}, {company.sCompany}")

    print("Company 이름 필드 업데이트가 완료되었습니다!")

if __name__ == "__main__":
    update_company_names()