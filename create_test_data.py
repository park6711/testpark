#!/usr/bin/env python
"""CompanyReport 테스트 데이터 생성 스크립트"""
import os
import sys
import django
from datetime import datetime, date
from decimal import Decimal

# Django 설정
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "testpark_project.settings")
os.environ["USE_MYSQL"] = "True"
os.environ["DB_HOST"] = "localhost"
os.environ["DB_NAME"] = "testpark"
os.environ["DB_USER"] = "testpark"
os.environ["DB_PASSWORD"] = "**jeje4211"

django.setup()

from contract.models import CompanyReport, ClientReport
from company.models import Company
from django.contrib.auth import get_user_model

User = get_user_model()

def create_test_data():
    """테스트 데이터 생성"""

    # 테스트 사용자 생성 또는 가져오기
    user, created = User.objects.get_or_create(
        username="testuser",
        defaults={
            "email": "test@example.com",
            "first_name": "테스트",
            "last_name": "사용자"
        }
    )
    if created:
        print(f"✓ 테스트 사용자 생성: {user.username}")
    else:
        print(f"✓ 기존 테스트 사용자 사용: {user.username}")

    # 테스트 업체 생성
    companies = []
    company_names = [
        ("(주)삼성인테리어", "삼성인테리어"),
        ("(주)현대디자인", "현대디자인"),
        ("LG하우징", "LG하우징"),
        ("SK건설인테리어", "SK건설"),
        ("대우인테리어", "대우인테리어"),
        ("한화리모델링", "한화리모델링"),
        ("롯데하우징", "롯데하우징"),
        ("포스코인테리어", "포스코인테리어"),
        ("GS건설디자인", "GS건설"),
        ("두산인테리어", "두산인테리어")
    ]

    for sName1, sName2 in company_names:
        company, created = Company.objects.get_or_create(
            sName2=sName2,
            defaults={
                "sName1": sName1,
                "sName3": sName2[:3] if len(sName2) >= 3 else sName2,
                "sCompanyName": f"{sName1} 정식명칭",
                "sAddress": "서울특별시 강남구 테스트로 123",
                "sMemo": f"{sName2} 테스트 업체",
                "nType": 0,  # 일반토탈
                "nCondition": 1  # 정상
            }
        )
        companies.append(company)
        if created:
            print(f"  ✓ 업체 생성: {company.sName2}")
        else:
            print(f"  - 기존 업체: {company.sName2}")

    # ClientReport 생성 (CompanyReport와 연결하기 위해)
    client_report, created = ClientReport.objects.get_or_create(
        sName="테스트 고객",
        sPhone="010-1234-5678",
        defaults={
            "sArea": "서울",
            "sMemo": "테스트 고객 메모"
        }
    )
    if created:
        print(f"\n✓ ClientReport 생성: {client_report.sName}")
    else:
        print(f"\n- 기존 ClientReport 사용: {client_report.sName}")

    # ID 30번 CompanyReport 생성
    try:
        # 먼저 30번이 이미 있는지 확인
        existing = CompanyReport.objects.filter(no=30).first()
        if existing:
            print(f"\n✓ 기존 CompanyReport #30 존재: {existing}")
            # 업체가 없으면 첫 번째 업체 할당
            if not existing.noCompany and companies:
                existing.noCompany = companies[0].no
                existing.save()
                print(f"  - 업체 할당: {companies[0].sName2}")
        else:
            # 새로 생성
            report = CompanyReport.objects.create(
                no=30,  # ID 명시적 설정
                noCompany=companies[0].no if companies else None,
                noClientReport=client_report.no,
                iCount=1,
                bType=1,
                fFee=Decimal("100000.00"),
                bFeeStatus=0,
                bStatus=1,
                dDate=date.today(),
                sMemo="테스트 CompanyReport #30",
                sUser=user.username
            )
            print(f"\n✓ CompanyReport #30 생성 완료")
            print(f"  - 업체: {companies[0].sName2 if companies else 'None'}")
            print(f"  - 상태: {report.get_bStatus_display() if hasattr(report, 'get_bStatus_display') else report.bStatus}")
    except Exception as e:
        print(f"\n⚠️ CompanyReport #30 생성 실패: {e}")
        # AUTO_INCREMENT 재설정 시도
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT MAX(no) FROM contract_companyreport")
            max_id = cursor.fetchone()[0] or 0
            if max_id < 30:
                # 29번까지 더미 데이터 생성
                for i in range(max_id + 1, 30):
                    try:
                        CompanyReport.objects.create(
                            noCompany=companies[i % len(companies)].no if companies else None,
                            noClientReport=client_report.no,
                            iCount=1,
                            bType=1,
                            fFee=Decimal("50000.00"),
                            bFeeStatus=0,
                            bStatus=1,
                            dDate=date.today(),
                            sMemo=f"더미 데이터 #{i}",
                            sUser=user.username
                        )
                        print(f"  - 더미 #{i} 생성")
                    except Exception as dummy_e:
                        print(f"  ⚠️ 더미 #{i} 생성 실패: {dummy_e}")

                # 30번 재시도
                try:
                    report = CompanyReport.objects.create(
                        noCompany=companies[0].no if companies else None,
                        noClientReport=client_report.no,
                        iCount=1,
                        bType=1,
                        fFee=Decimal("100000.00"),
                        bFeeStatus=0,
                        bStatus=1,
                        dDate=date.today(),
                        sMemo="테스트 CompanyReport #30",
                        sUser=user.username
                    )
                    print(f"\n✓ CompanyReport #30 생성 성공 (재시도)")
                except Exception as retry_e:
                    print(f"\n❌ CompanyReport #30 생성 최종 실패: {retry_e}")

    # 추가 CompanyReport 생성 (테스트용)
    for i in range(1, 6):
        try:
            report = CompanyReport.objects.create(
                noCompany=companies[i % len(companies)].no if companies else None,
                noClientReport=client_report.no,
                iCount=i,
                bType=(i % 3) + 1,
                fFee=Decimal(f"{50000 * i}.00"),
                bFeeStatus=i % 2,
                bStatus=(i % 4) + 1,
                dDate=date.today(),
                sMemo=f"테스트 CompanyReport #{i}",
                sUser=user.username
            )
            print(f"  ✓ 추가 CompanyReport 생성: ID {report.no}")
        except Exception as e:
            print(f"  ⚠️ 추가 CompanyReport 생성 실패: {e}")

    # 생성된 데이터 확인
    print("\n========== 데이터 확인 ==========")
    total_companies = Company.objects.count()
    total_reports = CompanyReport.objects.count()
    report_30 = CompanyReport.objects.filter(no=30).first()

    print(f"총 업체 수: {total_companies}")
    print(f"총 CompanyReport 수: {total_reports}")
    if report_30:
        print(f"\nCompanyReport #30 정보:")
        print(f"  - ID: {report_30.no}")
        print(f"  - 업체 ID: {report_30.noCompany}")
        if report_30.noCompany:
            company = Company.objects.filter(no=report_30.noCompany).first()
            if company:
                print(f"  - 업체명: {company.sName2}")
        print(f"  - 메모: {report_30.sMemo}")
        print(f"  - 상태: {report_30.bStatus}")
    else:
        print("⚠️ CompanyReport #30이 존재하지 않습니다.")

    print("\n✅ 테스트 데이터 생성 완료!")
    print(f"URL 테스트: http://localhost:8000/contract/companyreport/30/detail/?mode=edit")

if __name__ == "__main__":
    create_test_data()
