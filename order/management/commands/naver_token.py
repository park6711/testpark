"""
네이버 OAuth 토큰 관리 명령어
"""

import json
import os
from django.core.management.base import BaseCommand
from django.core.cache import cache
from order.naver_oauth import NaverOAuthManager, NaverCafeRealAPI


class Command(BaseCommand):
    help = '네이버 OAuth 토큰 관리 명령어'

    def add_arguments(self, parser):
        parser.add_argument(
            '--set',
            type=str,
            help='액세스 토큰 설정 (예: --set YOUR_ACCESS_TOKEN)'
        )
        parser.add_argument(
            '--set-refresh',
            type=str,
            help='리프레시 토큰 설정 (예: --set-refresh YOUR_REFRESH_TOKEN)'
        )
        parser.add_argument(
            '--show',
            action='store_true',
            help='현재 저장된 토큰 표시'
        )
        parser.add_argument(
            '--test',
            action='store_true',
            help='테스트 게시글 작성'
        )
        parser.add_argument(
            '--auth-url',
            action='store_true',
            help='네이버 로그인 URL 생성'
        )
        parser.add_argument(
            '--set-env',
            action='store_true',
            help='환경 변수 설정 가이드'
        )

    def handle(self, *args, **options):
        oauth_manager = NaverOAuthManager()

        # 액세스 토큰 설정
        if options['set']:
            token = options['set']
            cache.set('naver_access_token', token, 3600)  # 1시간
            oauth_manager.save_token_to_file(token)
            self.stdout.write(self.style.SUCCESS(f'✅ 액세스 토큰이 설정되었습니다.'))
            self.stdout.write(f'토큰: {token[:20]}...')

        # 리프레시 토큰 설정
        elif options['set_refresh']:
            token = options['set_refresh']
            cache.set('naver_refresh_token', token, 30 * 24 * 3600)  # 30일
            self.stdout.write(self.style.SUCCESS(f'✅ 리프레시 토큰이 설정되었습니다.'))
            self.stdout.write(f'토큰: {token[:20]}...')

        # 현재 토큰 표시
        elif options['show']:
            access_token = cache.get('naver_access_token')
            refresh_token = cache.get('naver_refresh_token')
            file_token = oauth_manager.load_token_from_file()

            self.stdout.write('=== 현재 토큰 상태 ===')

            if access_token:
                self.stdout.write(self.style.SUCCESS(f'✅ 캐시 액세스 토큰: {access_token[:20]}...'))
            else:
                self.stdout.write(self.style.WARNING('❌ 캐시 액세스 토큰 없음'))

            if refresh_token:
                self.stdout.write(self.style.SUCCESS(f'✅ 리프레시 토큰: {refresh_token[:20]}...'))
            else:
                self.stdout.write(self.style.WARNING('❌ 리프레시 토큰 없음'))

            if file_token:
                self.stdout.write(self.style.SUCCESS(f'✅ 파일 저장 토큰: {file_token[:20]}...'))
            else:
                self.stdout.write(self.style.WARNING('❌ 파일 저장 토큰 없음'))

        # 테스트 게시
        elif options['test']:
            self.stdout.write('=== 네이버 카페 테스트 게시 ===')

            from order.naver_oauth import test_real_posting
            result = test_real_posting()

            if result['success']:
                self.stdout.write(self.style.SUCCESS(f'✅ 게시 성공!'))
                self.stdout.write(f'게시글 URL: {result["article_url"]}')
            else:
                self.stdout.write(self.style.ERROR(f'❌ 게시 실패!'))
                self.stdout.write(f'에러: {result.get("error")}')
                self.stdout.write(f'메시지: {result.get("message")}')

        # 로그인 URL 생성
        elif options['auth_url']:
            if not oauth_manager.client_id:
                self.stdout.write(self.style.ERROR('❌ NAVER_CLIENT_ID가 설정되지 않았습니다.'))
                self.stdout.write('환경 변수를 설정하거나 settings.py를 확인하세요.')
                return

            auth_url = oauth_manager.get_authorization_url()
            self.stdout.write('=== 네이버 로그인 URL ===')
            self.stdout.write(self.style.SUCCESS(auth_url))
            self.stdout.write('')
            self.stdout.write('1. 위 URL에 접속하여 네이버 로그인')
            self.stdout.write('2. 권한 동의 후 리다이렉트되는 URL에서 code 파라미터 복사')
            self.stdout.write('3. 복사한 code로 액세스 토큰 획득')

        # 환경 변수 설정 가이드
        elif options['set_env']:
            self.stdout.write('=== 네이버 API 환경 변수 설정 가이드 ===\n')
            self.stdout.write('1. 네이버 개발자센터 접속:')
            self.stdout.write('   https://developers.naver.com/apps/\n')

            self.stdout.write('2. 애플리케이션 등록 또는 선택\n')

            self.stdout.write('3. API 설정에서 다음 권한 추가:')
            self.stdout.write('   - 네이버 로그인')
            self.stdout.write('   - 카페\n')

            self.stdout.write('4. 환경 변수 설정:')
            self.stdout.write(self.style.WARNING('   export NAVER_CLIENT_ID="YOUR_CLIENT_ID"'))
            self.stdout.write(self.style.WARNING('   export NAVER_CLIENT_SECRET="YOUR_CLIENT_SECRET"'))
            self.stdout.write(self.style.WARNING('   export NAVER_REDIRECT_URI="http://your-domain/api/naver/callback"\n'))

            self.stdout.write('5. Docker를 사용 중이라면 docker-compose.yml에 추가:')
            self.stdout.write('   environment:')
            self.stdout.write('     - NAVER_CLIENT_ID=YOUR_CLIENT_ID')
            self.stdout.write('     - NAVER_CLIENT_SECRET=YOUR_CLIENT_SECRET\n')

            self.stdout.write('6. 토큰 획득 프로세스:')
            self.stdout.write('   a) python manage.py naver_token --auth-url')
            self.stdout.write('   b) 생성된 URL로 로그인')
            self.stdout.write('   c) 리다이렉트 URL에서 code 파라미터 복사')
            self.stdout.write('   d) 코드로 토큰 획득 (별도 구현 필요)\n')

        else:
            self.stdout.write('사용법:')
            self.stdout.write('  python manage.py naver_token --set ACCESS_TOKEN')
            self.stdout.write('  python manage.py naver_token --set-refresh REFRESH_TOKEN')
            self.stdout.write('  python manage.py naver_token --show')
            self.stdout.write('  python manage.py naver_token --test')
            self.stdout.write('  python manage.py naver_token --auth-url')
            self.stdout.write('  python manage.py naver_token --set-env')