from django.core.management.base import BaseCommand
from company.models import Company
import random


class Command(BaseCommand):
    help = 'Create 40 test Company records with nType=1 (고정비토탈)'

    def handle(self, *args, **kwargs):
        # 지역 리스트
        regions = ['서울', '부산', '대구', '인천', '광주', '대전', '울산', '세종',
                   '경기', '강원', '충북', '충남', '전북', '전남', '경북', '경남', '제주']

        # 활동상태 리스트 (0:준비중, 1:정상, 2:일시정지)
        conditions = [0, 1, 1, 1, 1, 2]  # 정상이 많도록

        # 월고정비 금액 리스트
        fix_fees = [0, 330000, 440000, 550000, 660000, 770000]

        created_count = 0

        for i in range(1, 41):
            region = random.choice(regions)
            company_name = f"{region}테스트{i}호"

            # 중복 체크
            if Company.objects.filter(sName2=company_name).exists():
                self.stdout.write(f"Company '{company_name}' already exists, skipping...")
                continue

            company = Company.objects.create(
                sName1=f"테스트업체{i}",  # 열린업체명1
                sName2=company_name,  # 열린업체명2
                sCompanyName=f"{company_name} 주식회사",  # 업체명
                nType=1,  # 고정비토탈
                nCondition=random.choice(conditions),  # 활동상태
                nFixFee=random.choice(fix_fees),  # 월고정비
                sAddress=f"{region}시 테스트구 테스트로 {i}",  # 주소
                sCeoName=f"대표자{i}",  # 대표자명
                sCeoPhone=f"010-{1000+i:04d}-{5000+i:04d}",  # 대표자 연락처
                sCeoMail=f"ceo{i}@example.com",  # 대표자 이메일
                sSaleName=f"영업담당{i}",  # 영업담당자명
                sSalePhone=f"010-{2000+i:04d}-{5000+i:04d}",  # 영업담당자 연락처
                sSaleMail=f"sales{i}@example.com",  # 영업담당자 이메일
                sMemo=f"테스트 업체 {i} - 자동 생성됨",  # 메모
                nJoinFee=0,  # 가입비
                nDeposit=0,  # 보증금
            )

            created_count += 1
            self.stdout.write(
                self.style.SUCCESS(
                    f"Created: {company.sName2} (상태: {company.get_nCondition_display()}, "
                    f"월고정비: {company.nFixFee:,}원)"
                )
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"\n✅ Successfully created {created_count} test companies with nType=1 (고정비토탈)"
            )
        )

        # 전체 통계 출력
        total = Company.objects.filter(nType=1).count()
        self.stdout.write(
            self.style.SUCCESS(
                f"📊 Total 고정비토탈 companies in database: {total}"
            )
        )