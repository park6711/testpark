"""
업체 삭제 시 포인트 데이터 보존 테스트
Usage: python manage.py test_company_deletion
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from company.models import Company
from point.models import Point


class Command(BaseCommand):
    help = '업체 삭제 시 포인트 데이터가 보존되는지 테스트합니다'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('\n업체 삭제 시 포인트 데이터 보존 테스트\n'))
        self.stdout.write('=' * 60)

        # 테스트용 업체 생성
        test_company = Company.objects.create(
            sName1='테스트업체',
            sName2='TEST COMPANY',
            sTel='010-1234-5678'
        )
        self.stdout.write(f'\n✅ 테스트 업체 생성: {test_company.sName2} (ID: {test_company.no})')

        # 테스트용 포인트 데이터 생성
        point1 = Point.objects.create(
            noCompany=test_company,
            nType=3,  # 페이백 적립
            nPrePoint=0,
            nUsePoint=10000,
            nRemainPoint=10000,
            sWorker='테스트',
            sMemo='테스트 포인트 1'
        )
        self.stdout.write(f'✅ 포인트 1 생성: ID={point1.no}, 잔액={point1.nRemainPoint:,}')

        point2 = Point.objects.create(
            noCompany=test_company,
            nType=1,  # 취소환불
            nPrePoint=10000,
            nUsePoint=-3000,
            nRemainPoint=7000,
            sWorker='테스트',
            sMemo='테스트 포인트 2'
        )
        self.stdout.write(f'✅ 포인트 2 생성: ID={point2.no}, 잔액={point2.nRemainPoint:,}')

        # 삭제 전 상태 확인
        self.stdout.write(f'\n삭제 전 포인트 상태:')
        self.stdout.write(f'  - Point {point1.no}: noCompany={point1.noCompany_id}')
        self.stdout.write(f'  - Point {point2.no}: noCompany={point2.noCompany_id}')

        # 업체 삭제
        company_id = test_company.no
        company_name = test_company.sName2
        test_company.delete()
        self.stdout.write(f'\n🗑️  업체 삭제: {company_name} (ID: {company_id})')

        # 삭제 후 포인트 데이터 확인
        point1.refresh_from_db()
        point2.refresh_from_db()

        self.stdout.write(f'\n삭제 후 포인트 상태:')
        self.stdout.write(f'  - Point {point1.no}: noCompany={point1.noCompany_id} (NULL이 되어야 함)')
        self.stdout.write(f'  - Point {point2.no}: noCompany={point2.noCompany_id} (NULL이 되어야 함)')

        if point1.noCompany is None and point2.noCompany is None:
            self.stdout.write(self.style.SUCCESS('\n✅ 테스트 성공: 업체 삭제 후 포인트 데이터가 보존되었습니다!'))
            self.stdout.write('   포인트의 noCompany가 NULL로 설정되어 데이터가 유지됩니다.')
        else:
            self.stdout.write(self.style.ERROR('\n❌ 테스트 실패: 예상대로 동작하지 않았습니다.'))

        # 테스트 데이터 정리
        point1.delete()
        point2.delete()
        self.stdout.write('\n🧹 테스트 데이터 정리 완료')