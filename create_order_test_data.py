#!/usr/bin/env python3
"""
Order 관련 모든 모델에 테스트 데이터를 생성하는 스크립트
- Order: 40개
- Assign: 80개 (각 Order당 평균 2개)
- Estimate: 80개 (각 Assign당 1개)
- AssignMemo: 80개 (각 Assign당 1개)
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

from order.models import Order, Assign, Estimate, AssignMemo
from company.models import Company

# Faker 한국어 설정
fake = Faker('ko_KR')

def create_orders(count=40):
    """Order 테스트 데이터 생성"""
    print(f"Order {count}개 생성 중...")

    # 지역 목록
    areas = [
        "서울시 강남구", "서울시 서초구", "서울시 송파구", "서울시 강동구",
        "서울시 마포구", "서울시 용산구", "서울시 종로구", "서울시 중구",
        "경기도 성남시", "경기도 수원시", "경기도 안양시", "경기도 부천시",
        "인천시 연수구", "인천시 남동구", "부산시 해운대구", "부산시 서면"
    ]

    # 공사내용 목록
    constructions = [
        "아파트 베란다 확장 공사", "주택 리모델링 전체", "상가 인테리어 공사",
        "욕실 전체 리모델링", "주방 싱크대 교체", "방 도배 및 마루 시공",
        "아파트 전체 도배", "타일 부분 보수", "벽지 도배 작업",
        "상가 바닥 공사", "아파트 방수 공사", "주택 외벽 도색"
    ]

    orders = []
    for i in range(count):
        order = Order(
            sAppoint=random.choice(["지정없음", "업체지정", "공구지정"]),
            sNick=fake.user_name(),
            sNaverID=f"naver_{fake.user_name()}",
            sName=fake.name(),
            sPhone=fake.phone_number(),
            sPost=f"공사 의뢰드립니다 - {random.choice(['급함', '일반', '상담 후 결정'])}",
            sArea=random.choice(areas),
            dateSchedule=fake.date_between(start_date='-30d', end_date='+60d'),
            sConstruction=random.choice(constructions),
            bPrivacy1=random.choice([True, False]),
            bPrivacy2=random.choice([True, False])
        )
        orders.append(order)

    Order.objects.bulk_create(orders)
    print(f"✅ Order {count}개 생성 완료")
    return Order.objects.all()

def create_assigns(orders, count=80):
    """Assign 테스트 데이터 생성"""
    print(f"Assign {count}개 생성 중...")

    # 업체 ID 목록 가져오기
    company_ids = list(Company.objects.values_list('no', flat=True))
    if not company_ids:
        print("⚠️ Company 데이터가 없습니다. 임시로 1-31 범위 사용")
        company_ids = list(range(1, 32))

    # SMS 메시지 템플릿
    company_sms_templates = [
        "안녕하세요. 견적 문의 주셔서 감사합니다.",
        "상담 가능한 시간을 알려주세요.",
        "현장 확인 후 정확한 견적 드리겠습니다.",
        "문의해주신 공사 관련 연락드렸습니다."
    ]

    client_sms_templates = [
        "견적서가 발송되었습니다. 확인 부탁드립니다.",
        "상담 예약이 완료되었습니다.",
        "공사 일정이 확정되었습니다.",
        "추가 문의사항이 있으시면 연락주세요."
    ]

    workers = ["김관리", "이팀장", "박실장", "최부장", "정과장", "송대리"]

    assigns = []
    order_list = list(orders)

    for i in range(count):
        # 각 Order에 평균 2개의 Assign이 되도록 분배
        order = order_list[i % len(order_list)]

        assign = Assign(
            noOrder=order.no,
            noCompany=random.choice(company_ids),
            nConstructionType=random.randint(0, 7),  # 0-7: 공사종류
            nAssignType=random.randint(0, 8),  # 0-8: 할당상태
            sCompanyPhone=fake.phone_number(),
            sCompanySMS=random.choice(company_sms_templates),
            sClientPhone=order.sPhone,
            sClientSMS=random.choice(client_sms_templates),
            sWorker=random.choice(workers),
            noCompanyReport=random.randint(1, 100) if random.random() > 0.3 else None,
            nAppoint=random.randint(0, 2),  # 0-2: 지정종류
            noGonggu=random.randint(1, 50) if random.random() > 0.5 else None,
            noArea=random.randint(1, 100) if random.random() > 0.4 else None
        )
        assigns.append(assign)

    Assign.objects.bulk_create(assigns)
    print(f"✅ Assign {count}개 생성 완료")
    return Assign.objects.all()

def create_estimates(assigns, count=80):
    """Estimate 테스트 데이터 생성"""
    print(f"Estimate {count}개 생성 중...")

    # 견적서 게시글 템플릿
    estimate_posts = [
        "견적서 전달드립니다. 검토 후 연락주세요.",
        "상세 견적 내용 첨부하였습니다.",
        "현장 확인 후 작성한 정확한 견적입니다.",
        "추가 옵션 포함된 견적서입니다.",
        "기본 견적 + 부가 서비스 견적 포함",
        "재료비 포함 전체 견적서입니다.",
        "공사 기간 및 비용 상세 안내",
        "할인 적용된 최종 견적서입니다."
    ]

    estimates = []
    assign_list = list(assigns)

    for i in range(count):
        assign = assign_list[i % len(assign_list)]

        estimate = Estimate(
            noOrder=assign.noOrder,
            noAssign=assign.no,
            sPost=random.choice(estimate_posts)
        )
        estimates.append(estimate)

    Estimate.objects.bulk_create(estimates)
    print(f"✅ Estimate {count}개 생성 완료")
    return Estimate.objects.all()

def create_assign_memos(assigns, count=80):
    """AssignMemo 테스트 데이터 생성"""
    print(f"AssignMemo {count}개 생성 중...")

    workers = ["김관리", "이팀장", "박실장", "최부장", "정과장", "송대리"]

    # 메모 템플릿 (중요 키워드 포함)
    memo_templates = [
        "고객 연락 완료. 다음주 현장방문 예정",
        "견적서 발송 완료. 고객 검토 중",
        "중요: 공사 일정 변경 요청 있음",
        "업체 연락두절. 긴급 대응 필요",
        "현장 확인 완료. 추가 작업 필요",
        "고객 만족도 높음. 추가 공사 문의",
        "주의: 이웃 민원 가능성 있음",
        "자재 지연으로 일정 조정 필요",
        "문제: 업체 자격 미달 확인됨",
        "정상 진행 중. 특이사항 없음",
        "고객 추가 요구사항 확인",
        "이슈: 예산 초과 우려",
        "업체 교체 검토 중",
        "공사 완료. 정산 대기",
        "A/S 요청 접수",
        "재시공 필요 판정",
        "고객 컴플레인 접수",
        "우수 업체 추천 가능",
        "중요: 계약서 수정 필요",
        "긴급: 안전사고 예방 조치 필요"
    ]

    assign_memos = []
    assign_list = list(assigns)

    for i in range(count):
        assign = assign_list[i % len(assign_list)]

        memo = AssignMemo(
            noOrder=assign.noOrder,
            noAssign=assign.no,
            sWorker=random.choice(workers),
            sMemo=random.choice(memo_templates)
        )
        assign_memos.append(memo)

    AssignMemo.objects.bulk_create(assign_memos)
    print(f"✅ AssignMemo {count}개 생성 완료")

def main():
    """메인 실행 함수"""
    print("Order 관련 테스트 데이터 생성 시작...")
    print("=" * 50)

    # 기존 데이터 삭제 여부 확인
    existing_orders = Order.objects.count()
    if existing_orders > 0:
        print(f"⚠️ 기존 Order 데이터 {existing_orders}개가 있습니다.")
        print("기존 데이터를 삭제하고 새로 생성합니다.")
        Order.objects.all().delete()
        Assign.objects.all().delete()
        Estimate.objects.all().delete()
        AssignMemo.objects.all().delete()

    # 1. Order 40개 생성
    orders = create_orders(40)

    # 2. Assign 80개 생성
    assigns = create_assigns(orders, 80)

    # 3. Estimate 80개 생성
    estimates = create_estimates(assigns, 80)

    # 4. AssignMemo 80개 생성
    create_assign_memos(assigns, 80)

    print("=" * 50)
    print("🎉 모든 테스트 데이터 생성 완료!")
    print(f"📊 생성된 데이터:")
    print(f"   - Order: {Order.objects.count()}개")
    print(f"   - Assign: {Assign.objects.count()}개")
    print(f"   - Estimate: {Estimate.objects.count()}개")
    print(f"   - AssignMemo: {AssignMemo.objects.count()}개")

if __name__ == '__main__':
    main()