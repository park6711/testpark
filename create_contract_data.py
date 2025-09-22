#!/usr/bin/env python
import os
import sys
import django
from datetime import datetime, timedelta
import random
from faker import Faker

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testpark_project.settings')
django.setup()

from contract.models import CompanyReport, ClientReport
from company.models import Company

fake = Faker('ko_KR')

def create_company_reports():
    """CompanyReport 테스트 데이터 30개 생성"""
    print("CompanyReport 테스트 데이터 생성 중...")

    # 기존 업체 ID 가져오기
    company_ids = list(Company.objects.values_list('no', flat=True))
    if not company_ids:
        company_ids = list(range(1, 21))  # 기본값으로 1-20 사용

    reports = []
    for i in range(30):
        # 랜덤 시간 생성 (최근 6개월)
        random_time = fake.date_time_between(start_date='-6M', end_date='now')

        # 계약일과 완료예정일 설정
        contract_date = fake.date_between(start_date='-3M', end_date='today')
        schedule_date = fake.date_between(start_date=contract_date, end_date=contract_date + timedelta(days=90))

        # 금액 계산
        contract_money = random.randint(500, 5000) * 10000  # 500만~5000만원
        fee_rate = random.uniform(0.08, 0.20)  # 8~20% 수수료
        fee = int(contract_money * fee_rate)
        app_point = random.randint(0, 50) * 1000  # 0~5만 포인트
        demand = fee - app_point
        deposit = demand + random.randint(-50000, 100000)  # 과/미입금 고려
        excess = deposit - demand

        report = CompanyReport(
            time=random_time,
            noCompany=random.choice(company_ids),
            nType=random.choice([0, 1, 2, 3, 4, 5, 6, 7, 8]),
            noPre=random.choice([None, random.randint(1, 10)]) if random.random() > 0.8 else None,
            noNext=random.choice([None, random.randint(1, 10)]) if random.random() > 0.8 else None,
            noConType=random.choice([0, 1, 2, 3]),
            sPost=fake.numerify('###-####'),
            noAssign=random.randint(1, 50) if random.random() > 0.3 else None,
            sName=fake.name(),
            sPhone=fake.phone_number(),
            sArea=fake.address(),
            dateContract=contract_date,
            dateSchedule=schedule_date,
            nConMoney=contract_money,
            bVat=random.choice([True, False]),
            nFee=fee,
            nAppPoint=app_point,
            nDemand=demand,
            dateDeposit=fake.date_between(start_date=contract_date, end_date='today') if random.random() > 0.2 else None,
            nDeposit=deposit,
            nExcess=excess,
            nRefund=random.choice([0, 1]),
            sCompanyName=fake.company(),
            sAccount=f"{fake.random_element(['국민', '신한', '우리', 'KB'])}{fake.numerify('###-######-##-###')}",
            sCompanyMemo=fake.text(max_nb_chars=200) if random.random() > 0.3 else '',
            sStaffMemo=fake.text(max_nb_chars=150) if random.random() > 0.4 else '',
            sWorker=fake.name()
        )
        reports.append(report)

    CompanyReport.objects.bulk_create(reports)
    print(f"CompanyReport {len(reports)}개 생성 완료!")

def create_client_reports():
    """ClientReport 테스트 데이터 30개 생성"""
    print("ClientReport 테스트 데이터 생성 중...")

    # 기존 업체 ID 가져오기
    company_ids = list(Company.objects.values_list('no', flat=True))
    if not company_ids:
        company_ids = list(range(1, 21))  # 기본값으로 1-20 사용

    # 소명/징계 내용 샘플
    explanation_samples = [
        "공사 일정 지연에 대한 소명서를 제출합니다. 기상악화로 인한 불가피한 지연이었습니다.",
        "자재 품질 문제에 대해 해명드립니다. 공급업체 변경으로 해결하겠습니다.",
        "고객 요청사항 미반영에 대한 소명입니다. 추가 협의를 통해 해결하겠습니다.",
        "공사비 추가 청구 관련 소명서입니다. 설계 변경으로 인한 불가피한 비용입니다.",
        "A/S 지연에 대한 해명입니다. 인력 부족으로 인한 지연이었으나 즉시 해결하겠습니다."
    ]

    punishment_samples = [
        "경고 - 공사 일정 준수 미흡",
        "벌점 1점 - 고객 응대 불량",
        "계약 해지 경고 - 품질 기준 미달",
        "교육 이수 명령 - 안전 규정 위반",
        "해결됨 - 관리자 처리",
        "벌금 10만원 - 약정 위반"
    ]

    reports = []
    for i in range(30):
        # 랜덤 시간 생성 (최근 3개월)
        random_time = fake.date_time_between(start_date='-3M', end_date='now')

        # 소명/징계 여부 결정
        has_explanation = random.random() > 0.3
        has_punishment = random.random() > 0.5

        company_id = random.choice(company_ids)
        company_name = fake.company()

        report = ClientReport(
            time=random_time,
            noCompany=company_id,
            sCompanyName=company_name,
            sName=fake.name(),
            sPhone=fake.phone_number(),
            sExplain=random.choice(explanation_samples) if has_explanation else '',
            sPunish=random.choice(punishment_samples) if has_punishment else ''
        )
        reports.append(report)

    ClientReport.objects.bulk_create(reports)
    print(f"ClientReport {len(reports)}개 생성 완료!")

def main():
    print("Contract 앱 테스트 데이터 생성을 시작합니다...")

    try:
        # 기존 데이터 삭제 여부 확인
        existing_company_reports = CompanyReport.objects.count()
        existing_client_reports = ClientReport.objects.count()

        print(f"기존 CompanyReport: {existing_company_reports}개")
        print(f"기존 ClientReport: {existing_client_reports}개")

        # CompanyReport 데이터 생성
        create_company_reports()

        # ClientReport 데이터 생성
        create_client_reports()

        print("\n=== 데이터 생성 완료 ===")
        print(f"총 CompanyReport: {CompanyReport.objects.count()}개")
        print(f"총 ClientReport: {ClientReport.objects.count()}개")

    except Exception as e:
        print(f"에러 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()