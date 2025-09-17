from django.db import models


class Staff(models.Model):
    """
    스텝 정보를 관리하는 모델
    """
    MASTER_CHOICES = [
        (0, '일반'),
        (1, '마스터'),
        (2, '슈퍼마스터'),
    ]

    AUTHORITY_CHOICES = [
        (0, '권한없음'),
        (1, '읽기권한'),
        (2, '쓰기권한'),
    ]

    no = models.AutoField(primary_key=True, help_text="No")
    sNaverID0 = models.CharField(max_length=255, help_text="네이버 식별자")
    bApproval = models.BooleanField(default=False, help_text="승인 여부")
    sNaverID = models.CharField(max_length=255, help_text="네이버 ID")
    sName = models.CharField(max_length=255, help_text="이름")
    sTeam = models.CharField(max_length=255, help_text="팀")
    sTitle = models.CharField(max_length=255, help_text="직급")
    sNick = models.CharField(max_length=255, help_text="닉네임")
    sGoogleID = models.CharField(max_length=255, blank=True, null=True, help_text="구글 ID")
    sPhone1 = models.CharField(max_length=255, blank=True, null=True, help_text="업무 핸드폰")
    sPhone2 = models.CharField(max_length=255, blank=True, null=True, help_text="개인 핸드폰")

    nMaster = models.IntegerField(
        choices=MASTER_CHOICES,
        default=0,
        help_text="마스터 타입 (0:일반, 1:마스터, 2:슈퍼마스터)"
    )
    nStaffAuthority = models.IntegerField(
        choices=AUTHORITY_CHOICES,
        default=0,
        help_text="스텝정보 권한 (0:권한없음, 1:읽기권한, 2:쓰기권한)"
    )
    nCompanyAuthority = models.IntegerField(
        choices=AUTHORITY_CHOICES,
        default=0,
        help_text="업체정보 권한 (0:권한없음, 1:읽기권한, 2:쓰기권한)"
    )
    nOrderAuthority = models.IntegerField(
        choices=AUTHORITY_CHOICES,
        default=0,
        help_text="의뢰할당 권한 (0:권한없음, 1:읽기권한, 2:쓰기권한)"
    )
    nContractAuthority = models.IntegerField(
        choices=AUTHORITY_CHOICES,
        default=0,
        help_text="계약관리 권한 (0:권한없음, 1:읽기권한, 2:쓰기권한)"
    )
    nEvaluationAuthority = models.IntegerField(
        choices=AUTHORITY_CHOICES,
        default=0,
        help_text="업체평가 권한 (0:권한없음, 1:읽기권한, 2:쓰기권한)"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'staff'
        verbose_name = '스텝'
        verbose_name_plural = '스텝들'
        ordering = ['no']

    def __str__(self):
        return f"{self.no} - {self.sName} ({self.sTeam})"

    def get_master_display_korean(self):
        """마스터 타입을 한국어로 반환"""
        return dict(self.MASTER_CHOICES).get(self.nMaster, '알 수 없음')

    def get_authority_summary(self):
        """권한 요약 반환"""
        authorities = {
            '스텝정보': dict(self.AUTHORITY_CHOICES).get(self.nStaffAuthority),
            '업체정보': dict(self.AUTHORITY_CHOICES).get(self.nCompanyAuthority),
            '의뢰할당': dict(self.AUTHORITY_CHOICES).get(self.nOrderAuthority),
            '계약관리': dict(self.AUTHORITY_CHOICES).get(self.nContractAuthority),
            '업체평가': dict(self.AUTHORITY_CHOICES).get(self.nEvaluationAuthority),
        }
        return authorities