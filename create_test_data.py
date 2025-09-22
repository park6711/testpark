#!/usr/bin/env python
"""
테스트 데이터 생성 스크립트
기존 Gonggu, GongguArea 데이터 삭제 후 새로운 테스트 데이터 생성
- Gonggu: 10개
- GongguCompany: 20개
- GongguArea: 40개
"""

import os
import sys
import django
from datetime import date, timedelta
import random

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testpark_project.settings')
django.setup()

from gonggu.models import Gonggu, GongguCompany, GongguArea
from company.models import Company
from area.models import Area

def delete_existing_data():
    """기존 데이터 삭제"""
    print("기존 데이터 삭제 중...")

    # GongguArea 먼저 삭제 (참조 관계 때문에)
    deleted_areas = GongguArea.objects.all().delete()
    print(f"GongguArea {deleted_areas[0]}개 삭제됨")

    # GongguCompany 삭제
    deleted_companies = GongguCompany.objects.all().delete()
    print(f"GongguCompany {deleted_companies[0]}개 삭제됨")

    # Gonggu 삭제
    deleted_gonggus = Gonggu.objects.all().delete()
    print(f"Gonggu {deleted_gonggus[0]}개 삭제됨")

    print("기존 데이터 삭제 완료\n")

def create_test_gonggus():
    """테스트 Gonggu 10개 생성"""
    print("Gonggu 테스트 데이터 생성 중...")

    gonggu_names = [
        "2024년 12월 전국 자동차 올수리 공구",
        "겨울 대비 난방기기 특가 공구",
        "스마트폰 액세서리 대량 공구",
        "주방용품 연말 특가 공구",
        "의류 겨울 신상품 공구",
        "생활용품 연말 정리 공구",
        "전자제품 신상 런칭 공구",
        "화장품 브랜드 콜라보 공구",
        "도서/문구 신학기 준비 공구",
        "펜트하우스 인테리어 공구"
    ]

    gonggu_strengths = [
        "전국 최저가 보장, A/S 3년 무료",
        "에너지 효율 1등급 제품만 선별",
        "정품 보장, 무료배송, 당일발송",
        "친환경 소재, 내구성 강화 제품",
        "트렌디한 디자인, 다양한 컬러 옵션",
        "생활 필수품 세트 구성, 가격 혜택",
        "최신 기술 적용, 품질 보증서 제공",
        "인기 브랜드 협업, 한정수량 특가",
        "교육부 인증 도서, 무료 배송",
        "프리미엄 브랜드, 럭셔리 인테리어"
    ]

    created_gonggus = []

    for i in range(10):
        start_date = date.today() + timedelta(days=random.randint(-30, 10))
        end_date = start_date + timedelta(days=random.randint(7, 30))

        gonggu = Gonggu.objects.create(
            nStepType=random.choice([0, 1, 2, 3]),  # 진행구분
            nType=random.choice([0, 1]),  # 구분 (올수리/부분기타)
            sNo=f"2024-{i+1:02d}",  # 공구회차
            dateStart=start_date,
            dateEnd=end_date,
            sName=gonggu_names[i],
            sPost=f"https://cafe.naver.com/gonggu{i+1:02d}",
            sStrength=gonggu_strengths[i],
            nCommentPre=random.randint(0, 50),  # 이전 댓글수
            nCommentNow=random.randint(0, 100)  # 현재 댓글수
        )
        created_gonggus.append(gonggu)
        print(f"Gonggu {gonggu.no}: {gonggu.sName}")

    print(f"Gonggu {len(created_gonggus)}개 생성 완료\n")
    return created_gonggus

