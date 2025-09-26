from django.core.management.base import BaseCommand
from django.db import transaction
from fixfee.models import FixFeeDate, FixFee
from datetime import date


class Command(BaseCommand):
    help = 'Replace FixFeeDate data with dates from 2025-09 to 2060-01'

    def handle(self, *args, **kwargs):
        # 데이터 정의 (2025년 9월부터 2060년 1월까지)
        dates_data = []

        # 2025년 (9월부터 12월)
        for month in range(9, 13):
            dates_data.append((len(dates_data) + 1, date(2025, month, 1)))

        # 2026년부터 2059년까지 (각 년도 12개월)
        for year in range(2026, 2060):
            for month in range(1, 13):
                dates_data.append((len(dates_data) + 1, date(year, month, 1)))

        # 2060년 1월
        dates_data.append((len(dates_data) + 1, date(2060, 1, 1)))

        with transaction.atomic():
            # 기존 FixFee 데이터가 있는지 확인
            has_fixfee_data = FixFee.objects.exists()

            if has_fixfee_data:
                self.stdout.write(
                    self.style.WARNING(
                        "⚠️  Warning: FixFee records exist. Deleting them to avoid foreign key issues..."
                    )
                )
                # FixFee 데이터 삭제
                deleted_count = FixFee.objects.all().delete()[0]
                self.stdout.write(
                    self.style.WARNING(f"Deleted {deleted_count} FixFee records")
                )

            # 기존 FixFeeDate 데이터 삭제
            old_count = FixFeeDate.objects.count()
            FixFeeDate.objects.all().delete()
            self.stdout.write(
                self.style.WARNING(f"Deleted {old_count} old FixFeeDate records")
            )

            # 새 데이터 생성
            created_count = 0
            for no, date_value in dates_data:
                FixFeeDate.objects.create(
                    no=no,
                    date=date_value
                )
                created_count += 1

                # 진행 상황 표시 (10개마다)
                if created_count % 10 == 0:
                    self.stdout.write(f"Created {created_count} records...")

            self.stdout.write(
                self.style.SUCCESS(
                    f"\n✅ Successfully created {created_count} FixFeeDate records"
                )
            )

            # 처음 5개와 마지막 5개 확인
            first_dates = FixFeeDate.objects.order_by('no')[:5]
            last_dates = FixFeeDate.objects.order_by('-no')[:5]

            self.stdout.write("\n📅 First 5 dates:")
            for fd in first_dates:
                self.stdout.write(
                    f"  no={fd.no}: {fd.date.strftime('%Y년 %-m월 %-d일')}"
                )

            self.stdout.write("\n📅 Last 5 dates:")
            for fd in reversed(last_dates):
                self.stdout.write(
                    f"  no={fd.no}: {fd.date.strftime('%Y년 %-m월 %-d일')}"
                )

            total = FixFeeDate.objects.count()
            self.stdout.write(
                self.style.SUCCESS(
                    f"\n📊 Total FixFeeDate records in database: {total}"
                )
            )