from django.db import models


class Template(models.Model):
    """템플리트(Template) 모델"""

    # 분류 선택지 (nType) - 6종류
    TYPE_CHOICES = [
        (0, '기타'),
        (1, '댓글'),
        (2, '의뢰할당'),
        (3, '업체관리'),
        (4, '업체평가'),
        (5, '계약회계'),
    ]

    # 분류2 선택지 (nSort) - 3종류
    SORT_CHOICES = [
        (0, '기타'),
        (1, '업체'),
        (2, '고객'),
    ]


    # 기본 정보
    no = models.AutoField(primary_key=True, verbose_name='템프리트ID')

    # 분류 정보
    nType = models.IntegerField(
        choices=TYPE_CHOICES,
        default=0,
        verbose_name='분류'
    )
    nReceiver = models.IntegerField(
        choices=SORT_CHOICES,
        default=0,
        verbose_name='수신 대상'
    )

    # 템플릿 내용
    sTitle = models.CharField(max_length=200, blank=True, verbose_name='제목')
    sContent = models.TextField(verbose_name='내용')

    # 사용 통계
    nUse = models.IntegerField(default=0, verbose_name='사용횟수')

    # 자동 생성 필드
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일시')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일시')

    class Meta:
        db_table = 'template'
        verbose_name = '템플리트'
        verbose_name_plural = '템플리트'
        ordering = ['-no']  # 최신순 정렬

    def __str__(self):
        return f"템플릿 {self.no} - {self.sTitle or '제목없음'}"

    def get_type_display_with_icon(self):
        """분류 아이콘과 함께 표시"""
        type_icons = {
            0: '❓',  # 기타
            1: '💬',  # 댓글
            2: '📋',  # 의뢰할당
            3: '🏢',  # 업체관리
            4: '⭐',  # 업체평가
            5: '💰',  # 계약회계
        }
        icon = type_icons.get(self.nType, '📄')
        return f"{icon} {self.get_nType_display()}"

    def get_type_display_with_color(self):
        """분류 색상과 함께 표시"""
        type_colors = {
            0: ('기타', 'gray'),
            1: ('댓글', 'green'),
            2: ('의뢰할당', 'blue'),
            3: ('업체관리', 'orange'),
            4: ('업체평가', 'purple'),
            5: ('계약회계', 'red'),
        }
        type_name, color = type_colors.get(self.nType, ('알 수 없음', 'black'))
        return {'type': type_name, 'color': color}

    def get_receiver_display_with_icon(self):
        """수신 대상 아이콘과 함께 표시"""
        receiver_icons = {
            0: '❓',  # 기타
            1: '🏢',  # 업체
            2: '👤',  # 고객
        }
        icon = receiver_icons.get(self.nReceiver, '❓')
        return f"{icon} {self.get_nReceiver_display()}"

    def increment_usage(self):
        """사용횟수 증가"""
        self.nUse += 1
        self.save(update_fields=['nUse'])

    def get_content_preview(self, length=50):
        """내용 미리보기"""
        if len(self.sContent) <= length:
            return self.sContent
        return self.sContent[:length] + '...'

    def is_frequently_used(self):
        """자주 사용되는 템플릿 여부 (사용횟수 10회 이상)"""
        return self.nUse >= 10

    def get_usage_level(self):
        """사용 빈도 레벨"""
        if self.nUse >= 50:
            return "매우높음"
        elif self.nUse >= 20:
            return "높음"
        elif self.nUse >= 10:
            return "보통"
        elif self.nUse >= 1:
            return "낮음"
        else:
            return "미사용"

    def get_usage_color(self):
        """사용 빈도별 색상"""
        level = self.get_usage_level()
        color_map = {
            "매우높음": "red",
            "높음": "orange",
            "보통": "blue",
            "낮음": "green",
            "미사용": "gray"
        }
        return color_map.get(level, "black")

    def substitute_variables(self, **kwargs):
        """변수 치환 기능"""
        content = self.sContent
        title = self.sTitle

        # 공통 변수 치환
        variables = {
            '{업체명}': kwargs.get('company_name', ''),
            '{고객명}': kwargs.get('customer_name', ''),
            '{날짜}': kwargs.get('date', ''),
            '{시간}': kwargs.get('time', ''),
            '{전화번호}': kwargs.get('phone', ''),
            '{주소}': kwargs.get('address', ''),
            '{금액}': kwargs.get('amount', ''),
            '{계약번호}': kwargs.get('contract_no', ''),
            '{담당자}': kwargs.get('manager', ''),
        }

        # 사용자 정의 변수 치환
        for key, value in kwargs.items():
            if key not in ['company_name', 'customer_name', 'date', 'time',
                          'phone', 'address', 'amount', 'contract_no', 'manager']:
                variables[f'{{{key}}}'] = str(value)

        # 치환 실행
        for var, value in variables.items():
            content = content.replace(var, value)
            title = title.replace(var, value)

        return {
            'title': title,
            'content': content
        }

    def get_template_summary(self):
        """템플릿 요약 정보"""
        return {
            'template_id': self.no,
            'type': self.get_type_display_with_icon(),
            'type_color': self.get_type_display_with_color(),
            'receiver': self.get_receiver_display_with_icon(),
            'title': self.sTitle,
            'content_preview': self.get_content_preview(),
            'usage_count': self.nUse,
            'usage_level': self.get_usage_level(),
            'is_popular': self.is_frequently_used(),
            'created_date': self.created_at.date()
        }

    def get_similar_templates(self):
        """유사한 템플릿 찾기"""
        return Template.objects.filter(
            nType=self.nType,
            nReceiver=self.nReceiver
        ).exclude(no=self.no)[:5]

    @classmethod
    def get_popular_templates(cls, limit=10):
        """인기 템플릿 조회"""
        return cls.objects.filter(nUse__gt=0).order_by('-nUse')[:limit]

    @classmethod
    def get_templates_by_category(cls, type_filter=None, receiver_filter=None):
        """카테고리별 템플릿 조회"""
        queryset = cls.objects.all()

        if type_filter is not None:
            queryset = queryset.filter(nType=type_filter)
        if receiver_filter is not None:
            queryset = queryset.filter(nReceiver=receiver_filter)

        return queryset.order_by('-nUse', '-created_at')
