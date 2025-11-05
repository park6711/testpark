#!/usr/bin/env python3
"""
CompanyReport 테스트 데이터 생성 스크립트
30개의 테스트 CompanyReport 데이터를 생성합니다.
"""

import os
import sys
import django
import random
from datetime import datetime, timedelta

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testpark_project.settings')
os.environ['USE_MYSQL'] = 'True'
os.environ['DB_HOST'] = 'carpenterhosting.cafe24.com'
os.environ['DB_NAME'] = 'testpark'
os.environ['DB_USER'] = 'testpark'
os.environ['DB_PASSWORD'] = '**jeje4211'

django.setup()

from contract.models import CompanyReport
from company.models import Company

def create_test_company_reports():
    """테스트용 CompanyReport 데이터 생성"""

    # 모든 Company 가져오기
    companies = list(Company.objects.all())

    if not companies:
        print("Company 데이터가 없습니다. 먼저 Company 데이터를 생성해주세요.")
        return

    # 보고구분 종류
    report_types = [0, 1, 2, 3, 4, 5, 6, 7, 8]

    # 공사유형 종류
    construction_types = [0, 1, 2, 3]

    # 환불방식 종류
    refund_types = [0, 1]

    # 지역 목록
    areas = [
        '서울 강남구 테헤란로',
        '서울 서초구 강남대로',
        '경기 성남시 분당구',
        '경기 수원시 영통구',
        '부산 해운대구 센텀시티',
        '대구 중구 동성로',
        '인천 연수구 송도동',
        '광주 서구 치평동',
        '대전 유성구 노은동',
        '울산 남구 삼산동'
    ]

    # 고객 이름 목록
    customer_names = ['김철수', '이영희', '박민수', '최지현', '정대한', '강미나', '조성우', '윤서연', '임태준', '한소율']

    # 30개 데이터 생성
    created_count = 0
    for i in range(30):
        # 랜덤으로 Company 선택
        company = random.choice(companies)

        # 현재 시간 기준으로 랜덤 날짜 생성
        now = datetime.now()
        timestamp = now - timedelta(days=random.randint(0, 90))

        # 계약일과 완료예정일
        contract_date = now.date() - timedelta(days=random.randint(0, 60))
        schedule_date = contract_date + timedelta(days=random.randint(7, 90))

        # 공사금액 (백만원 ~ 1억원)
        con_money = random.randint(10, 1000) * 100000

        # 수수료 (공사금액의 5~15%)
        fee = int(con_money * random.uniform(0.05, 0.15))

        # CompanyReport 생성
        report = CompanyReport.objects.create(
            # 타임스탬프
            sTimeStamp=timestamp.strftime('%Y. %m. %d 오후 %I:%M:%S'),
            timeStamp=timestamp,

            # 업체 정보
            noCompany=company.no,
            sCompanyName=company.sName2 if company.sName2 else f'업체{company.no}',

            # 고객 정보
            sName=random.choice(customer_names),
            sPhone=f'010-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}',

            # 보고 정보
            nType=random.choice(report_types),

            # 공사 정보
            noConType=random.choice(construction_types),
            sPost=f'https://cafe.naver.com/interiorworker/{random.randint(100000, 999999)}',
            sArea=random.choice(areas) + f' {random.randint(1, 500)}호',

            # 계약 정보
            sDateContract=contract_date.strftime('%Y. %m. %d'),
            dateContract=contract_date,
            sDateSchedule=schedule_date.strftime('%Y. %m. %d'),
            dateSchedule=schedule_date,
            sConMoney=f'{con_money:,}',
            nConMoney=con_money,
            bVat=random.choice([True, False]),

            # 수수료 및 정산 정보
            nFee=fee,
            nAppPoint=random.randint(0, 100000),
            nDemand=fee - random.randint(0, 50000),

            # 입금/환불 정보
            dateDeposit=contract_date + timedelta(days=random.randint(1, 7)),
            nDeposit=fee - random.randint(-10000, 10000),
            nExcess=random.randint(-50000, 50000),
            nRefund=random.choice(refund_types),

            # 세금계산서 및 계좌 정보
            sTaxCompany=f'{company.sName2} 사업자' if company.sName2 else f'사업자{company.no}',
            sAccount=f'국민은행 {random.randint(100000, 999999)}-{random.randint(10, 99)}-{random.randint(100000, 999999)}',

            # 파일 및 메모
            sFile=f'https://drive.google.com/file/d/{random.randint(1000000, 9999999)}',
            sCompanyMemo=f'테스트 보고 {i+1}번 - 업체 메모입니다.',
            sStaffMemo=f'테스트 데이터 {i+1}번',
            sWorker='테스트관리자'
        )

        created_count += 1
        print(f'CompanyReport 생성: {report.no} - {report.sName} ({report.sCompanyName})')

    print(f'\n총 {created_count}개의 CompanyReport 데이터가 생성되었습니다.')

if __name__ == '__main__':
    print('CompanyReport 테스트 데이터 생성을 시작합니다...')
    create_test_company_reports()
    print('완료!')