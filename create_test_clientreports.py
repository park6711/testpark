import os
import sys
import django
import random
from datetime import datetime, timedelta

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testpark_project.settings')
sys.path.append('/Users/sewookpark/Documents/testpark')
django.setup()

from contract.models import ClientReport
from django.utils import timezone

# 테스트 데이터 생성
def create_test_clientreports():
    # 샘플 업체명
    company_names = [
        '행복인테리어', '드림디자인', '모던하우스', '스타일홈', '뉴홈인테리어',
        '베스트디자인', '프리미엄홈', '아름다운집', '클린하우스', '파인인테리어'
    ]

    # 샘플 고객명
    customer_names = [
        '김철수', '이영희', '박민수', '최지은', '정대성',
        '강서연', '조민준', '윤서진', '임도현', '한지민',
        '송민호', '김나연', '이준호', '박소연', '최동욱',
        '정하늘', '강유진', '조현우', '윤미래', '임서윤'
    ]

    # 샘플 지역
    areas = [
        '서울시 강남구 역삼동', '서울시 서초구 서초동', '서울시 송파구 잠실동',
        '경기도 성남시 분당구', '경기도 용인시 수지구', '서울시 마포구 상암동',
        '서울시 강동구 천호동', '경기도 고양시 일산동구', '서울시 노원구 상계동',
        '경기도 수원시 영통구', '서울시 중구 명동', '서울시 종로구 종로'
    ]

    # 샘플 메모
    client_memos = [
        '빠른 시공 부탁드립니다', '깔끔하게 마무리 해주세요', '예산 내에서 최대한 잘 부탁드립니다',
        '소음 최소화 부탁드립니다', '자재는 친환경으로 해주세요', '디자인 상담 후 진행 원합니다',
        '공사 일정 조율 필요합니다', '견적서 상세히 부탁드립니다', '애완동물 있어서 조심해주세요',
        '주말 공사 가능한가요?', '급하지 않으니 천천히 해주세요', '품질 위주로 부탁드립니다'
    ]

    created_count = 0

    for i in range(30):
        # 랜덤 데이터 생성
        company_name = random.choice(company_names)
        customer_name = random.choice(customer_names) + str(random.randint(1, 100))
        area = random.choice(areas)
        phone = f"010-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}"

        # 공사금액 (100만원 ~ 5000만원)
        money = f"{random.randint(100, 5000)}만원"

        # 계약일 (최근 60일 이내)
        days_ago = random.randint(0, 60)
        contract_date = timezone.now().date() - timedelta(days=days_ago)

        # 확인 상태 (0: 미확인, 1: 불필요, 2: 계약O, 3: 계약X)
        check_status = random.choices([0, 1, 2, 3], weights=[40, 10, 35, 15])[0]

        # 소명 관련 (20% 확률로 소명 필요)
        if random.random() < 0.2:
            explain_date0 = timezone.now().date() + timedelta(days=random.randint(1, 30))
            explain_date1 = None if random.random() < 0.5 else explain_date0 + timedelta(days=random.randint(1, 10))
            explain = "고객 요청사항 변경으로 인한 지연" if explain_date1 else ""
            punish = "경고 조치" if explain_date1 and random.random() < 0.3 else ""
        else:
            explain_date0 = None
            explain_date1 = None
            explain = ""
            punish = ""

        # ClientReport 생성
        client_report = ClientReport.objects.create(
            sCompanyName=company_name,
            noCompany=random.randint(1, 50),
            sName=customer_name,
            sArea=area,
            sPhone=phone,
            sConMoney=money,
            dateContract=contract_date,
            sFile=f"https://example.com/contract_{i+1}.pdf",
            sClientMemo=random.choice(client_memos),
            sPost=f"https://cafe.naver.com/post/{random.randint(10000, 99999)}",
            noAssign=random.randint(1, 100) if random.random() < 0.7 else None,
            noCompanyReport=random.randint(1, 100) if random.random() < 0.5 else None,
            nCheck=check_status,
            sMemo=f"테스트 메모 #{i+1}" if random.random() < 0.3 else "",
            dateExplain0=explain_date0,
            dateExplain1=explain_date1,
            sExplain=explain,
            sPunish=punish
        )

        created_count += 1
        print(f"생성 {created_count}: {customer_name} - {company_name} - {area} - {money}")

    print(f"\n총 {created_count}개의 ClientReport 테스트 데이터가 생성되었습니다!")
    return created_count

if __name__ == "__main__":
    try:
        count = create_test_clientreports()
        print(f"✅ 성공적으로 {count}개의 데이터를 생성했습니다.")
    except Exception as e:
        print(f"❌ 오류 발생: {e}")