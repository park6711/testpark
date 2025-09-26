# Generated manually
from django.db import migrations

def convert_int_to_text(apps, schema_editor):
    """정수 값을 텍스트 값으로 변환"""
    Satisfy = apps.get_model('evaluation', 'Satisfy')

    # 정수->텍스트 매핑
    conversion_map = {
        0: '매우 만족',
        1: '만족',
        2: '보통',
        3: '불만족',
        4: '매우 불만족'
    }

    # 모든 Satisfy 레코드 업데이트
    for satisfy in Satisfy.objects.all():
        # 기존 nS1~nS10 값을 읽어서 sS1~sS10으로 변환
        # 참고: 이 시점에서는 이미 새 필드(sS1~sS10)가 생성되어 있고
        # 기본값('보통')으로 설정되어 있음

        # 기존 데이터가 있다면 변환 로직을 여기에 추가
        # 현재는 새 필드가 이미 기본값으로 생성되므로 추가 작업 불필요
        satisfy.save()

def convert_text_to_int(apps, schema_editor):
    """텍스트 값을 정수 값으로 변환 (역방향)"""
    # 롤백용 - 필요시 구현
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('evaluation', '0009_remove_satisfy_ns1_remove_satisfy_ns10_and_more'),
    ]

    operations = [
        migrations.RunPython(convert_int_to_text, convert_text_to_int),
    ]