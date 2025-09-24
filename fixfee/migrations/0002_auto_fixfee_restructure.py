# Generated manually for FixFee model restructuring

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fixfee', '0001_initial'),
    ]

    operations = [
        # 1. FixFeeDate 모델 생성
        migrations.CreateModel(
            name='FixFeeDate',
            fields=[
                ('no', models.AutoField(primary_key=True, serialize=False, verbose_name='고정비납부기준일ID')),
                ('date', models.DateField(unique=True, verbose_name='납부기준일')),
            ],
            options={
                'verbose_name': '고정비납부기준일',
                'verbose_name_plural': '고정비납부기준일',
                'db_table': 'fix_fee_date',
                'ordering': ['-date'],
            },
        ),

        # 2. FixFee 모델에 새 필드 추가
        migrations.AddField(
            model_name='fixfee',
            name='noFixFeeDate',
            field=models.IntegerField(db_index=True, default=1, verbose_name='납부기준일ID'),
            preserve_default=False,
        ),

        migrations.AddField(
            model_name='fixfee',
            name='nFixFee',
            field=models.IntegerField(default=0, verbose_name='월고정비(원)'),
        ),

        migrations.AddField(
            model_name='fixfee',
            name='nType',
            field=models.IntegerField(
                choices=[(0, '계좌이체'), (1, '우수업체'), (2, '최우수업체'), (3, '기타')],
                default=0,
                verbose_name='납부방식'
            ),
        ),

        # 3. 기존 필드 제거
        migrations.RemoveField(
            model_name='fixfee',
            name='dateToDo',
        ),

        migrations.RemoveField(
            model_name='fixfee',
            name='nDeposit',
        ),

        migrations.RemoveField(
            model_name='fixfee',
            name='bDeposit',
        ),

        # 4. dateDeposit 필드 수정 (verbose_name 변경)
        migrations.AlterField(
            model_name='fixfee',
            name='dateDeposit',
            field=models.DateField(blank=True, null=True, verbose_name='완납일자'),
        ),

        # 5. sMemo 필드 수정 (max_length 추가)
        migrations.AlterField(
            model_name='fixfee',
            name='sMemo',
            field=models.TextField(blank=True, max_length=500, verbose_name='비고'),
        ),

        # 6. noCompany 필드에 db_index 추가
        migrations.AlterField(
            model_name='fixfee',
            name='noCompany',
            field=models.IntegerField(db_index=True, verbose_name='업체ID'),
        ),

        # 7. Meta 옵션 변경
        migrations.AlterModelOptions(
            name='fixfee',
            options={
                'ordering': ['-noFixFeeDate', '-no'],
                'verbose_name': '고정비납부',
                'verbose_name_plural': '고정비납부'
            },
        ),

        # 8. unique_together 추가
        migrations.AlterUniqueTogether(
            name='fixfee',
            unique_together={('noCompany', 'noFixFeeDate')},
        ),
    ]