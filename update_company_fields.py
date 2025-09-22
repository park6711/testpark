#!/usr/bin/env python3
"""
Company 모델의 새로운 필드들에 테스트 데이터를 채우는 스크립트
"""
import os
import sys
import django
import random
from datetime import date

# Django 환경 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testpark_project.settings')
django.setup()

from company.models import Company
from stop.models import Stop

def update_company_fields():
    """Company 필드 업데이트"""

    companies = Company.objects.all()
    print(f"총 {companies.count()}개 업체 필드 업데이트 시작...")

    for company in companies:
        print(f"\n업체 {company.no}: {company.sCompanyName} 처리 중...")

        # Stop 데이터에서 일시정지 정보 가져오기
        stops = Stop.objects.filter(noCompany=company.no)

        if stops.exists():
            # 가장 최근 Stop의 sStop 사용
            latest_stop = stops.first()
            company.sStop = latest_stop.sStop

            # 가장 빠른 dateStart
            earliest_start = stops.aggregate(min_date=models.Min('dateStart'))['min_date']
            company.dateStopStart = earliest_start

            # 가장 늦은 dateEnd
            latest_end = stops.aggregate(max_date=models.Max('dateEnd'))['max_date']
            company.dateStopEnd = latest_end

            print(f"  - Stop 데이터 연동: {company.sStop[:50]}...")
        else:
            # Stop 데이터가 없으면 기본값
            company.sStop = ""
            company.dateStopStart = None
            company.dateStopEnd = None
            print("  - Stop 데이터 없음")

        # 레벨과 등급 (0~10)
        level = random.randint(0, 10)
        company.nLevel = level
        company.nGrade = level  # nLevel과 동일
        company.nApplyGrade = level  # nLevel과 동일

        # 적용등급 사유 (간단한 예시)
        grade_reasons = [
            "신규 업체", "평가 기간 중", "우수 업체", "일반 업체",
            "개선 필요", "우수 등급 승격", "일반 등급 유지"
        ]
        company.sApplyGradeReason = random.choice(grade_reasons)

        # 할당 수량 (0~2)
        company.nAssignAll2 = random.randint(0, 2)
        company.nAssignPart2 = random.randint(0, 2)

        # 평가기간 할당 수량 (20~30)
        company.nAssignAllTerm = random.randint(20, 30)
        company.nAssignPartTerm = random.randint(20, 30)

        # 최대할당수 = (nApplyGrade+1)*2+2
        company.nAssignMax = (company.nApplyGrade + 1) * 2 + 2

        # 할당퍼센트 = (nAssignAllTerm + nAssignPartTerm/2) / nAssignMax * 100
        if company.nAssignMax > 0:
            company.fAssignPercent = round(
                (company.nAssignAllTerm + company.nAssignPartTerm / 2) / company.nAssignMax * 100, 2
            )
        else:
            company.fAssignPercent = 0.0

        # 할당부족개수 (0~2)
        company.fAssignLack = round(random.uniform(0, 2), 1)

        # 저장
        company.save()

        print(f"  ✅ 업데이트 완료:")
        print(f"     레벨: {company.nLevel}, 등급: {company.nGrade}, 적용등급: {company.nApplyGrade}")
        print(f"     할당: All2={company.nAssignAll2}, Part2={company.nAssignPart2}")
        print(f"     평가기간: AllTerm={company.nAssignAllTerm}, PartTerm={company.nAssignPartTerm}")
        print(f"     최대할당: {company.nAssignMax}, 퍼센트: {company.fAssignPercent}%")
        print(f"     할당부족: {company.fAssignLack}")

    print(f"\n✅ 모든 업체 필드 업데이트 완료!")

if __name__ == '__main__':
    # Django models import 추가
    from django.db import models
    update_company_fields()