def create_test_gonggu_companies(gonggus):
    """테스트 GongguCompany 20개 생성"""
    print("GongguCompany 테스트 데이터 생성 중...")

    # 기존 Company 데이터가 있는지 확인
    companies = list(Company.objects.all()[:50])  # 최대 50개 업체 사용
    if not companies:
        print("경고: Company 데이터가 없습니다. Company ID를 임의로 생성합니다.")
        company_ids = list(range(1, 51))  # 1~50 범위의 임의 ID
    else:
        company_ids = [company.no for company in companies]

    created_companies = []

    # 각 공구당 평균 2개의 업체가 참여하도록 분배
    for i in range(20):
        gonggu = random.choice(gonggus)
        company_id = random.choice(company_ids)

        # 중복 방지: 같은 공구-업체 조합이 이미 있는지 확인
        if GongguCompany.objects.filter(noGonggu=gonggu.no, noCompany=company_id).exists():
            # 중복이면 다른 업체 선택
            available_companies = [cid for cid in company_ids
                                 if not GongguCompany.objects.filter(noGonggu=gonggu.no, noCompany=cid).exists()]
            if available_companies:
                company_id = random.choice(available_companies)
            else:
                continue  # 해당 공구에 모든 업체가 참여중이면 스킵

        try:
            gonggu_company = GongguCompany.objects.create(
                noGonggu=gonggu.no,
                noCompany=company_id
            )
            created_companies.append(gonggu_company)
            print(f"GongguCompany {gonggu_company.no}: 공구{gonggu.no} - 업체{company_id}")
        except Exception as e:
            print(f"GongguCompany 생성 실패: {e}")
            continue

    print(f"GongguCompany {len(created_companies)}개 생성 완료\n")
    return created_companies

def create_test_gonggu_areas(gonggu_companies):
    """테스트 GongguArea 40개 생성"""
    print("GongguArea 테스트 데이터 생성 중...")

    # 기존 Area 데이터가 있는지 확인
    areas = list(Area.objects.all()[:100])  # 최대 100개 지역 사용
    if not areas:
        print("경고: Area 데이터가 없습니다. Area ID를 임의로 생성합니다.")
        area_ids = list(range(1, 101))  # 1~100 범위의 임의 ID
    else:
        area_ids = [area.no for area in areas]

    created_areas = []

    # 각 공구업체당 평균 2개의 지역이 할당되도록 분배
    for i in range(40):
        gonggu_company = random.choice(gonggu_companies)
        area_id = random.choice(area_ids)
        area_type = random.choice([0, 1, 2])  # 추가지역, 제외지역, 실제할당지역

        # 중복 방지는 현재 unique_together가 비활성화되어 있으므로 허용
        try:
            gonggu_area = GongguArea.objects.create(
                noGongguCompany=gonggu_company.no,
                nType=area_type,
                noArea=area_id
            )
            created_areas.append(gonggu_area)
            type_name = {0: "추가지역", 1: "제외지역", 2: "실제할당지역"}[area_type]
            print(f"GongguArea {gonggu_area.no}: 공구업체{gonggu_company.no} - 지역{area_id} ({type_name})")
        except Exception as e:
            print(f"GongguArea 생성 실패: {e}")
            continue

    print(f"GongguArea {len(created_areas)}개 생성 완료\n")
    return created_areas

def main():
    """메인 실행 함수"""
    print("=== 공구(Gonggu) 테스트 데이터 생성 스크립트 ===\n")

    try:
        # 1. 기존 데이터 삭제
        delete_existing_data()

        # 2. Gonggu 10개 생성
        gonggus = create_test_gonggus()

        # 3. GongguCompany 20개 생성
        gonggu_companies = create_test_gonggu_companies(gonggus)

        # 4. GongguArea 40개 생성
        gonggu_areas = create_test_gonggu_areas(gonggu_companies)

        print("=== 테스트 데이터 생성 완료 ===")
        print(f"총 생성된 데이터:")
        print(f"- Gonggu: {len(gonggus)}개")
        print(f"- GongguCompany: {len(gonggu_companies)}개")
        print(f"- GongguArea: {len(gonggu_areas)}개")

        # 5. 데이터 확인
        print(f"\n=== 데이터베이스 확인 ===")
        print(f"- Gonggu 총 개수: {Gonggu.objects.count()}개")
        print(f"- GongguCompany 총 개수: {GongguCompany.objects.count()}개")
        print(f"- GongguArea 총 개수: {GongguArea.objects.count()}개")

    except Exception as e:
        print(f"오류 발생: {e}")
        return False

    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)