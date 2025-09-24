# 구글 스프레드시트 동기화 커맨드
from django.core.management.base import BaseCommand
from django.utils import timezone
from order.google_sheets_sync import GoogleSheetsSync
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = '구글 스프레드시트에서 의뢰 데이터를 동기화합니다'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='실제 DB 변경 없이 테스트만 수행',
        )

    def handle(self, *args, **options):
        dry_run = options.get('dry_run', False)

        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN 모드 - 실제 변경사항 없음'))

        self.stdout.write(f'동기화 시작: {timezone.now()}')

        try:
            sync = GoogleSheetsSync()
            result = sync.sync_data()

            self.stdout.write(self.style.SUCCESS(
                f'\n동기화 완료:\n'
                f'- 새로 생성: {result["created"]}건\n'
                f'- 업데이트: {result["updated"]}건\n'
                f'- 건너뛴 항목: {result["skipped"]}건\n'
                f'- 전체 처리: {result["total"]}건'
            ))

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'동기화 실패: {str(e)}')
            )
            logger.error(f'구글 시트 동기화 오류: {str(e)}', exc_info=True)