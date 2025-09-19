import os
import django
import sys

# Django 설정
sys.path.append('/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testpark_project.settings')
django.setup()

from license.models import License
from company.models import Company

# 샘플 데이터 생성
license_data = [
    {
        'noCompany': 1,
        'sCompanyName': '삼성전자',
        'sCeoName': '이재용',
        'sLicenseNo': '123-45-67890',
        'sAccountMail': 'ceo@samsung.com',
        'sAccount': '110-123-456789',
    },
    {
        'noCompany': 2,
        'sCompanyName': 'LG전자',
        'sCeoName': '조주완',
        'sLicenseNo': '234-56-78901',
        'sAccountMail': 'ceo@lg.com',
        'sAccount': '220-234-567890',
    },
    {
        'noCompany': 3,
        'sCompanyName': '현대자동차',
        'sCeoName': '장재훈',
        'sLicenseNo': '345-67-89012',
        'sAccountMail': 'ceo@hyundai.com',
        'sAccount': '330-345-678901',
    },
    {
        'noCompany': 4,
        'sCompanyName': '네이버',
        'sCeoName': '최수연',
        'sLicenseNo': '456-78-90123',
        'sAccountMail': 'ceo@naver.com',
        'sAccount': '440-456-789012',
    },
    {
        'noCompany': 5,
        'sCompanyName': '카카오',
        'sCeoName': '홍은택',
        'sLicenseNo': '567-89-01234',
        'sAccountMail': 'ceo@kakao.com',
        'sAccount': '550-567-890123',
    },
    {
        'noCompany': 6,
        'sCompanyName': '신한은행',
        'sCeoName': '진옥동',
        'sLicenseNo': '678-90-12345',
        'sAccountMail': 'ceo@shinhan.com',
        'sAccount': '660-678-901234',
    },
    {
        'noCompany': 7,
        'sCompanyName': '하나은행',
        'sCeoName': '이승열',
        'sLicenseNo': '789-01-23456',
        'sAccountMail': 'ceo@hana.com',
        'sAccount': '770-789-012345',
    },
    {
        'noCompany': 8,
        'sCompanyName': '한국전력공사',
        'sCeoName': '김동철',
        'sLicenseNo': '890-12-34567',
        'sAccountMail': 'ceo@kepco.co.kr',
        'sAccount': '880-890-123456',
    },
    {
        'noCompany': 9,
        'sCompanyName': '포스코',
        'sCeoName': '정기섭',
        'sLicenseNo': '901-23-45678',
        'sAccountMail': 'ceo@posco.com',
        'sAccount': '990-901-234567',
    },
    {
        'noCompany': 10,
        'sCompanyName': 'SK텔레콤',
        'sCeoName': '유영상',
        'sLicenseNo': '012-34-56789',
        'sAccountMail': 'ceo@skt.com',
        'sAccount': '100-012-345678',
    },
    {
        'noCompany': 11,
        'sCompanyName': 'KT',
        'sCeoName': '김영섭',
        'sLicenseNo': '123-45-67891',
        'sAccountMail': 'ceo@kt.com',
        'sAccount': '110-123-456790',
    },
    {
        'noCompany': 12,
        'sCompanyName': 'LG유플러스',
        'sCeoName': '황현식',
        'sLicenseNo': '234-56-78902',
        'sAccountMail': 'ceo@lguplus.co.kr',
        'sAccount': '220-234-567801',
    },
    {
        'noCompany': 13,
        'sCompanyName': '삼성물산',
        'sCeoName': '오세철',
        'sLicenseNo': '345-67-89013',
        'sAccountMail': 'ceo@samsungcnt.com',
        'sAccount': '330-345-678912',
    },
    {
        'noCompany': 14,
        'sCompanyName': '롯데그룹',
        'sCeoName': '신동빈',
        'sLicenseNo': '456-78-90124',
        'sAccountMail': 'ceo@lotte.co.kr',
        'sAccount': '440-456-789023',
    },
    {
        'noCompany': 15,
        'sCompanyName': 'CJ제일제당',
        'sCeoName': '강신호',
        'sLicenseNo': '567-89-01235',
        'sAccountMail': 'ceo@cj.net',
        'sAccount': '550-567-890134',
    },
    {
        'noCompany': 16,
        'sCompanyName': '한화그룹',
        'sCeoName': '김승연',
        'sLicenseNo': '678-90-12346',
        'sAccountMail': 'ceo@hanwha.com',
        'sAccount': '660-678-901245',
    },
    {
        'noCompany': 17,
        'sCompanyName': '두산그룹',
        'sCeoName': '박정원',
        'sLicenseNo': '789-01-23457',
        'sAccountMail': 'ceo@doosan.com',
        'sAccount': '770-789-012356',
    },
    {
        'noCompany': 18,
        'sCompanyName': 'GS그룹',
        'sCeoName': '허태수',
        'sLicenseNo': '890-12-34568',
        'sAccountMail': 'ceo@gs.co.kr',
        'sAccount': '880-890-123467',
    },
    {
        'noCompany': 19,
        'sCompanyName': 'LS그룹',
        'sCeoName': '구자은',
        'sLicenseNo': '901-23-45679',
        'sAccountMail': 'ceo@ls.co.kr',
        'sAccount': '990-901-234578',
    },
    {
        'noCompany': 20,
        'sCompanyName': '효성그룹',
        'sCeoName': '조현준',
        'sLicenseNo': '012-34-56780',
        'sAccountMail': 'ceo@hyosung.com',
        'sAccount': '100-012-345689',
    },
    {
        'noCompany': 21,
        'sCompanyName': '대우건설',
        'sCeoName': '정원주',
        'sLicenseNo': '123-45-67892',
        'sAccountMail': 'ceo@daewooenc.com',
        'sAccount': '110-123-456791',
    },
    {
        'noCompany': 22,
        'sCompanyName': '현대건설',
        'sCeoName': '윤영준',
        'sLicenseNo': '234-56-78903',
        'sAccountMail': 'ceo@hdec.co.kr',
        'sAccount': '220-234-567802',
    },
    {
        'noCompany': 23,
        'sCompanyName': '대림산업',
        'sCeoName': '이해선',
        'sLicenseNo': '345-67-89014',
        'sAccountMail': 'ceo@daelim.co.kr',
        'sAccount': '330-345-678913',
    },
    {
        'noCompany': 24,
        'sCompanyName': '코오롱그룹',
        'sCeoName': '이웅열',
        'sLicenseNo': '456-78-90125',
        'sAccountMail': 'ceo@kolon.com',
        'sAccount': '440-456-789024',
    },
    {
        'noCompany': 25,
        'sCompanyName': '금호타이어',
        'sCeoName': '강호찬',
        'sLicenseNo': '567-89-01236',
        'sAccountMail': 'ceo@kumhotire.co.kr',
        'sAccount': '550-567-890135',
    },
    {
        'noCompany': 26,
        'sCompanyName': '넥슨',
        'sCeoName': '이정헌',
        'sLicenseNo': '678-90-12347',
        'sAccountMail': 'ceo@nexon.co.kr',
        'sAccount': '660-678-901246',
    },
    {
        'noCompany': 27,
        'sCompanyName': '엔씨소프트',
        'sCeoName': '김택진',
        'sLicenseNo': '789-01-23458',
        'sAccountMail': 'ceo@ncsoft.com',
        'sAccount': '770-789-012357',
    },
    {
        'noCompany': 28,
        'sCompanyName': '펄어비스',
        'sCeoName': '허진영',
        'sLicenseNo': '890-12-34569',
        'sAccountMail': 'ceo@pearlabyss.com',
        'sAccount': '880-890-123468',
    },
    {
        'noCompany': 29,
        'sCompanyName': '크래프톤',
        'sCeoName': '김창한',
        'sLicenseNo': '901-23-45680',
        'sAccountMail': 'ceo@krafton.com',
        'sAccount': '990-901-234579',
    },
    {
        'noCompany': 30,
        'sCompanyName': '쿠팡',
        'sCeoName': '김범석',
        'sLicenseNo': '012-34-56781',
        'sAccountMail': 'ceo@coupang.com',
        'sAccount': '100-012-345680',
    },
]

# 기존 데이터 삭제 (선택사항)
print("기존 License 데이터 삭제 중...")
License.objects.all().delete()

# 새 데이터 생성
print("새로운 License 데이터 생성 중...")
for i, data in enumerate(license_data, 1):
    license_obj = License.objects.create(**data)
    print(f"{i}. {license_obj.sCompanyName} ({license_obj.sCeoName}) 생성완료")

print(f"\n총 {len(license_data)}개의 License 데이터가 생성되었습니다.")