"""
업체별 포인트 잔액 확인 커맨드
Usage: python manage.py check_company_points
"""
from django.core.management.base import BaseCommand
from django.db.models import Count, Sum
from company.models import Company
from point.models import Point


class Command(BaseCommand):
    help = '업체별 포인트 잔액 및 내역을 확인합니다'

    def add_arguments(self, parser):
        parser.add_argument(
            '--company-id',
            type=int,
            help='특정 업체의 포인트만 확인 (업체 ID)',
        )
        parser.add_argument(
            '--non-zero',
            action='store_true',
            help='잔액이 0이 아닌 업체만 표시',
        )

    def handle(self, *args, **options):
        company_id = options.get('company_id')
        non_zero_only = options.get('non_zero')

        if company_id:
            # 특정 업체 확인
            try:
                company = Company.objects.get(no=company_id)
                self.check_single_company(company)
            except Company.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'업체 ID {company_id}를 찾을 수 없습니다.'))
        else:
            # 전체 업체 확인
            self.check_all_companies(non_zero_only)

    def check_single_company(self, company):
        """특정 업체의 포인트 상세 확인"""
        points = Point.objects.filter(noCompany=company).order_by('-time', '-no')

        if not points.exists():
            self.stdout.write(f"\n{company.sName2} ({company.sName1}): 포인트 내역 없음")
            return

        last_point = points.first()
        total_count = points.count()

        self.stdout.write(self.style.SUCCESS(f"\n{'='*60}"))
        self.stdout.write(self.style.SUCCESS(f"{company.sName2} ({company.sName1})"))
        self.stdout.write(self.style.SUCCESS(f"{'='*60}"))
        self.stdout.write(f"총 내역 수: {total_count}개")
        self.stdout.write(f"현재 잔액: {last_point.nRemainPoint:,} 포인트")

        if company.dateWithdraw:
            self.stdout.write(self.style.WARNING(f"⚠️  탈퇴일: {company.dateWithdraw}"))

        # 최근 5개 내역 표시
        self.stdout.write(f"\n최근 5개 내역:")
        self.stdout.write(f"{'날짜':<20} {'구분':<15} {'적용':>10} {'잔액':>12}")
        self.stdout.write(f"{'-'*60}")

        for point in points[:5]:
            date_str = point.time.strftime('%Y-%m-%d %H:%M')
            type_str = point.get_nType_display()
            self.stdout.write(
                f"{date_str:<20} {type_str:<15} "
                f"{point.nUsePoint:>10,} {point.nRemainPoint:>12,}"
            )

    def check_all_companies(self, non_zero_only):
        """전체 업체의 포인트 잔액 확인"""
        # 포인트가 있는 업체들 조회
        companies_with_points = Company.objects.filter(
            point_records__isnull=False
        ).distinct().annotate(
            point_count=Count('point_records')
        )

        total_balance = 0
        companies_data = []

        for company in companies_with_points:
            last_point = Point.objects.filter(
                noCompany=company
            ).order_by('-time', '-no').first()

            if last_point:
                balance = last_point.nRemainPoint
                if non_zero_only and balance == 0:
                    continue

                companies_data.append({
                    'company': company,
                    'balance': balance,
                    'count': company.point_count,
                    'last_date': last_point.time
                })
                total_balance += balance

        # 정렬 (잔액 기준 내림차순)
        companies_data.sort(key=lambda x: abs(x['balance']), reverse=True)

        # 결과 출력
        self.stdout.write(self.style.SUCCESS(f"\n{'='*80}"))
        self.stdout.write(self.style.SUCCESS("업체별 포인트 잔액 현황"))
        self.stdout.write(self.style.SUCCESS(f"{'='*80}"))

        if not companies_data:
            self.stdout.write("포인트 내역이 있는 업체가 없습니다.")
            return

        self.stdout.write(
            f"{'업체명':<20} {'잔액':>15} {'내역수':>8} {'최종갱신':<20} {'상태':<10}"
        )
        self.stdout.write(f"{'-'*80}")

        for data in companies_data:
            company = data['company']
            status = '탈퇴' if company.dateWithdraw else '활성'
            status_style = self.style.WARNING if company.dateWithdraw else self.style.SUCCESS

            balance_str = f"{data['balance']:,}"
            if data['balance'] < 0:
                balance_str = self.style.ERROR(balance_str)
            elif data['balance'] > 0:
                balance_str = self.style.SUCCESS(balance_str)

            self.stdout.write(
                f"{company.sName2[:20]:<20} {balance_str:>15} "
                f"{data['count']:>8} {data['last_date'].strftime('%Y-%m-%d %H:%M'):<20} "
                f"{status_style(status):<10}"
            )

        self.stdout.write(f"{'-'*80}")
        self.stdout.write(f"총 업체 수: {len(companies_data)}개")
        self.stdout.write(f"전체 잔액 합계: {total_balance:,} 포인트")