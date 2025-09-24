from django.db import models

class GlobalVar(models.Model):
    TYPE_CHOICES = [
        ('int', '정수'),
        ('float', '실수'),
        ('str', '문자열'),
        ('bool', '불린'),
    ]

    key = models.CharField(max_length=100, unique=True, verbose_name='변수명')
    value = models.TextField(verbose_name='값')
    var_type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='str', verbose_name='타입')
    description = models.TextField(blank=True, verbose_name='설명')
    category = models.CharField(max_length=50, default='EVALUATION', verbose_name='카테고리')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일시')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일시')

    class Meta:
        db_table = 'global_vars'
        verbose_name = '전역변수'
        verbose_name_plural = '전역변수'
        ordering = ['category', 'key']

    def __str__(self):
        return f"{self.key} = {self.value}"

    def get_typed_value(self):
        """타입에 맞게 변환된 값 반환"""
        if self.var_type == 'int':
            return int(self.value)
        elif self.var_type == 'float':
            return float(self.value)
        elif self.var_type == 'bool':
            return self.value.lower() in ('true', '1', 'yes')
        else:
            return self.value
