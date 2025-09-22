from django.db import models


class License(models.Model):
    """사업자 정보 모델"""

    # 기본 정보
    no = models.AutoField(primary_key=True, help_text="사업자 번호")
    noCompany = models.IntegerField(help_text="업체 번호")
    sCompanyName = models.CharField(max_length=100, help_text="업체명")
    sLicenseNo = models.CharField(max_length=50, help_text="사업자등록번호")
    sCeoName = models.CharField(max_length=50, help_text="대표자명")
    sAccountMail = models.CharField(max_length=100, help_text="계좌 메일")

    # 파일 필드
    fileLicense = models.FileField(
        upload_to='license/license_files/',
        blank=True,
        null=True,
        help_text="사업자등록증 파일"
    )

    # 계좌 정보
    sAccount = models.CharField(max_length=100, help_text="계좌번호")
    fileAccount = models.FileField(
        upload_to='license/account_files/',
        blank=True,
        null=True,
        help_text="통장사본 파일"
    )

    # 자동 생성 필드
    created_at = models.DateTimeField(auto_now_add=True, help_text="생성일시")
    updated_at = models.DateTimeField(auto_now=True, help_text="수정일시")

    class Meta:
        db_table = 'license'
        verbose_name = '사업자'
        verbose_name_plural = '사업자'
        ordering = ['no']

    def __str__(self):
        return f"{self.no} - {self.sCompanyName} ({self.sCeoName})"

    def get_company_name(self):
        """업체명 반환"""
        return self.sCompanyName

    def get_license_file_name(self):
        """사업자등록증 파일명 반환"""
        if self.fileLicense:
            return self.fileLicense.name.split('/')[-1]
        return None

    def get_account_file_name(self):
        """통장사본 파일명 반환"""
        if self.fileAccount:
            return self.fileAccount.name.split('/')[-1]
        return None

    def get_company_sname2(self):
        """연결된 회사의 sName2 반환"""
        try:
            from company.models import Company
            company = Company.objects.get(no=self.noCompany)
            return company.sName2 if company.sName2 else company.sName1
        except Company.DoesNotExist:
            return f"업체번호: {self.noCompany}"

    def delete(self, *args, **kwargs):
        """License 삭제 시 관련된 Company의 noLicenseRepresent 값 조정"""
        deleted_license_no = self.no

        # 이 License를 noLicenseRepresent로 참조하는 Company들을 찾아서 -1로 설정
        from company.models import Company
        Company.objects.filter(noLicenseRepresent=deleted_license_no).update(noLicenseRepresent=-1)
        print(f"DEBUG: License {deleted_license_no} deleted - Updated Company noLicenseRepresent references to -1")

        # License.no가 삭제될 번호 이상인 Company들의 noLicenseRepresent 값을 1씩 감소
        companies_to_update = Company.objects.filter(noLicenseRepresent__gt=deleted_license_no)
        companies_count = companies_to_update.count()
        if companies_count > 0:
            for company in companies_to_update:
                company.noLicenseRepresent -= 1
                company.save()
            print(f"DEBUG: Updated {companies_count} Company noLicenseRepresent references after License {deleted_license_no} deletion")

        # 실제 삭제 수행
        super().delete(*args, **kwargs)
