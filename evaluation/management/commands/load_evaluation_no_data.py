from django.core.management.base import BaseCommand
from django.db import transaction
from evaluation.models import EvaluationNo
from datetime import date, time


class Command(BaseCommand):
    help = 'Load EvaluationNo data from 2015 to 2060'

    def handle(self, *args, **kwargs):
        # 데이터 정의
        evaluation_data = [
            (1, date(2015, 5, 1), date(2015, 6, 30), date(2015, 7, 10), 0.00, 0.00, time(14, 0), time(14, 0)),
            (2, date(2015, 7, 1), date(2015, 8, 31), date(2015, 9, 10), 0.00, 0.00, time(14, 0), time(14, 0)),
            (3, date(2015, 9, 1), date(2015, 10, 31), date(2015, 11, 10), 0.00, 0.00, time(14, 0), time(14, 0)),
            (4, date(2015, 11, 1), date(2015, 12, 31), date(2016, 1, 10), 0.00, 0.00, time(14, 0), time(14, 0)),
            (5, date(2016, 1, 1), date(2016, 2, 29), date(2016, 3, 10), 6.62, 0.00, time(14, 0), time(14, 0)),
            (6, date(2016, 3, 1), date(2016, 4, 30), date(2016, 5, 10), 8.17, 0.00, time(14, 0), time(14, 0)),
            (7, date(2016, 5, 1), date(2016, 6, 30), date(2016, 7, 10), 9.18, 0.00, time(14, 0), time(14, 0)),
            (8, date(2016, 7, 1), date(2016, 8, 31), date(2016, 9, 10), 8.64, 0.00, time(14, 0), time(14, 0)),
            (9, date(2016, 9, 1), date(2016, 10, 31), date(2016, 11, 10), 9.02, 0.00, time(14, 0), time(14, 0)),
            (10, date(2016, 11, 1), date(2016, 12, 31), date(2017, 1, 10), 10.88, 0.00, time(14, 0), time(14, 0)),
            (11, date(2017, 1, 1), date(2017, 2, 28), date(2017, 3, 10), 9.65, 0.00, time(14, 0), time(14, 0)),
            (12, date(2017, 3, 1), date(2017, 4, 30), date(2017, 5, 10), 9.35, 0.00, time(14, 0), time(14, 0)),
            (13, date(2017, 5, 1), date(2017, 6, 30), date(2017, 7, 10), 6.38, 0.00, time(14, 0), time(14, 0)),
            (14, date(2017, 7, 1), date(2017, 8, 31), date(2017, 9, 10), 8.05, 0.00, time(14, 0), time(14, 0)),
            (15, date(2017, 9, 1), date(2017, 10, 31), date(2017, 11, 10), 9.95, 0.00, time(14, 0), time(14, 0)),
            (16, date(2017, 11, 1), date(2017, 12, 31), date(2018, 1, 10), 9.28, 0.00, time(14, 0), time(14, 0)),
            (17, date(2018, 1, 1), date(2018, 2, 28), date(2018, 3, 10), 6.73, 0.00, time(14, 0), time(14, 0)),
            (18, date(2018, 3, 1), date(2018, 4, 30), date(2018, 5, 10), 8.57, 0.00, time(14, 0), time(14, 0)),
            (19, date(2018, 5, 1), date(2018, 6, 30), date(2018, 7, 10), 10.82, 0.00, time(14, 0), time(14, 0)),
            (20, date(2018, 7, 1), date(2018, 8, 31), date(2018, 9, 10), 8.71, 0.00, time(14, 0), time(14, 0)),
            (21, date(2018, 9, 1), date(2018, 10, 31), date(2018, 11, 10), 9.10, 0.00, time(14, 0), time(14, 0)),
            (22, date(2018, 11, 1), date(2018, 12, 31), date(2019, 1, 10), 10.91, 0.00, time(14, 0), time(14, 0)),
            (23, date(2019, 1, 1), date(2019, 2, 28), date(2019, 3, 10), 10.13, 0.00, time(14, 0), time(14, 0)),
            (24, date(2019, 3, 1), date(2019, 4, 30), date(2019, 5, 10), 11.22, 0.00, time(14, 0), time(14, 0)),
            (25, date(2019, 5, 1), date(2019, 6, 30), date(2019, 7, 10), 11.00, 0.00, time(14, 0), time(14, 0)),
            (26, date(2019, 7, 1), date(2019, 8, 31), date(2019, 9, 10), 10.08, 0.00, time(14, 0), time(14, 0)),
            (27, date(2019, 9, 1), date(2019, 10, 31), date(2019, 11, 10), 8.72, 0.00, time(14, 0), time(14, 0)),
            (28, date(2019, 11, 1), date(2019, 12, 31), date(2020, 1, 10), 9.26, 0.00, time(14, 0), time(14, 0)),
            (29, date(2020, 1, 1), date(2020, 2, 29), date(2020, 3, 10), 8.47, 0.00, time(14, 0), time(14, 0)),
            (30, date(2020, 3, 1), date(2020, 4, 30), date(2020, 5, 10), 10.10, 0.00, time(14, 0), time(14, 0)),
            (31, date(2020, 5, 1), date(2020, 6, 30), date(2020, 7, 10), 10.56, 0.00, time(14, 0), time(14, 0)),
            (32, date(2020, 7, 1), date(2020, 8, 31), date(2020, 9, 10), 7.87, 0.00, time(14, 0), time(14, 0)),
            (33, date(2020, 9, 1), date(2020, 10, 31), date(2020, 11, 10), 9.23, 0.00, time(14, 0), time(14, 0)),
            (34, date(2020, 11, 1), date(2020, 12, 31), date(2021, 1, 10), 8.09, 15.24, time(14, 0), time(14, 0)),
            (35, date(2021, 1, 1), date(2021, 2, 28), date(2021, 3, 10), 7.50, 17.24, time(14, 0), time(14, 0)),
            (36, date(2021, 3, 1), date(2021, 4, 30), date(2021, 5, 10), 9.11, 19.00, time(14, 0), time(14, 0)),
            (37, date(2021, 5, 1), date(2021, 6, 30), date(2021, 7, 10), 8.48, 20.23, time(14, 0), time(14, 0)),
            (38, date(2021, 7, 1), date(2021, 8, 31), date(2021, 9, 10), 7.67, 16.63, time(14, 0), time(14, 0)),
            (39, date(2021, 9, 1), date(2021, 10, 31), date(2021, 11, 10), 9.07, 20.25, time(14, 0), time(14, 0)),
            (40, date(2021, 11, 1), date(2021, 12, 31), date(2022, 1, 10), 10.29, 19.43, time(14, 0), time(14, 0)),
            (41, date(2022, 1, 1), date(2022, 2, 28), date(2022, 3, 10), 9.49, 24.02, time(14, 0), time(14, 0)),
            (42, date(2022, 3, 1), date(2022, 4, 30), date(2022, 5, 10), 9.49, 19.15, time(14, 0), time(14, 0)),
            (43, date(2022, 5, 1), date(2022, 6, 30), date(2022, 7, 10), 8.97, 19.64, time(14, 0), time(14, 0)),
            (44, date(2022, 7, 1), date(2022, 8, 31), date(2022, 9, 10), 11.12, 25.00, time(14, 0), time(14, 0)),
            (45, date(2022, 9, 1), date(2022, 10, 31), date(2022, 11, 10), 12.12, 29.50, time(14, 0), time(14, 0)),
            (46, date(2022, 11, 1), date(2022, 12, 31), date(2023, 1, 10), 10.02, 29.64, time(14, 0), time(14, 0)),
            (47, date(2023, 1, 1), date(2023, 2, 28), date(2023, 3, 10), 8.49, 21.64, time(14, 0), time(14, 0)),
            (48, date(2023, 3, 1), date(2023, 4, 30), date(2023, 5, 10), 9.74, 20.74, time(14, 0), time(14, 0)),
            (49, date(2023, 5, 1), date(2023, 6, 30), date(2023, 7, 10), 10.77, 21.13, time(14, 0), time(14, 0)),
            (50, date(2023, 7, 1), date(2023, 8, 31), date(2023, 9, 10), 11.54, 22.84, time(14, 0), time(14, 0)),
            (51, date(2023, 9, 1), date(2023, 10, 31), date(2023, 11, 10), 12.11, 23.21, time(14, 0), time(14, 0)),
            (52, date(2023, 11, 1), date(2023, 12, 31), date(2024, 1, 10), 13.40, 25.54, time(14, 0), time(14, 0)),
            (53, date(2024, 1, 1), date(2024, 2, 29), date(2024, 3, 10), 10.26, 21.67, time(14, 0), time(14, 0)),
            (54, date(2024, 3, 1), date(2024, 4, 30), date(2024, 5, 10), 12.87, 23.21, time(14, 0), time(14, 0)),
            (55, date(2024, 5, 1), date(2024, 6, 30), date(2024, 7, 10), 10.06, 18.56, time(14, 0), time(14, 0)),
            (56, date(2024, 7, 1), date(2024, 8, 31), date(2024, 9, 10), 10.62, 19.17, time(14, 0), time(14, 0)),
            (57, date(2024, 9, 1), date(2024, 10, 31), date(2024, 11, 10), 11.38, 22.43, time(14, 0), time(14, 0)),
            (58, date(2024, 11, 1), date(2024, 12, 31), date(2025, 1, 10), 13.24, 23.30, time(14, 0), time(14, 0)),
            (59, date(2025, 1, 1), date(2025, 2, 28), date(2025, 3, 10), 10.37, 23.76, time(14, 0), time(14, 0)),
            (60, date(2025, 3, 1), date(2025, 4, 30), date(2025, 5, 10), 10.05, 16.69, time(14, 0), time(14, 0)),
            (61, date(2025, 5, 1), date(2025, 6, 30), date(2025, 7, 10), 9.26, 17.41, time(14, 0), time(14, 0)),
            (62, date(2025, 7, 1), date(2025, 8, 31), date(2025, 9, 10), 10.41, 16.93, time(14, 0), time(14, 0)),
            (63, date(2025, 9, 1), date(2025, 10, 31), date(2025, 11, 10), 0.00, 0.00, time(14, 0), time(14, 0)),
            (64, date(2025, 11, 1), date(2025, 12, 31), date(2026, 1, 10), 0.00, 0.00, time(14, 0), time(14, 0)),
        ]

        # 2026년부터 2060년까지 생성
        for year in range(2026, 2060):
            periods = [
                (1, 2, 28 if year % 4 != 0 else 29, 3, 10),  # 1-2월
                (3, 4, 30, 5, 10),  # 3-4월
                (5, 6, 30, 7, 10),  # 5-6월
                (7, 8, 31, 9, 10),  # 7-8월
                (9, 10, 31, 11, 10),  # 9-10월
                (11, 12, 31, 1, 10)  # 11-12월 (다음해 1월 공지)
            ]

            for start_month, end_month, end_day, notice_month, notice_day in periods:
                no = len(evaluation_data) + 1
                start_date = date(year, start_month, 1)
                end_date = date(year, end_month, end_day)
                # 11-12월의 경우 다음해 1월이 공지일
                notice_year = year + 1 if start_month == 11 else year
                notice_date = date(notice_year, notice_month, notice_day)

                evaluation_data.append(
                    (no, start_date, end_date, notice_date, 0.00, 0.00, time(14, 0), time(14, 0))
                )

        # 2060년 1-2월 추가
        no = len(evaluation_data) + 1
        evaluation_data.append(
            (no, date(2060, 1, 1), date(2060, 2, 29), date(2060, 3, 10), 0.00, 0.00, time(14, 0), time(14, 0))
        )

        with transaction.atomic():
            # 기존 데이터 삭제
            old_count = EvaluationNo.objects.count()
            if old_count > 0:
                self.stdout.write(
                    self.style.WARNING(f"Deleting {old_count} existing EvaluationNo records...")
                )
                EvaluationNo.objects.all().delete()

            # 새 데이터 생성
            created_count = 0
            for (no, date_start, date_end, date_notice, avg_all, avg_excel,
                 time_excel, time_weak) in evaluation_data:

                EvaluationNo.objects.create(
                    no=no,
                    dateStart=date_start,
                    dateEnd=date_end,
                    dateNotice=date_notice,
                    fAverageAll=avg_all,
                    fAverageExcel=avg_excel,
                    timeExcel=time_excel,
                    timeWeak=time_weak
                )
                created_count += 1

                # 진행 상황 표시
                if created_count % 20 == 0:
                    self.stdout.write(f"Created {created_count} records...")

            self.stdout.write(
                self.style.SUCCESS(
                    f"\n✅ Successfully created {created_count} EvaluationNo records"
                )
            )

            # 처음 5개와 마지막 5개 확인
            first_records = EvaluationNo.objects.order_by('no')[:5]
            last_records = EvaluationNo.objects.order_by('-no')[:5]

            self.stdout.write("\n📅 First 5 evaluation rounds:")
            for eval_no in first_records:
                self.stdout.write(
                    f"  no={eval_no.no}: {eval_no.dateStart} ~ {eval_no.dateEnd} "
                    f"(공지: {eval_no.dateNotice}) - "
                    f"전체:{eval_no.fAverageAll}% / 우수:{eval_no.fAverageExcel}%"
                )

            self.stdout.write("\n📅 Last 5 evaluation rounds:")
            for eval_no in reversed(last_records):
                self.stdout.write(
                    f"  no={eval_no.no}: {eval_no.dateStart} ~ {eval_no.dateEnd} "
                    f"(공지: {eval_no.dateNotice}) - "
                    f"전체:{eval_no.fAverageAll}% / 우수:{eval_no.fAverageExcel}%"
                )

            total = EvaluationNo.objects.count()
            self.stdout.write(
                self.style.SUCCESS(
                    f"\n📊 Total EvaluationNo records in database: {total}"
                )
            )