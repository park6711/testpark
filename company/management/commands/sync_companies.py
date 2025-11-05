"""
Google Sheets에서 Company 데이터를 동기화하는 Django Management Command
"""
from django.core.management.base import BaseCommand
from company.google_sheets_sync import CompanySheetsSync
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Google Sheets에서 Company 데이터를 동기화합니다'

    def add_arguments(self, parser):
        parser.add_argument(
            '--update',
            action='store_true',
            help='기존 레코드도 업데이트합니다',
        )

    def handle(self, *args, **options):
        update_existing = options.get('update', False)

        self.stdout.write(self.style.NOTICE('Company 동기화 시작...'))

        try:
            sync_service = CompanySheetsSync()
            result = sync_service.sync_data(update_existing=update_existing)

            self.stdout.write(self.style.SUCCESS('\n동기화 완료!'))
            self.stdout.write(f"  - 생성: {result['created']}개")
            self.stdout.write(f"  - 업데이트: {result['updated']}개")
            self.stdout.write(f"  - 스킵: {result['skipped']}개")
            self.stdout.write(f"  - 에러: {result['errors']}개")
            self.stdout.write(f"  - 전체: {result['total']}개")

            if result['errors'] > 0:
                self.stdout.write(self.style.WARNING(f"\n⚠️  {result['errors']}개의 에러가 발생했습니다. 로그를 확인하세요."))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n동기화 실패: {str(e)}'))
            logger.error(f"Company 동기화 실패: {str(e)}", exc_info=True)
            raise
