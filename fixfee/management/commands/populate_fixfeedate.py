from django.core.management.base import BaseCommand
from django.db import transaction
from datetime import date
from fixfee.models import FixFeeDate


class Command(BaseCommand):
    help = 'FixFeeDate 테이블에 2025년 9월부터 2036년 12월까지 매월 1일 데이터를 입력합니다.'

    def handle(self, *args, **kwargs):
        # 데이터 정의 (2025년 9월부터 2036년 12월까지)
        fee_dates = []

        # 2025년 9월부터 12월
        for month in range(9, 13):
            fee_dates.append(date(2025, month, 1))

        # 2026년부터 2036년까지 각 월
        for year in range(2026, 2037):
            for month in range(1, 13):
                fee_dates.append(date(year, month, 1))

        # 트랜잭션으로 묶어서 처리
        with transaction.atomic():
            # 기존 데이터 삭제
            existing_count = FixFeeDate.objects.count()
            if existing_count > 0:
                self.stdout.write(self.style.WARNING(f'기존 데이터 {existing_count}건을 삭제합니다...'))
                FixFeeDate.objects.all().delete()

            # 새 데이터 입력
            success_count = 0
            error_count = 0

            for idx, fee_date in enumerate(fee_dates, 1):
                try:
                    FixFeeDate.objects.create(
                        no=idx,
                        date=fee_date
                    )
                    success_count += 1

                    # 10개마다 진행상황 출력
                    if idx % 10 == 0:
                        self.stdout.write(f'진행중... {idx}건 입력')

                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'오류 발생 (ID: {idx}, 날짜: {fee_date}): {str(e)}'))
                    error_count += 1

        # 결과 출력
        self.stdout.write(self.style.SUCCESS(f'\n===== 작업 완료 ====='))
        self.stdout.write(self.style.SUCCESS(f'✓ 성공: {success_count}건'))
        if error_count > 0:
            self.stdout.write(self.style.ERROR(f'✗ 실패: {error_count}건'))

        # 최종 확인
        final_count = FixFeeDate.objects.count()
        self.stdout.write(self.style.SUCCESS(f'\n최종 FixFeeDate 데이터 수: {final_count}건'))

        # 처음과 마지막 데이터 확인
        if final_count > 0:
            first = FixFeeDate.objects.order_by('date').first()
            last = FixFeeDate.objects.order_by('date').last()
            self.stdout.write(self.style.SUCCESS(f'첫 번째 날짜: {first.date} (ID: {first.no})'))
            self.stdout.write(self.style.SUCCESS(f'마지막 날짜: {last.date} (ID: {last.no})'))