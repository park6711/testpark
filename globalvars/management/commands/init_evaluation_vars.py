from django.core.management.base import BaseCommand
from globalvars.models import GlobalVar


class Command(BaseCommand):
    help = 'Initialize evaluation global variables'

    def handle(self, *args, **kwargs):
        # G_N_EVALUATION_NO 초기화
        var, created = GlobalVar.objects.get_or_create(
            key='G_N_EVALUATION_NO',
            defaults={
                'value': '62',  # 2025년 7-8월 회차
                'var_type': 'int',
                'description': '현재 진행 중인 업체평가 회차 번호',
                'category': 'EVALUATION'
            }
        )

        if created:
            self.stdout.write(
                self.style.SUCCESS(
                    f"✅ Created G_N_EVALUATION_NO with value: {var.value}"
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    f"⚠️  G_N_EVALUATION_NO already exists with value: {var.value}"
                )
            )

        # 기타 평가 관련 전역변수 추가 (필요시)
        other_vars = [
            {
                'key': 'G_EVALUATION_AUTO_START',
                'value': 'false',
                'var_type': 'bool',
                'description': '평가 자동 시작 여부',
                'category': 'EVALUATION'
            },
            {
                'key': 'G_EVALUATION_NOTIFY_DAYS',
                'value': '3',
                'var_type': 'int',
                'description': '평가 시작 전 알림 일수',
                'category': 'EVALUATION'
            }
        ]

        for var_data in other_vars:
            var, created = GlobalVar.objects.get_or_create(
                key=var_data['key'],
                defaults=var_data
            )

            if created:
                self.stdout.write(
                    f"  Created {var_data['key']}: {var_data['value']}"
                )

        # 전체 평가 변수 출력
        self.stdout.write("\n📊 Current evaluation variables:")
        eval_vars = GlobalVar.objects.filter(category='EVALUATION')
        for var in eval_vars:
            self.stdout.write(
                f"  {var.key} = {var.value} ({var.var_type})"
            )