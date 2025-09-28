#!/usr/bin/env python3
import os
import sys
import django

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testpark_project.settings')
django.setup()

from evaluation.models import Satisfy

# 데이터 확인
print("\n=== Satisfy 테스트 데이터 확인 ===\n")
print(f"전체 데이터 수: {Satisfy.objects.count()}개\n")

print("최근 입력된 데이터 5개:")
print("-" * 80)
for satisfy in Satisfy.objects.order_by('-created_at')[:5]:
    print(f"ID: {satisfy.no}")
    print(f"  업체명: {satisfy.sCompanyName}")
    print(f"  업체ID: {satisfy.noCompany}")
    print(f"  전화번호: {satisfy.sPhone}")
    print(f"  공사금액: {satisfy.sConMoney}")
    print(f"  지역: {satisfy.sArea}")
    print(f"  평가점수: nS1={satisfy.nS1}, nS2={satisfy.nS2}, nS3={satisfy.nS3}, nS4={satisfy.nS4}, nS5={satisfy.nS5}")
    print(f"            nS6={satisfy.nS6}, nS7={satisfy.nS7}, nS8={satisfy.nS8}, nS9={satisfy.nS9}, nS10={satisfy.nS10}")
    print(f"  만족도 합계: {satisfy.fSatisfySum}점 ({satisfy.get_satisfaction_level()})")
    print(f"  타임스탬프: {satisfy.sTimeStamp}")
    print(f"  날짜시간: {satisfy.timeStamp}")
    if satisfy.sS11:
        print(f"  추가의견: {satisfy.sS11[:50]}...")
    print("-" * 80)

# 통계 정보
from django.db.models import Avg, Count, Max, Min

stats = Satisfy.objects.aggregate(
    평균점수=Avg('fSatisfySum'),
    최고점수=Max('fSatisfySum'),
    최저점수=Min('fSatisfySum')
)

print("\n=== 만족도 통계 ===")
print(f"평균 만족도: {stats['평균점수']:.1f}점")
print(f"최고 만족도: {stats['최고점수']}점")
print(f"최저 만족도: {stats['최저점수']}점")

# 만족도 레벨별 분포
print("\n=== 만족도 레벨 분포 ===")
for satisfy in Satisfy.objects.all():
    level = satisfy.get_satisfaction_level()

levels_count = {}
for satisfy in Satisfy.objects.all():
    level = satisfy.get_satisfaction_level()
    levels_count[level] = levels_count.get(level, 0) + 1

for level, count in sorted(levels_count.items()):
    print(f"{level}: {count}건")