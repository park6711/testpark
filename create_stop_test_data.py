#!/usr/bin/env python
"""
Stop 테스트 데이터 생성 스크립트
"""

import os
import sys
import django
from datetime import date, timedelta

# Django 설정 초기화
if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testpark_project.settings')
    django.setup()

from stop.models import Stop

def create_stop_test_data():
    """Stop 테스트 데이터 생성"""

    # 기존 Stop 데이터 확인
    existing_count = Stop.objects.count()
    print(f"기존 Stop 데이터: {existing_count}개")

    # 오늘 날짜 기준
    today = date.today()

    # 테스트 데이터 정의
    stop_data = [
        {
            'noCompany': 1,
            'dateStart': today - timedelta(days=5),
            'dateEnd': today + timedelta(days=5),
            'sStop': '안전사고로 인한 임시 작업 중단',
            'bShow': True,
            'sWorker': '김관리자',
        },
        {
            'noCompany': 2,
            'dateStart': today + timedelta(days=3),
            'dateEnd': today + timedelta(days=10),
            'sStop': '정기 안전점검 및 장비 교체 작업',
            'bShow': True,
            'sWorker': '이안전관리자',
        },
        {
            'noCompany': 3,
            'dateStart': today - timedelta(days=15),
            'dateEnd': today - timedelta(days=8),
            'sStop': '환경 오염 방지를 위한 공사 중단',
            'bShow': False,
            'sWorker': '박환경관리자',
        },
        {
            'noCompany': 4,
            'dateStart': today - timedelta(days=2),
            'dateEnd': today + timedelta(days=3),
            'sStop': '날씨(태풍) 영향으로 인한 작업 중단',
            'bShow': True,
            'sWorker': '최현장관리자',
        },
        {
            'noCompany': 5,
            'dateStart': today + timedelta(days=7),
            'dateEnd': today + timedelta(days=14),
            'sStop': '인근 주민 민원 해결을 위한 공사 일시중단',
            'bShow': False,
            'sWorker': '정대표',
        },
        {
            'noCompany': 6,
            'dateStart': today - timedelta(days=20),
            'dateEnd': today - timedelta(days=10),
            'sStop': '자재 공급 지연으로 인한 작업 중단',
            'bShow': True,
            'sWorker': '강자재관리자',
        },
        {
            'noCompany': 7,
            'dateStart': today - timedelta(days=1),
            'dateEnd': today + timedelta(days=6),
            'sStop': '전력 공급 문제로 인한 장비 가동 중단',
            'bShow': True,
            'sWorker': '조전기관리자',
        },
        {
            'noCompany': 8,
            'dateStart': today + timedelta(days=14),
            'dateEnd': today + timedelta(days=21),
            'sStop': '하절기 고온으로 인한 작업자 안전을 위한 공사 조정',
            'bShow': True,
            'sWorker': '윤안전관리자',
        },
        {
            'noCompany': 9,
            'dateStart': today - timedelta(days=30),
            'dateEnd': today - timedelta(days=20),
            'sStop': '소음 규제 위반으로 인한 관할 기관 지시에 따른 중단',
            'bShow': False,
            'sWorker': '장법무팀',
        },
        {
            'noCompany': 10,
            'dateStart': today + timedelta(days=1),
            'dateEnd': today + timedelta(days=4),
            'sStop': '주말 및 공휴일 작업 금지 조치',
            'bShow': True,
            'sWorker': '임관리소장',
        },
    ]

    created_count = 0

    for data in stop_data:
        # 중복 체크 (업체번호 + 날짜 기준)
        if not Stop.objects.filter(
            noCompany=data['noCompany'],
            dateStart=data['dateStart'],
            dateEnd=data['dateEnd']
        ).exists():
            stop = Stop.objects.create(**data)
            created_count += 1
            status = "일시정지 중" if stop.is_active() else ("예정" if stop.dateStart > today else "해제됨")
            print(f"✅ Stop {stop.no} 생성: 업체{stop.noCompany} ({status}) - {stop.sWorker}")
        else:
            print(f"⚠️  업체{data['noCompany']} ({data['dateStart']} ~ {data['dateEnd']}) 이미 존재")

    total_count = Stop.objects.count()
    print(f"\n📊 결과:")
    print(f"   - 새로 생성된 Stop: {created_count}개")
    print(f"   - 전체 Stop 개수: {total_count}개")

    # 현재 활성 상태 통계
    active_count = Stop.objects.filter(dateStart__lte=today, dateEnd__gte=today).count()
    print(f"   - 현재 일시정지 중: {active_count}개")

    return created_count, total_count

if __name__ == '__main__':
    print("🛑 Stop 테스트 데이터 생성 시작...")
    print("=" * 50)

    try:
        created, total = create_stop_test_data()
        print("=" * 50)
        print("✅ Stop 테스트 데이터 생성 완료!")

    except Exception as e:
        print("=" * 50)
        print(f"❌ 오류 발생: {str(e)}")
        sys.exit(1)