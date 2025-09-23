"""
Point 앱 시그널 - Company 삭제 시 처리
"""
from django.db.models.signals import pre_delete, pre_save
from django.dispatch import receiver
from django.db.models.deletion import ProtectedError
from company.models import Company
from .models import Point


@receiver(pre_delete, sender=Company)
def protect_company_with_points(sender, instance, **kwargs):
    """
    Company 삭제 시 관련 Point가 있으면 삭제 방지
    """
    if instance.point_records.exists():
        point_count = instance.point_records.count()
        last_balance = instance.point_records.order_by('-time', '-no').first().nRemainPoint
        raise ProtectedError(
            f"이 업체({instance.sName2})는 {point_count}개의 포인트 내역이 있어 삭제할 수 없습니다. "
            f"현재 잔액: {last_balance:,} 포인트",
            instance.point_records.all()
        )


@receiver(pre_save, sender=Company)
def check_company_withdrawal_with_points(sender, instance, **kwargs):
    """
    Company 탈퇴(dateWithdraw 설정) 시 잔액 확인
    """
    if instance.pk:  # 기존 업체 수정인 경우
        try:
            old_instance = Company.objects.get(pk=instance.pk)
            # dateWithdraw가 None에서 값이 설정되는 경우 (탈퇴 처리)
            if old_instance.dateWithdraw is None and instance.dateWithdraw is not None:
                # 포인트 잔액 확인
                last_point = Point.objects.filter(
                    noCompany=instance
                ).order_by('-time', '-no').first()

                if last_point and last_point.nRemainPoint != 0:
                    # 잔액이 0이 아니면 경고 메시지 (실제로 막지는 않음)
                    print(f"⚠️ 경고: {instance.sName2} 업체 탈퇴 처리 중 - 포인트 잔액: {last_point.nRemainPoint:,}")
        except Company.DoesNotExist:
            pass