from django.db import models


class Member(models.Model):
    """회원정보 모델"""

    # 권한 선택지
    AUTHORITY_CHOICES = [
        (0, '권한없음'),
        (1, '읽기권한'),
        (2, '쓰기권한'),
    ]

    # 카페 등급 선택지
    CAFE_GRADE_CHOICES = [
        (0, '일반'),
        (1, '광고제휴'),
        (2, '단종열린'),
        (3, '토탈열린'),
        (4, '연합회'),
    ]

    # 기본 정보
    no = models.AutoField(primary_key=True, help_text="회원 번호")
    sNaverID0 = models.CharField(max_length=255, blank=True, default='', help_text="네이버 식별자")
    bApproval = models.BooleanField(default=False, help_text="승인 여부 (False: 미승인, True: 승인)")
    sNaverID = models.CharField(max_length=255, help_text="네이버 이메일")
    sCompanyName = models.CharField(max_length=100, help_text="업체명")
    sName2 = models.CharField(max_length=50, help_text="이름2")
    noCompany = models.IntegerField(help_text="업체 번호")
    sName = models.CharField(max_length=50, help_text="성명")
    sPhone = models.CharField(max_length=20, blank=True, default='', help_text="연락처")
    nCafeGrade = models.IntegerField(
        choices=CAFE_GRADE_CHOICES,
        default=0,
        help_text="카페 등급"
    )
    nNick = models.CharField(max_length=50, blank=True, default='', help_text="별명")

    # 마스터 권한
    bMaster = models.BooleanField(default=False, help_text="마스터 여부 (False: 일반, True: 마스터)")

    # 각종 권한 설정
    nCompanyAuthority = models.IntegerField(
        choices=AUTHORITY_CHOICES,
        default=0,
        help_text="업체정보 권한"
    )
    nOrderAuthority = models.IntegerField(
        choices=AUTHORITY_CHOICES,
        default=0,
        help_text="의뢰할당 권한"
    )
    nContractAuthority = models.IntegerField(
        choices=AUTHORITY_CHOICES,
        default=0,
        help_text="계약관리 권한"
    )
    nEvaluationAuthority = models.IntegerField(
        choices=AUTHORITY_CHOICES,
        default=0,
        help_text="업체평가 권한"
    )

    # 자동 생성 필드
    created_at = models.DateTimeField(auto_now_add=True, help_text="생성일시")
    updated_at = models.DateTimeField(auto_now=True, help_text="수정일시")

    class Meta:
        db_table = 'member'
        verbose_name = '회원'
        verbose_name_plural = '회원'
        ordering = ['no']

    def __str__(self):
        return f"{self.no} - {self.sName} ({self.sCompanyName})"

    def get_authority_display_dict(self):
        """권한 정보를 딕셔너리로 반환"""
        return {
            'company': self.get_nCompanyAuthority_display(),
            'order': self.get_nOrderAuthority_display(),
            'contract': self.get_nContractAuthority_display(),
            'evaluation': self.get_nEvaluationAuthority_display(),
        }
