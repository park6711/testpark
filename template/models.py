from django.db import models

class Template(models.Model):
    """템플리트(Template) 모델"""

    # 수신대상 선택 옵션
    RECEIVER_CHOICES = [
        (0, '기타'),
        (1, '업체'),
        (2, '고객'),
    ]

    # 구분 선택 옵션
    TYPE_CHOICES = [
        (0, '문자'),
        (1, '댓글'),
    ]

    # 기본 필드
    no = models.AutoField(primary_key=True, verbose_name='템플리트ID')
    nReceiver = models.IntegerField(
        choices=RECEIVER_CHOICES,
        default=0,
        verbose_name='수신대상'
    )
    nType = models.IntegerField(
        choices=TYPE_CHOICES,
        default=0,
        verbose_name='구분'
    )
    sTitle = models.CharField(
        max_length=100,
        verbose_name='제목'
    )
    sContent = models.TextField(
        verbose_name='내용'
    )
    nUse = models.IntegerField(
        default=0,
        verbose_name='사용횟수'
    )

    # 시간 관련 필드
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일시')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일시')

    class Meta:
        db_table = 'template'
        verbose_name = '템플리트'
        verbose_name_plural = '템플리트'
        ordering = ['-no']

    def __str__(self):
        return f"[{self.get_nType_display()}] {self.sTitle}"

    def get_receiver_display_text(self):
        """수신대상 텍스트 반환"""
        return self.get_nReceiver_display()

    def get_type_display_text(self):
        """구분 텍스트 반환"""
        return self.get_nType_display()

    def increment_use_count(self):
        """사용횟수 증가"""
        self.nUse += 1
        self.save(update_fields=['nUse'])