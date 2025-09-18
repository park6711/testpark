from django.db import models


class Company(models.Model):
    TYPE_CHOICES = [
        (0, '일반토탈'),
        (1, '고정비토탈'),
        (2, '부분단종'),
        (3, '순수단종'),
        (4, 'btoc제휴'),
        (5, 'btob제휴'),
    ]

    CONDITION_CHOICES = [
        (0, '준비중'),
        (1, '정상'),
        (2, '일시정지'),
        (3, '탈퇴'),
    ]

    REFUND_CHOICES = [
        (0, '계좌이체'),
        (1, '포인트적립'),
    ]

    no = models.AutoField(primary_key=True)
    sName1 = models.CharField(max_length=100, verbose_name='열린업체명1')
    sName2 = models.CharField(max_length=100, blank=True, verbose_name='열린업체명2')
    sName3 = models.CharField(max_length=100, blank=True, verbose_name='열린업체명3')
    sNaverID = models.CharField(max_length=50, blank=True, verbose_name='네이버 ID')
    nType = models.IntegerField(choices=TYPE_CHOICES, default=0, verbose_name='업체 타입')
    nCondition = models.IntegerField(choices=CONDITION_CHOICES, default=0, verbose_name='업체 상태')
    sCompanyName = models.CharField(max_length=200, verbose_name='업체명')
    sAddress = models.TextField(verbose_name='주소')
    nMember = models.IntegerField(default=0, verbose_name='직원수')
    sBuildLicense = models.CharField(max_length=100, blank=True, verbose_name='건설면허')
    fileBuildLicense = models.FileField(upload_to='build_licenses/', blank=True, null=True, verbose_name='건설면허 사진')
    sStrength = models.TextField(blank=True, verbose_name='강점')
    sCeoName = models.CharField(max_length=50, blank=True, verbose_name='대표자명')
    sCeoPhone = models.CharField(max_length=20, blank=True, verbose_name='대표자 연락처')
    sCeoMail = models.EmailField(blank=True, verbose_name='대표자 이메일')
    fileCeo = models.FileField(upload_to='ceo_files/', blank=True, null=True, verbose_name='대표자 사진')
    sSaleName = models.CharField(max_length=50, blank=True, verbose_name='영업담당자명')
    sSalePhone = models.CharField(max_length=20, blank=True, verbose_name='영업담당자 연락처')
    sSaleMail = models.EmailField(blank=True, verbose_name='영업담당자 이메일')
    fileSale = models.FileField(upload_to='sale_files/', blank=True, null=True, verbose_name='영업담당자 사진')
    sAccoutName = models.CharField(max_length=50, blank=True, verbose_name='회계담당자명')
    sAccoutPhone = models.CharField(max_length=20, blank=True, verbose_name='회계담당자 연락처')
    sAccoutMail = models.EmailField(blank=True, verbose_name='회계담당자 이메일')
    fileLicense = models.FileField(upload_to='license_files/', blank=True, null=True, verbose_name='사업자등록증 사진')
    sEmergencyName = models.CharField(max_length=50, blank=True, verbose_name='비상연락처명')
    sEmergencyPhone = models.CharField(max_length=20, blank=True, verbose_name='비상연락처')
    sEmergencyRelation = models.CharField(max_length=50, blank=True, verbose_name='비상연락처 관계')
    dateJoin = models.DateField(null=True, blank=True, verbose_name='가입일')
    nJoinFee = models.IntegerField(default=0, verbose_name='가입비(원)')
    nDeposit = models.IntegerField(default=0, verbose_name='보증금(원)')
    nFixFee = models.IntegerField(default=0, verbose_name='고정비(원)')
    dateFixFeeStart = models.DateField(null=True, blank=True, verbose_name='고정비 시작일')
    nFeePercent = models.FloatField(default=0.0, verbose_name='수수료율')
    nOrderFee = models.IntegerField(default=0, verbose_name='오더당 수수료(원)')
    nReportPeriod = models.IntegerField(default=0, verbose_name='보고주기')
    fileCampaignAgree = models.FileField(upload_to='campaign_agrees/', blank=True, null=True, verbose_name='캠페인 동의서')
    bPrivacy = models.BooleanField(default=False, verbose_name='개인정보동의')
    bCompetition = models.BooleanField(default=False, verbose_name='경업금지동의')
    bAptAll = models.BooleanField(default=False, verbose_name='아파트 올수리')
    bAptPart = models.BooleanField(default=False, verbose_name='아파트 부분')
    bHouseAll = models.BooleanField(default=False, verbose_name='주택 올수리')
    bHousePart = models.BooleanField(default=False, verbose_name='주택 부분')
    bCommerceAll = models.BooleanField(default=False, verbose_name='상업시설 올수리')
    bCommercePart = models.BooleanField(default=False, verbose_name='상업시설 부분')
    bBuild = models.BooleanField(default=False, verbose_name='신축/증축')
    bExtra = models.BooleanField(default=False, verbose_name='부가서비스')
    bUnion = models.BooleanField(default=False, verbose_name='연합회')
    bMentor = models.BooleanField(default=False, verbose_name='멘토')
    sMentee = models.CharField(max_length=100, blank=True, verbose_name='멘티')
    nRefund = models.IntegerField(choices=REFUND_CHOICES, default=0, verbose_name='선호 환불방식')
    sManager = models.CharField(max_length=50, blank=True, verbose_name='담당 스텝')
    dateWithdraw = models.DateField(null=True, blank=True, verbose_name='탈퇴일')
    sWithdraw = models.CharField(max_length=200, blank=True, verbose_name='탈퇴사유')
    sMemo = models.TextField(blank=True, verbose_name='메모')
    sPicture = models.CharField(max_length=200, blank=True, verbose_name='업체사진')
    sGallery = models.TextField(blank=True, verbose_name='갤러리방')
    sEstimate = models.TextField(blank=True, verbose_name='견적방')

    class Meta:
        db_table = 'company'
        verbose_name = '업체'
        verbose_name_plural = '업체'

    def __str__(self):
        return f"{self.sCompanyName} ({self.sName1})"


class ContractFile(models.Model):
    """협약서 파일 모델 (다중 파일 업로드용)"""
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='contract_files', verbose_name='업체')
    file = models.FileField(upload_to='contracts/', verbose_name='협약서 사진')
    name = models.CharField(max_length=255, blank=True, verbose_name='파일명')
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name='업로드 일시')

    class Meta:
        db_table = 'company_contract_file'
        verbose_name = '협약서 파일'
        verbose_name_plural = '협약서 파일들'
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.company.sCompanyName} - {self.name or self.file.name}"

    def save(self, *args, **kwargs):
        if not self.name and self.file:
            self.name = self.file.name
        super().save(*args, **kwargs)
