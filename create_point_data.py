#!/usr/bin/env python
import os
import sys
import django
import random
from faker import Faker
from datetime import datetime, timedelta
from django.utils import timezone

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testpark_project.settings')
django.setup()

from point.models import Point
from company.models import Company
from contract.models import CompanyReport

fake = Faker('ko_KR')

def create_point_data():
    """Point 테스트 데이터 30개 생성"""
    print("Point 테스트 데이터 생성 중...")

    # 기존 데이터 확인
    companies = list(Company.objects.all())
    company_reports = list(CompanyReport.objects.all())

    if not companies:
        print("Company 데이터가 없습니다. 먼저 Company 데이터를 생성해주세요.")
        return

    print(f"사용 가능한 Company: {len(companies)}개")
    print(f"사용 가능한 CompanyReport: {len(company_reports)}개")

    points = []

    # 포인트 타입별 샘플 데이터
    point_samples = [
        {
            'type': 0,  # 기타
            'workers': ['관리자', '시스템', '운영팀'],
            'use_points': [0, 100, 200, 500],
            'memos': [
                '기타 포인트 조정',
                '시스템 오류 보정',
                '특별 이벤트 포인트',
                '관리자 수동 조정'
            ]
        },
        {
            'type': 1,  # 취소환불액
            'workers': ['환불팀', '고객센터', '관리자'],
            'use_points': [0],  # 환불은 포인트 증가
            'memos': [
                '계약 취소로 인한 환불',
                '고객 요청 환불 처리',
                '불만족으로 인한 환불',
                '오류 계약 환불 처리'
            ]
        },
        {
            'type': 2,  # 과/미입금
            'workers': ['회계팀', '정산팀', '관리자'],
            'use_points': [0, 50, 100, 150, 300],
            'memos': [
                '과입금 포인트 적립',
                '미입금 포인트 차감',
                '입금 오차 조정',
                '계약금 정산 조정'
            ]
        },
        {
            'type': 3,  # 페이백 적립
            'workers': ['마케팅팀', '시스템', '이벤트팀'],
            'use_points': [0],  # 적립은 포인트 증가
            'memos': [
                '성과 달성 페이백',
                '우수 업체 보상',
                '추천 보상 포인트',
                '목표 달성 인센티브'
            ]
        },
        {
            'type': 4,  # 닷컴포인트 전환
            'workers': ['포인트팀', '시스템', '관리자'],
            'use_points': [100, 200, 500, 1000, 2000],
            'memos': [
                '닷컴포인트로 전환',
                '포인트 현금화',
                '제휴 포인트 전환',
                '외부 포인트 연동'
            ]
        },
        {
            'type': 5,  # 포인트 소멸
            'workers': ['시스템', '관리자', '정산팀'],
            'use_points': [50, 100, 200, 500, 1000],
            'memos': [
                '유효기간 만료',
                '휴면 계정 포인트 소멸',
                '약관 위반 포인트 차감',
                '시스템 정리 소멸'
            ]
        }
    ]

    # 업체별 현재 포인트 추적 (포인트 히스토리를 위해)
    company_points = {}
    for company in companies:
        company_points[company.no] = random.randint(0, 5000)  # 초기 포인트

    for i in range(30):
        # 랜덤 데이터 선택
        company = random.choice(companies)
        point_type = random.randint(0, 5)
        sample_data = point_samples[point_type]

        # 업체계약보고 연결 (50% 확률)
        company_report = random.choice(company_reports) if company_reports and random.choice([True, False]) else None

        # 작업자 선택
        worker = random.choice(sample_data['workers'])

        # 포인트 계산
        current_points = company_points.get(company.no, 0)
        use_point = random.choice(sample_data['use_points'])

        # 포인트 타입에 따른 포인트 변동 계산
        if point_type in [1, 3]:  # 취소환불액, 페이백 적립 - 포인트 증가
            point_change = random.randint(500, 3000)
            new_points = current_points + point_change
            use_point = 0  # 사용이 아닌 적립
        elif point_type in [4, 5]:  # 닷컴포인트 전환, 포인트 소멸 - 포인트 감소
            max_use = min(current_points, use_point) if current_points > 0 else 0
            use_point = max_use
            new_points = current_points - use_point
        else:  # 기타, 과/미입금 - 다양한 변동
            if random.choice([True, False]):  # 50% 확률로 증가/감소
                point_change = random.randint(100, 1000)
                new_points = current_points + point_change
                use_point = 0
            else:
                max_use = min(current_points, use_point) if current_points > 0 else 0
                use_point = max_use
                new_points = current_points - use_point

        # 음수 방지
        new_points = max(0, new_points)

        # 메모 선택
        memo = random.choice(sample_data['memos'])

        # 시간 생성 (최근 6개월 내)
        time = timezone.make_aware(fake.date_time_between(start_date='-6M', end_date='now'))

        point = Point(
            noCompany=company,
            time=time,
            nType=point_type,
            noCompanyReport=company_report,
            sWorker=worker,
            nPrePoint=current_points,
            nUsePoint=use_point,
            nRemainPoint=new_points,
            sMemo=memo
        )
        points.append(point)

        # 업체 포인트 업데이트
        company_points[company.no] = new_points

    Point.objects.bulk_create(points)
    print(f"Point {len(points)}개 생성 완료!")

def main():
    print("Point 앱 테스트 데이터 생성을 시작합니다...")

    try:
        # 기존 데이터 확인
        existing_count = Point.objects.count()
        print(f"기존 Point: {existing_count}개")

        # Point 데이터 생성
        create_point_data()

        print("\n=== 데이터 생성 완료 ===")
        print(f"총 Point: {Point.objects.count()}개")

        # 타입별 통계
        print("\n=== 타입별 통계 ===")
        for type_choice in Point.TYPE_CHOICES:
            count = Point.objects.filter(nType=type_choice[0]).count()
            print(f"{type_choice[1]}: {count}개")

        # 포인트 통계
        print("\n=== 포인트 통계 ===")
        from django.db.models import Sum, Avg, Max, Min

        stats = Point.objects.aggregate(
            total_use=Sum('nUsePoint'),
            avg_remain=Avg('nRemainPoint'),
            max_remain=Max('nRemainPoint'),
            min_remain=Min('nRemainPoint')
        )

        print(f"총 사용 포인트: {stats['total_use']:,}pt")
        print(f"평균 잔액: {stats['avg_remain']:.0f}pt")
        print(f"최대 잔액: {stats['max_remain']:,}pt")
        print(f"최소 잔액: {stats['min_remain']:,}pt")

        # 업체별 통계 (상위 5개)
        print("\n=== 업체별 포인트 현황 (상위 5개) ===")
        from django.db.models import OuterRef, Subquery

        # 각 업체의 최신 포인트 조회
        latest_points = Point.objects.filter(
            noCompany=OuterRef('noCompany')
        ).order_by('-time', '-no')

        top_companies = Point.objects.filter(
            no__in=Subquery(latest_points.values('no')[:1])
        ).select_related('noCompany').order_by('-nRemainPoint')[:5]

        for point in top_companies:
            print(f"{point.noCompany.sName1}: {point.nRemainPoint:,}pt")

        # 작업자별 통계
        print("\n=== 작업자별 통계 ===")
        from django.db.models import Count
        worker_stats = Point.objects.values('sWorker').annotate(
            count=Count('no'),
            total_handled=Sum('nUsePoint')
        ).order_by('-count')[:5]

        for stat in worker_stats:
            print(f"{stat['sWorker']}: {stat['count']}건, 처리 포인트 {stat['total_handled']:,}pt")

    except Exception as e:
        print(f"에러 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()