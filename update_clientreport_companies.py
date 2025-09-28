import os
import sys
import django
import random

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testpark_project.settings')
sys.path.append('/Users/sewookpark/Documents/testpark')
django.setup()

from contract.models import ClientReport
from company.models import Company

def update_clientreport_companies():
    """ClientReport의 업체 정보를 실제 Company 데이터로 업데이트"""

    # 모든 Company 데이터 가져오기
    companies = Company.objects.all()

    if not companies:
        print("❌ Company 데이터가 없습니다. 먼저 Company 데이터를 생성해주세요.")
        return 0

    print(f"✅ 사용 가능한 Company 수: {companies.count()}개")

    # 방금 생성한 ClientReport 데이터 가져오기 (최근 30개)
    client_reports = ClientReport.objects.all().order_by('-no')[:30]

    if not client_reports:
        print("❌ ClientReport 데이터가 없습니다.")
        return 0

    print(f"✅ 업데이트할 ClientReport 수: {len(client_reports)}개")

    updated_count = 0

    for report in client_reports:
        # 랜덤으로 Company 선택
        random_company = random.choice(companies)

        # ClientReport 업데이트
        report.noCompany = random_company.no
        report.sCompanyName = random_company.sName2 if random_company.sName2 else f"업체{random_company.no}"
        report.save()

        updated_count += 1
        print(f"업데이트 {updated_count}: ClientReport #{report.no} -> Company #{random_company.no} ({report.sCompanyName})")

    print(f"\n✅ 총 {updated_count}개의 ClientReport 업체 정보가 업데이트되었습니다!")
    return updated_count

if __name__ == "__main__":
    try:
        # 먼저 Company 데이터 확인
        company_count = Company.objects.count()
        print(f"📊 현재 Company 데이터: {company_count}개")

        if company_count == 0:
            print("⚠️ Company 데이터가 없습니다. Company 데이터를 먼저 생성해주세요.")
        else:
            # ClientReport 업데이트 실행
            count = update_clientreport_companies()
            print(f"✅ 성공적으로 {count}개의 ClientReport를 업데이트했습니다.")

            # 업데이트 결과 샘플 출력
            print("\n📋 업데이트된 데이터 샘플 (처음 5개):")
            sample_reports = ClientReport.objects.all().order_by('-no')[:5]
            for report in sample_reports:
                print(f"  - ClientReport #{report.no}: Company #{report.noCompany} - {report.sCompanyName}")

    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()