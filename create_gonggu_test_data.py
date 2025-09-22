#!/usr/bin/env python3
"""
Gonggu 관련 모든 모델에 테스트 데이터를 생성하는 스크립트
- Gonggu: 10개
- GongguArea: 30개 (각 Gonggu당 평균 3개)
"""
import os
import sys
import django
import random
from datetime import date, datetime, timedelta
from faker import Faker

# Django 환경 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testpark_project.settings')
django.setup()

from gonggu.models import Gonggu, GongguArea
from company.models import Company
from area.models import Area

# Faker 한국어 설정
fake = Faker('ko_KR')

def create_gonggus(count=10):
    """Gonggu 테스트 데이터 생성"""
    print(f"Gonggu {count}개 생성 중...")

    # 공구 이름 템플릿
    gonggu_names = [
        "2024년 상반기 아파트 올수리 공동구매",
        "경기도 주택 리모델링 특가 공구",
        "서울/경기 부분수리 할인 이벤트",
        "전국 상가 인테리어 공동구매",
        "봄맞이 도배/마루 특별 공구",
        "여름 방수공사 대규모 공구",
        "가을 외벽도색 단체 할인",
        "연말 대청소 리모델링 공구",
        "신축 아파트 입주 준비 공구",
        "겨울 난방비 절약 단열 공구",
        "베란다 확장 전문 공구",
        "욕실 리모델링 완전 패키지",
        "주방 시설 교체 공동구매",
        "펜션/카페 인테리어 공구",
        "오피스텔 원룸 꾸미기 공구"
    ]

    # 공구 특징 템플릿
    strength_templates = [
        "A급 자재만 사용, 전국 AS 보장",
        "20년 경력 전문가 직접 시공",
        "최대 40% 할인 혜택 제공",
        "무료 현장 견적 및 상담",
        "친환경 자재 100% 사용",
        "시공 후 5년 무상 A/S",
        "당일 견적, 익일 시공 가능",
        "소음 최소화 특수 공법 적용",
        "국산 프리미엄 자재 사용",
        "24시간 고객 상담 서비스"
    ]

    # 공지글 템플릿
    post_templates = [
        "공구 참여 업체 모집 중입니다!",
        "조기 마감 예상, 서둘러 신청하세요!",
        "품질 보장, 최저가 공급!",
        "한정 수량! 놓치면 후회하는 기회!",
        "검증된 업체만 참여 가능합니다",
        "고객 만족도 98% 달성 공구",
        "전국 어디든 시공 가능합니다",
        "무료 상담 및 견적 제공 중",
        "프리미엄 서비스, 합리적 가격",
        "안전시공 인증 업체만 선별"
    ]

    gonggus = []

    for i in range(count):
        # 시작일과 마감일 설정 (랜덤하게)
        start_date = fake.date_between(start_date='-60d', end_date='+30d')
        end_date = start_date + timedelta(days=random.randint(7, 90))

        gonggu = Gonggu(
            nStepType=random.choice([0, 1, 3, 4]),  # 진행구분
            nType=random.choice([0, 1]),  # 구분 (올수리/부분기타)
            sNo=f"{2024}-{str(i+1).zfill(3)}",  # 공구회차
            dateStart=start_date,
            dateEnd=end_date,
            sName=random.choice(gonggu_names),
            sPost=random.choice(post_templates),
            sStrength=random.choice(strength_templates),
            nCommentPre=random.randint(0, 50),  # 이전 댓글수
            nCommentNow=random.randint(0, 200)  # 현재 댓글수
        )

        # 현재 댓글수가 이전 댓글수보다 적으면 조정
        if gonggu.nCommentNow < gonggu.nCommentPre:
            gonggu.nCommentNow = gonggu.nCommentPre + random.randint(0, 50)

        gonggus.append(gonggu)

    Gonggu.objects.bulk_create(gonggus)
    print(f"✅ Gonggu {count}개 생성 완료")
    return Gonggu.objects.all()

def create_gonggu_areas(gonggus, count=30):
    """GongguArea 테스트 데이터 생성"""
    print(f"GongguArea {count}개 생성 중...")

    # 업체 ID 목록 가져오기
    company_ids = list(Company.objects.values_list('no', flat=True))
    if not company_ids:
        print("⚠️ Company 데이터가 없습니다. 임시로 1-31 범위 사용")
        company_ids = list(range(1, 32))

    # 지역 ID 목록 가져오기
    area_ids = list(Area.objects.values_list('no', flat=True))
    if not area_ids:
        print("⚠️ Area 데이터가 없습니다. 임시로 1-100 범위 사용")
        area_ids = list(range(1, 101))

    gonggu_areas = []
    gonggu_list = list(gonggus)
    created_combinations = set()  # 중복 방지용

    for i in range(count):
        attempts = 0
        max_attempts = 100

        while attempts < max_attempts:
            # 랜덤하게 공구, 업체, 지역 선택
            gonggu = random.choice(gonggu_list)
            company_id = random.choice(company_ids)
            area_id = random.choice(area_ids)

            # 중복 조합 확인
            combination = (gonggu.no, company_id, area_id)

            if combination not in created_combinations:
                created_combinations.add(combination)

                gonggu_area = GongguArea(
                    noGonggu=gonggu.no,
                    noCompany=company_id,
                    nType=random.choice([0, 1, 2]),  # 보관형식 랜덤
                    noArea=area_id
                )
                gonggu_areas.append(gonggu_area)
                break

            attempts += 1

        if attempts >= max_attempts:
            print(f"⚠️ {i+1}번째 GongguArea 생성 실패 (중복 조합)")

    if gonggu_areas:
        GongguArea.objects.bulk_create(gonggu_areas)
        print(f"✅ GongguArea {len(gonggu_areas)}개 생성 완료")
    else:
        print("❌ GongguArea 생성 실패")

def main():
    """메인 실행 함수"""
    print("Gonggu 관련 테스트 데이터 생성 시작...")
    print("=" * 50)

    # 기존 데이터 삭제 여부 확인
    existing_gonggus = Gonggu.objects.count()
    if existing_gonggus > 0:
        print(f"⚠️ 기존 Gonggu 데이터 {existing_gonggus}개가 있습니다.")
        print("기존 데이터를 삭제하고 새로 생성합니다.")
        Gonggu.objects.all().delete()
        GongguArea.objects.all().delete()

    # 1. Gonggu 10개 생성
    gonggus = create_gonggus(10)

    # 2. GongguArea 30개 생성
    create_gonggu_areas(gonggus, 30)

    print("=" * 50)
    print("🎉 모든 Gonggu 테스트 데이터 생성 완료!")
    print(f"📊 생성된 데이터:")
    print(f"   - Gonggu: {Gonggu.objects.count()}개")
    print(f"   - GongguArea: {GongguArea.objects.count()}개")

    # 통계 정보 출력
    print(f"\n📈 Gonggu 진행구분 통계:")
    for step_type, label in Gonggu.STEP_TYPE_CHOICES:
        count = Gonggu.objects.filter(nStepType=step_type).count()
        print(f"   - {label}: {count}개")

    print(f"\n📈 GongguArea 보관형식 통계:")
    for area_type, label in GongguArea.TYPE_CHOICES:
        count = GongguArea.objects.filter(nType=area_type).count()
        print(f"   - {label}: {count}개")

if __name__ == '__main__':
    main()