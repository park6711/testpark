from django.core.management.base import BaseCommand
from evaluation.models import Complain
from company.models import Company
import random

class Command(BaseCommand):
    help = 'Complain 레코드의 noCompany 필드를 유효한 Company ID로 업데이트'

    def handle(self, *args, **options):
        # 활성 상태의 Company 목록 가져오기 (nCondition이 1 또는 2인 회사)
        active_companies = Company.objects.filter(nCondition__in=[1, 2]).values_list('no', flat=True)

        if not active_companies:
            self.stdout.write(self.style.ERROR('활성 상태의 Company가 없습니다.'))
            return

        # Company ID 리스트로 변환
        company_ids = list(active_companies)
        self.stdout.write(f'사용 가능한 Company ID: {company_ids[:10]}...(총 {len(company_ids)}개)')

        # 모든 Complain 레코드 가져오기
        complains = Complain.objects.all()
        total = complains.count()

        if total == 0:
            self.stdout.write(self.style.WARNING('Complain 레코드가 없습니다.'))
            return

        self.stdout.write(f'\n총 {total}개의 Complain 레코드를 업데이트합니다...')

        updated = 0
        for complain in complains:
            # 랜덤하게 Company ID 선택
            complain.noCompany = random.choice(company_ids)
            complain.save()
            updated += 1

            if updated % 10 == 0:
                self.stdout.write(f'  {updated}/{total} 완료...')

        self.stdout.write(self.style.SUCCESS(f'\n✅ {updated}개의 Complain 레코드가 성공적으로 업데이트되었습니다.'))

        # 업데이트 결과 샘플 출력
        sample_complains = Complain.objects.all()[:5]
        self.stdout.write('\n업데이트된 샘플 데이터:')
        for complain in sample_complains:
            company = Company.objects.get(no=complain.noCompany)
            self.stdout.write(f'  - Complain #{complain.no}: Company #{company.no} ({company.sCompany})')