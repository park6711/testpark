from django.core.management.base import BaseCommand
from django.db import transaction
from fixfee.models import FixFee, FixFeeDate
from company.models import Company
import random


class Command(BaseCommand):
    help = 'FixFee 테스트 데이터 생성 - 고정비토탈 업체 대상'

    def handle(self, *args, **options):
        # nType=1(고정비토탈) 업체 조회
        fixfee_companies = Company.objects.filter(nType=1)
        company_count = fixfee_companies.count()

        self.stdout.write(f'고정비토탈 업체 수: {company_count}개')

        if company_count == 0:
            self.stdout.write(self.style.WARNING('고정비토탈 업체가 없습니다.'))
            return

        # FixFeeDate 1, 2, 3번 조회
        fee_dates = {}
        for i in [1, 2, 3]:
            try:
                fee_dates[i] = FixFeeDate.objects.get(no=i)
            except FixFeeDate.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'FixFeeDate no={i}이 존재하지 않습니다.'))
                return

        created_count = 0
        updated_count = 0

        with transaction.atomic():
            # 각 고정비토탈 업체에 대해 3개의 FixFee 레코드 생성
            for company in fixfee_companies:
                for fee_date_no in [1, 2, 3]:
                    # nType 결정
                    if fee_date_no == 1:
                        n_type = 0  # 계좌이체
                    elif fee_date_no == 2:
                        n_type = random.choice([1, 2])  # 우수업체 또는 최우수업체
                    else:  # fee_date_no == 3
                        n_type = 3  # 기타

                    # 고정비 금액 설정 (기본값 165000원, 우수/최우수 업체는 할인 적용)
                    if n_type == 0:
                        n_fix_fee = 165000
                    elif n_type == 1:
                        n_fix_fee = 132000  # 우수업체 20% 할인
                    elif n_type == 2:
                        n_fix_fee = 99000   # 최우수업체 40% 할인
                    else:
                        n_fix_fee = 165000

                    # dateDeposit 설정 (완납일자)
                    date_deposit = fee_dates[fee_date_no].date

                    # FixFee 생성 또는 업데이트
                    fee, created = FixFee.objects.update_or_create(
                        noCompany=company.no,
                        noFixFeeDate=fee_date_no,
                        defaults={
                            'dateDeposit': date_deposit,
                            'nFixFee': n_fix_fee,
                            'nType': n_type,
                            'sMemo': f'테스트 데이터 - {company.sName2 or company.sName1}'
                        }
                    )

                    if created:
                        created_count += 1
                        self.stdout.write(
                            f'생성: 업체={company.no}({company.sName2 or company.sName1}), '
                            f'납부기준일={fee_date_no}, 납부방식={n_type}, '
                            f'금액={n_fix_fee:,}원'
                        )
                    else:
                        updated_count += 1
                        self.stdout.write(
                            f'업데이트: 업체={company.no}({company.sName2 or company.sName1}), '
                            f'납부기준일={fee_date_no}'
                        )

        # 요약 통계
        total_fees = FixFee.objects.all()
        type_stats = {}
        for i in range(4):
            type_count = total_fees.filter(nType=i).count()
            type_names = ['계좌이체', '우수업체', '최우수업체', '기타']
            type_stats[type_names[i]] = type_count

        self.stdout.write(
            self.style.SUCCESS(
                f'\n작업 완료!\n'
                f'- 생성: {created_count}건\n'
                f'- 업데이트: {updated_count}건\n'
                f'- 전체 FixFee 레코드 수: {total_fees.count()}건\n'
                f'\n납부방식별 통계:\n'
                f'  - 계좌이체: {type_stats.get("계좌이체", 0)}건\n'
                f'  - 우수업체: {type_stats.get("우수업체", 0)}건\n'
                f'  - 최우수업체: {type_stats.get("최우수업체", 0)}건\n'
                f'  - 기타: {type_stats.get("기타", 0)}건'
            )
        )