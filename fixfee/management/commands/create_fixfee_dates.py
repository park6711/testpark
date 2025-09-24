from django.core.management.base import BaseCommand
from django.db import transaction
from fixfee.models import FixFeeDate
from datetime import date


class Command(BaseCommand):
    help = 'FixFeeDate 초기 데이터 생성 (2025년 9월 ~ 2036년 12월)'

    def handle(self, *args, **options):
        # 데이터 정의 (25년 = 2025년)
        fee_dates_data = [
            (1, date(2025, 9, 1)),
            (2, date(2025, 10, 1)),
            (3, date(2025, 11, 1)),
            (4, date(2025, 12, 1)),
            (5, date(2026, 1, 1)),
            (6, date(2026, 2, 1)),
            (7, date(2026, 3, 1)),
            (8, date(2026, 4, 1)),
            (9, date(2026, 5, 1)),
            (10, date(2026, 6, 1)),
            (11, date(2026, 7, 1)),
            (12, date(2026, 8, 1)),
            (13, date(2026, 9, 1)),
            (14, date(2026, 10, 1)),
            (15, date(2026, 11, 1)),
            (16, date(2026, 12, 1)),
            (17, date(2027, 1, 1)),
            (18, date(2027, 2, 1)),
            (19, date(2027, 3, 1)),
            (20, date(2027, 4, 1)),
            (21, date(2027, 5, 1)),
            (22, date(2027, 6, 1)),
            (23, date(2027, 7, 1)),
            (24, date(2027, 8, 1)),
            (25, date(2027, 9, 1)),
            (26, date(2027, 10, 1)),
            (27, date(2027, 11, 1)),
            (28, date(2027, 12, 1)),
            (29, date(2028, 1, 1)),
            (30, date(2028, 2, 1)),
            (31, date(2028, 3, 1)),
            (32, date(2028, 4, 1)),
            (33, date(2028, 5, 1)),
            (34, date(2028, 6, 1)),
            (35, date(2028, 7, 1)),
            (36, date(2028, 8, 1)),
            (37, date(2028, 9, 1)),
            (38, date(2028, 10, 1)),
            (39, date(2028, 11, 1)),
            (40, date(2028, 12, 1)),
            (41, date(2029, 1, 1)),
            (42, date(2029, 2, 1)),
            (43, date(2029, 3, 1)),
            (44, date(2029, 4, 1)),
            (45, date(2029, 5, 1)),
            (46, date(2029, 6, 1)),
            (47, date(2029, 7, 1)),
            (48, date(2029, 8, 1)),
            (49, date(2029, 9, 1)),
            (50, date(2029, 10, 1)),
            (51, date(2029, 11, 1)),
            (52, date(2029, 12, 1)),
            (53, date(2030, 1, 1)),
            (54, date(2030, 2, 1)),
            (55, date(2030, 3, 1)),
            (56, date(2030, 4, 1)),
            (57, date(2030, 5, 1)),
            (58, date(2030, 6, 1)),
            (59, date(2030, 7, 1)),
            (60, date(2030, 8, 1)),
            (61, date(2030, 9, 1)),
            (62, date(2030, 10, 1)),
            (63, date(2030, 11, 1)),
            (64, date(2030, 12, 1)),
            (65, date(2031, 1, 1)),
            (66, date(2031, 2, 1)),
            (67, date(2031, 3, 1)),
            (68, date(2031, 4, 1)),
            (69, date(2031, 5, 1)),
            (70, date(2031, 6, 1)),
            (71, date(2031, 7, 1)),
            (72, date(2031, 8, 1)),
            (73, date(2031, 9, 1)),
            (74, date(2031, 10, 1)),
            (75, date(2031, 11, 1)),
            (76, date(2031, 12, 1)),
            (77, date(2032, 1, 1)),
            (78, date(2032, 2, 1)),
            (79, date(2032, 3, 1)),
            (80, date(2032, 4, 1)),
            (81, date(2032, 5, 1)),
            (82, date(2032, 6, 1)),
            (83, date(2032, 7, 1)),
            (84, date(2032, 8, 1)),
            (85, date(2032, 9, 1)),
            (86, date(2032, 10, 1)),
            (87, date(2032, 11, 1)),
            (88, date(2032, 12, 1)),
            (89, date(2033, 1, 1)),
            (90, date(2033, 2, 1)),
            (91, date(2033, 3, 1)),
            (92, date(2033, 4, 1)),
            (93, date(2033, 5, 1)),
            (94, date(2033, 6, 1)),
            (95, date(2033, 7, 1)),
            (96, date(2033, 8, 1)),
            (97, date(2033, 9, 1)),
            (98, date(2033, 10, 1)),
            (99, date(2033, 11, 1)),
            (100, date(2033, 12, 1)),
            (101, date(2034, 1, 1)),
            (102, date(2034, 2, 1)),
            (103, date(2034, 3, 1)),
            (104, date(2034, 4, 1)),
            (105, date(2034, 5, 1)),
            (106, date(2034, 6, 1)),
            (107, date(2034, 7, 1)),
            (108, date(2034, 8, 1)),
            (109, date(2034, 9, 1)),
            (110, date(2034, 10, 1)),
            (111, date(2034, 11, 1)),
            (112, date(2034, 12, 1)),
            (113, date(2035, 1, 1)),
            (114, date(2035, 2, 1)),
            (115, date(2035, 3, 1)),
            (116, date(2035, 4, 1)),
            (117, date(2035, 5, 1)),
            (118, date(2035, 6, 1)),
            (119, date(2035, 7, 1)),
            (120, date(2035, 8, 1)),
            (121, date(2035, 9, 1)),
            (122, date(2035, 10, 1)),
            (123, date(2035, 11, 1)),
            (124, date(2035, 12, 1)),
            (125, date(2036, 1, 1)),
            (126, date(2036, 2, 1)),
            (127, date(2036, 3, 1)),
            (128, date(2036, 4, 1)),
            (129, date(2036, 5, 1)),
            (130, date(2036, 6, 1)),
            (131, date(2036, 7, 1)),
            (132, date(2036, 8, 1)),
            (133, date(2036, 9, 1)),
            (134, date(2036, 10, 1)),
            (135, date(2036, 11, 1)),
            (136, date(2036, 12, 1)),
        ]

        created_count = 0
        updated_count = 0

        with transaction.atomic():
            for no_val, date_val in fee_dates_data:
                # no 필드를 직접 지정하여 생성/업데이트
                try:
                    # 기존 레코드 확인
                    fee_date = FixFeeDate.objects.filter(no=no_val).first()

                    if fee_date:
                        # 업데이트
                        fee_date.date = date_val
                        fee_date.save()
                        updated_count += 1
                        self.stdout.write(f'업데이트: no={no_val}, date={date_val}')
                    else:
                        # 새로 생성
                        fee_date = FixFeeDate(no=no_val, date=date_val)
                        fee_date.save(force_insert=True)
                        created_count += 1
                        self.stdout.write(f'생성: no={no_val}, date={date_val}')

                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'오류 발생 (no={no_val}): {str(e)}')
                    )

        self.stdout.write(
            self.style.SUCCESS(
                f'\n작업 완료!\n'
                f'- 생성: {created_count}건\n'
                f'- 업데이트: {updated_count}건\n'
                f'- 전체 레코드 수: {FixFeeDate.objects.count()}건'
            )
        )