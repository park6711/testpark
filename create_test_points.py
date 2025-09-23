"""
테스트용 Point 데이터 생성 스크립트
Django shell에서 실행: python manage.py shell < create_test_points.py
또는 python manage.py shell 후 exec(open('create_test_points.py').read())
"""

from point.models import Point
from company.models import Company
from datetime import datetime, timedelta
import random

# Company ID 1 확인
try:
    company = Company.objects.get(no=1)
    print(f"✓ Company found: {company.sName2}")
except Company.DoesNotExist:
    print("❌ Company with ID 1 not found!")
    exit()

# 기존 데이터 확인
existing = Point.objects.filter(noCompany_id=1).order_by('-no')
if existing.exists():
    last_point = existing.first()
    print(f"📊 Found {existing.count()} existing points for {company.sName2}")
    print(f"   Last point: #{last_point.no}, 잔액: {last_point.nRemainPoint:,}")
    initial_remain = last_point.nRemainPoint
else:
    print(f"📊 No existing points for {company.sName2}")
    initial_remain = 0  # 초기값 0으로 시작

# 테스트 데이터 생성
base_date = datetime.now()
current_remain = initial_remain

test_data = []
print("\n🔨 Creating test data...")
print("-" * 70)
print(f"{'#':<5} {'이전포인트':>12} {'적용포인트':>12} {'잔액포인트':>12} {'구분':<10}")
print("-" * 70)

for i in range(10):
    # nUsePoint는 양수/음수 랜덤 (포인트 차감/적립)
    # 양수: 포인트 차감, 음수: 포인트 적립
    if random.random() > 0.7:  # 30% 확률로 적립
        use_point = -random.randint(1000, 10000)  # 적립 (음수)
    else:  # 70% 확률로 차감
        use_point = random.randint(1000, 5000)  # 차감 (양수)

    # 이전 포인트는 이전 레코드의 잔액
    pre_point = current_remain

    # 잔액 계산: 이전포인트 + 적용포인트
    # 적용포인트가 양수면 잔액 증가, 음수면 잔액 감소
    remain_point = pre_point + use_point

    # 구분 타입 선택
    if use_point < 0:
        # 적립인 경우 주로 페이백적립(3)
        point_type = 3
    elif use_point > 3000:
        # 큰 금액 차감은 닷컴전환(4) 또는 포인트소멸(5)
        point_type = random.choice([4, 5])
    else:
        # 일반 차감
        point_type = random.choice([0, 1, 2])

    # 시간은 1시간씩 늘려가며 설정
    point_time = base_date + timedelta(hours=i+1)

    # 메모
    type_names = {
        0: "기타",
        1: "취소환불",
        2: "과/미입금",
        3: "페이백적립",
        4: "닷컴전환",
        5: "포인트소멸"
    }

    if use_point < 0:
        memo = f"테스트 포인트 적립 #{i+1} - {type_names[point_type]}"
    else:
        memo = f"테스트 포인트 차감 #{i+1} - {type_names[point_type]}"

    # Point 객체 생성
    point = Point(
        noCompany_id=1,
        time=point_time,
        nType=point_type,
        nPrePoint=pre_point,
        nUsePoint=use_point,
        nRemainPoint=remain_point,
        sWorker="테스트",
        sMemo=memo
    )
    test_data.append(point)

    # 출력
    print(f"{i+1:<5} {pre_point:>12,} {use_point:>+12,} {remain_point:>12,} {type_names[point_type]:<10}")

    # 다음 반복을 위해 현재 잔액 업데이트
    current_remain = remain_point

print("-" * 70)

# 데이터베이스에 저장
if test_data:
    Point.objects.bulk_create(test_data)
    print(f"\n✅ {len(test_data)}개의 테스트 포인트 데이터가 생성되었습니다.")
    print(f"   최종 잔액: {current_remain:,} 포인트")

    # 확인
    created = Point.objects.filter(noCompany_id=1).order_by('-time')[:10]
    print(f"\n📋 최근 생성된 포인트 내역 확인:")
    for p in created[:3]:
        print(f"   #{p.no}: {p.time.strftime('%m/%d %H:%M')} | "
              f"이전:{p.nPrePoint:,} + 적용:{p.nUsePoint:+,} = 잔액:{p.nRemainPoint:,}")
else:
    print("❌ No data created")