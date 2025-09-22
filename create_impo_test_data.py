#!/usr/bin/env python
"""
공사불가능 기간(ImpossibleTerm) 테스트 데이터 생성 스크립트
"""

import os
import sys
import django
from datetime import date, timedelta
import random

# Django 설정
sys.path.append('/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testpark_project.settings')
django.setup()

from impossibleterm.models import ImpossibleTerm
from company.models import Company

def create_test_data():
    """테스트 데이터 생성"""

    # 기존 데이터 삭제
    ImpossibleTerm.objects.all().delete()
    print("기존 ImpossibleTerm 데이터 삭제 완료")

    # 업체 목록 가져오기
    companies = list(Company.objects.all())
    if not companies:
        print("업체 데이터가 없습니다. Company 데이터를 먼저 생성해주세요.")
        return

    print(f"총 {len(companies)}개 업체 발견")

    # 설정자 목록
    workers = ['관리자', '홍길동', '김철수', '이영희', '박민수', '최지은']

    # 오늘 날짜 기준
    today = date.today()

    # 15개 테스트 데이터 생성
    test_data = []

    for i in range(1, 16):
        # 랜덤 업체 선택
        company = random.choice(companies)

        # 랜덤 설정자 선택
        worker = random.choice(workers)

        # 다양한 날짜 패턴 생성
        if i <= 5:
            # 과거 기간 (해제된 상태)
            start_date = today - timedelta(days=random.randint(30, 90))
            end_date = today - timedelta(days=random.randint(1, 29))
        elif i <= 10:
            # 현재 진행 중 (적용 중 상태)
            start_date = today - timedelta(days=random.randint(1, 15))
            end_date = today + timedelta(days=random.randint(1, 30))
        else:
            # 미래 기간 (예정 상태)
            start_date = today + timedelta(days=random.randint(1, 15))
            end_date = today + timedelta(days=random.randint(16, 60))

        test_data.append({
            'noCompany': company.no,
            'dateStart': start_date,
            'dateEnd': end_date,
            'sWorker': worker
        })

    # 데이터 저장
    created_records = []
    for data in test_data:
        impo = ImpossibleTerm.objects.create(**data)
        created_records.append(impo)
        print(f"생성: #{impo.no} - {impo.get_company_name()} ({impo.dateStart} ~ {impo.dateEnd}) - {impo.get_status_display()}")

    print(f"\n총 {len(created_records)}개의 ImpossibleTerm 테스트 데이터가 생성되었습니다!")

    # 통계 출력
    active_count = sum(1 for impo in created_records if impo.is_active())
    pending_count = sum(1 for impo in created_records if impo.dateStart > today)
    ended_count = len(created_records) - active_count - pending_count

    print(f"\n📊 상태별 통계:")
    print(f"해제: {ended_count}개")
    print(f"적용 중: {active_count}개")
    print(f"예정: {pending_count}개")

if __name__ == "__main__":
    try:
        create_test_data()
    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()