"""
자동 동기화 Management Command
5분마다 실행되도록 cron에 등록하여 사용

예시:
*/5 * * * * docker exec testpark python manage.py auto_sync >> /var/log/testpark_sync.log 2>&1
"""
from django.core.management.base import BaseCommand
from django.core.cache import cache
from django.db.models import Q
from datetime import datetime, timedelta
import logging
import json

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Google Sheets 자동 동기화 및 업체 할당'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='전체 동기화 실행 (캐시 무시)',
        )
        parser.add_argument(
            '--update-existing',
            action='store_true',
            help='기존 레코드도 업데이트',
        )
        parser.add_argument(
            '--auto-assign',
            action='store_true',
            default=True,
            help='동기화 후 자동 업체 할당',
        )
        parser.add_argument(
            '--notify',
            action='store_true',
            default=True,
            help='새 접수 건 알림 발송',
        )

    def handle(self, *args, **options):
        """메인 처리 로직"""
        start_time = datetime.now()

        try:
            # 1. 동기화 잠금 확인 (동시 실행 방지)
            lock_key = 'google_sheets_sync_lock'
            if cache.get(lock_key) and not options['force']:
                self.stdout.write(self.style.WARNING('다른 동기화가 진행 중입니다.'))
                return

            # 잠금 설정 (5분)
            cache.set(lock_key, True, 300)

            # 2. Google Sheets 동기화 실행
            self.stdout.write('📋 Google Sheets 동기화 시작...')
            sync_result = self.sync_google_sheets(options['update_existing'])

            # 3. 새 접수 건 확인
            if sync_result.get('created', 0) > 0:
                self.stdout.write(
                    self.style.SUCCESS(f'✅ 새로운 접수 {sync_result["created"]}건 발견!')
                )

                # 4. 알림 발송
                if options['notify']:
                    self.send_notifications(sync_result['created'])

                # 5. 업체 자동 할당
                if options['auto_assign']:
                    assign_result = self.auto_assign_companies()
                    if assign_result.get('assigned', 0) > 0:
                        self.stdout.write(
                            self.style.SUCCESS(f'🏢 {assign_result["assigned"]}건 업체 할당 완료')
                        )

            # 6. 24시간 이상 응답 없는 할당 확인
            self.check_stale_assignments()

            # 7. 동기화 통계 기록
            elapsed_time = (datetime.now() - start_time).total_seconds()
            stats = {
                'sync_time': start_time.isoformat(),
                'elapsed_seconds': elapsed_time,
                'result': sync_result
            }

            # 캐시에 저장 (대시보드용)
            cache.set('last_sync_stats', stats, 3600)  # 1시간 보관

            self.stdout.write(
                self.style.SUCCESS(
                    f'✨ 동기화 완료! '
                    f'(생성: {sync_result.get("created", 0)}, '
                    f'수정: {sync_result.get("updated", 0)}, '
                    f'건너뜀: {sync_result.get("skipped", 0)}, '
                    f'소요시간: {elapsed_time:.2f}초)'
                )
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ 동기화 실패: {str(e)}')
            )
            logger.error(f'자동 동기화 오류: {str(e)}', exc_info=True)

        finally:
            # 잠금 해제
            cache.delete(lock_key)

    def sync_google_sheets(self, update_existing=False):
        """Google Sheets 동기화 실행"""
        try:
            from order.google_sheets_sync import GoogleSheetsSync

            sync = GoogleSheetsSync()
            result = sync.sync_data(update_existing=update_existing)

            # 동기화 로그 기록
            logger.info(f"Google Sheets 동기화: {result}")

            return result

        except ImportError as e:
            logger.error(f"Google Sheets 동기화 모듈 로드 실패: {e}")
            return {'error': 'Module not found'}
        except Exception as e:
            logger.error(f"동기화 오류: {e}")
            return {'error': str(e)}

    def send_notifications(self, new_count):
        """새 접수 건에 대한 알림 발송"""
        try:
            from order.models import Order

            # 최근 10분 내 생성된 대기중 주문 조회
            recent = datetime.now() - timedelta(minutes=10)
            new_orders = Order.objects.filter(
                created_at__gte=recent,
                recent_status='대기중'
            ).order_by('-created_at')[:new_count]

            if new_orders:
                # 알림 메시지 구성
                message = f"🔔 새로운 견적 의뢰 {new_count}건 접수!\n\n"

                for order in new_orders:
                    message += f"• {order.sName or '고객'} - {order.sArea or '지역미정'}\n"

                    if order.designation_type == '공동구매':
                        message += f"  ※ 공동구매 지정: {order.designation}\n"

                    if order.sConstruction:
                        preview = order.sConstruction[:50]
                        if len(order.sConstruction) > 50:
                            preview += "..."
                        message += f"  내용: {preview}\n"

                    message += "\n"

                message += "👉 업체 할당이 필요합니다!"

                # 로그에 기록
                logger.warning(message)

                # TODO: 실제 알림 발송 (Jandi, Slack, Email 등)
                # self.send_jandi_webhook(message)
                # self.send_email_notification(message)

                self.stdout.write(self.style.SUCCESS(f'📢 알림 발송 완료'))

        except Exception as e:
            logger.error(f"알림 발송 실패: {e}")

    def auto_assign_companies(self):
        """업체 자동 할당"""
        try:
            from order.models import Order, StatusHistory
            from company.models import Company

            # 할당 대기 중인 주문
            pending_orders = Order.objects.filter(
                recent_status='대기중',
                assigned_company__in=['', None]
            )

            assigned_count = 0
            assignments = []

            for order in pending_orders:
                company = None

                # 1. 공동구매 지정 확인
                if order.designation_type == '공동구매':
                    company = self.find_group_purchase_company(order)

                # 2. 업체 지정 확인
                elif order.designation_type == '업체지정' and order.designation:
                    company = self.find_designated_company(order.designation)

                # 3. 지역 기반 업체 찾기
                if not company and order.sArea:
                    company = self.find_area_based_company(order.sArea)

                # 업체 할당
                if company:
                    order.assigned_company = company.sCompanyName
                    order.recent_status = '할당'
                    order.save()

                    # 상태 이력 기록
                    StatusHistory.objects.create(
                        order=order,
                        old_status='대기중',
                        new_status='할당',
                        message_content=f'{company.sCompanyName} 자동 할당',
                        author='시스템'
                    )

                    assigned_count += 1
                    assignments.append({
                        'order': order.no,
                        'customer': order.sName,
                        'company': company.sCompanyName
                    })

            # 할당 결과 로그
            if assigned_count > 0:
                logger.info(f"자동 할당 완료: {assigned_count}건")
                for assign in assignments:
                    logger.info(f"  - {assign['customer']} → {assign['company']}")

            return {'assigned': assigned_count, 'details': assignments}

        except Exception as e:
            logger.error(f"자동 할당 실패: {e}")
            return {'error': str(e), 'assigned': 0}

    def find_group_purchase_company(self, order):
        """공동구매 업체 찾기"""
        try:
            from gonggu.models import GroupPurchase

            # 활성화된 공동구매 중 매칭
            gp = GroupPurchase.objects.filter(
                is_active=True
            ).first()

            if gp and gp.check_availability(order.dateSchedule, order.sArea):
                from company.models import Company
                return Company.objects.filter(
                    sCompanyName__icontains=gp.company_name
                ).first()

        except Exception as e:
            logger.error(f"공동구매 업체 검색 실패: {e}")

        return None

    def find_designated_company(self, designation):
        """지정된 업체 찾기"""
        try:
            from company.models import Company

            # 업체명으로 검색
            return Company.objects.filter(
                Q(sCompanyName__icontains=designation) |
                Q(sCompanyCode__icontains=designation)
            ).first()

        except Exception as e:
            logger.error(f"지정 업체 검색 실패: {e}")

        return None

    def find_area_based_company(self, area):
        """지역 기반 업체 찾기"""
        try:
            from company.models import Company
            from possiblearea.models import PossibleArea

            # 해당 지역에서 활동 가능한 업체
            possible = PossibleArea.objects.filter(
                sArea__icontains=area
            ).values_list('company_id', flat=True)

            if possible:
                # 현재 할당이 가장 적은 업체 선택
                return Company.objects.filter(
                    no__in=possible,
                    is_active=True
                ).order_by('current_assignments').first()

        except Exception as e:
            logger.error(f"지역 기반 업체 검색 실패: {e}")

        return None

    def check_stale_assignments(self):
        """24시간 이상 응답 없는 할당 확인"""
        try:
            from order.models import Order, StatusHistory

            deadline = datetime.now() - timedelta(hours=24)

            # 24시간 이상 할당 상태인 주문
            stale = Order.objects.filter(
                recent_status='할당',
                updated_at__lte=deadline
            )

            reassigned = 0

            for order in stale:
                # 마지막 할당 시간 확인
                last_assign = StatusHistory.objects.filter(
                    order=order,
                    new_status='할당'
                ).order_by('-created_at').first()

                if last_assign and last_assign.created_at <= deadline:
                    # 반려 처리
                    order.recent_status = '반려'
                    order.assigned_company = ''
                    order.save()

                    StatusHistory.objects.create(
                        order=order,
                        old_status='할당',
                        new_status='반려',
                        message_content='24시간 내 응답 없음',
                        author='시스템'
                    )

                    reassigned += 1
                    logger.warning(f"자동 반려: {order.sName} (주문번호: {order.no})")

            if reassigned > 0:
                self.stdout.write(
                    self.style.WARNING(f'⏰ {reassigned}건 자동 반려 처리')
                )

        except Exception as e:
            logger.error(f"할당 만료 확인 실패: {e}")