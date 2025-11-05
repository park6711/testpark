from django.db import models
from django.utils import timezone
import uuid


class CompanyReport(models.Model):
    """업체계약보고(CompanyReport) 모델"""

    # 보고구분 선택지
    TYPE_CHOICES = [
        (0, '계약(입금X)'),
        (1, '계약(입금O)'),
        (2, '증액(입금X)'),
        (3, '증액(입금O)'),
        (4, '감액(환불X)'),
        (5, '감액(환불O)'),
        (6, '취소(환불X)'),
        (7, '취소(환불O)'),
    ]

    # 공사유형 선택지
    CONSTRUCTION_TYPE_CHOICES = [
        (0, '[카페건]인테리어/리모델링/기타'),
        (1, '[카테건]신축/증축/개축'),
        (2, '[소개건]인테리어/리모델링/기타'),
        (3, '[소개건]신축/증축/개축'),
    ]

    # 환불방식 선택지
    REFUND_TYPE_CHOICES = [
        (0, '계좌이체'),
        (1, '포인트적립'),
    ]

    # 기본 정보 - ID, UUID와 타임스탬프
    no = models.AutoField(primary_key=True, verbose_name='업체계약보고ID')
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, verbose_name='UUID')
    sTimeStamp = models.CharField(max_length=50, blank=True, verbose_name='타임스탬프')
    timeStamp = models.DateTimeField(null=True, blank=True, verbose_name='타임스탬프')

    # 업체 정보
    sCompanyName = models.CharField(max_length=200, blank=True, verbose_name='업체명')
    noCompany = models.IntegerField(verbose_name='업체ID')

    # 고객 정보
    sName = models.CharField(max_length=50, blank=True, verbose_name='고객이름')
    sPhone = models.CharField(max_length=20, blank=True, verbose_name='고객핸드폰')

    # 보고 정보
    nType = models.IntegerField(
        choices=TYPE_CHOICES,
        default=0,
        verbose_name='보고구분'
    )
    noPre = models.IntegerField(null=True, blank=True, verbose_name='관련 이전보고 ID')
    noNext = models.IntegerField(null=True, blank=True, verbose_name='관련 이후보고 ID')

    # 공사 유형 및 링크
    nConType = models.IntegerField(
        choices=CONSTRUCTION_TYPE_CHOICES,
        default=0,
        verbose_name='공사유형'
    )
    sPost = models.CharField(max_length=200, blank=True, verbose_name='게시글 링크')
    noOrder = models.IntegerField(null=True, blank=True, verbose_name='의뢰ID')
    noAssign = models.IntegerField(null=True, blank=True, verbose_name='할당ID')
    sArea = models.TextField(blank=True, verbose_name='공사지역')

    # 계약 정보 (구글 원본 텍스트와 변환 필드)
    sDateContract = models.CharField(max_length=50, blank=True, verbose_name='공사계약일(구글)')
    dateContract = models.DateField(null=True, blank=True, verbose_name='공사계약일')
    sDateSchedule = models.CharField(max_length=50, blank=True, verbose_name='공사 완료예정일(구글)')
    dateSchedule = models.DateField(null=True, blank=True, verbose_name='공사 완료예정일')
    sConMoney = models.CharField(max_length=50, blank=True, verbose_name='공사금액(구글)')
    nConMoney = models.IntegerField(default=0, verbose_name='공사금액')

    # 수수료 및 정산 정보
    nFee = models.IntegerField(default=0, verbose_name='수수료(원)')
    nPreConMoney = models.IntegerField(default=0, verbose_name='이전보고 공사금액')
    nPreFee = models.IntegerField(default=0, verbose_name='이전보고 수수료(원)')
    nAppPoint = models.IntegerField(default=0, verbose_name='적용포인트')
    nDemand = models.IntegerField(default=0, verbose_name='청구액/환불액(원)')

    # 입금/환불 정보
    dateDeposit = models.DateField(null=True, blank=True, verbose_name='입금일/환불일')
    nDeposit = models.IntegerField(default=0, verbose_name='입금액/환불액')
    nExcess = models.IntegerField(default=0, verbose_name='과/미입금(+ or -)')
    nRefund = models.IntegerField(
        choices=REFUND_TYPE_CHOICES,
        default=0,
        verbose_name='환불방식'
    )

    # 세금계산서 및 계좌 정보
    sTaxCompany = models.CharField(max_length=200, blank=True, verbose_name='전자세금계산서 발행 사업자')
    sAccount = models.CharField(max_length=100, blank=True, verbose_name='환불 통장계좌')

    # 파일 및 메모
    sFile = models.TextField(blank=True, verbose_name='계약서 링크')
    file = models.FileField(upload_to='company_reports/', blank=True, null=True, verbose_name='증빙자료')
    sCompanyMemo = models.TextField(blank=True, verbose_name='남긴 말씀')
    sStaffMemo = models.TextField(blank=True, verbose_name='메모')
    sWorker = models.CharField(max_length=50, blank=True, verbose_name='보고자')

    # 자동 생성 필드
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일시')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일시')

    class Meta:
        db_table = 'company_report'
        verbose_name = '업체계약보고'
        verbose_name_plural = '업체계약보고'
        ordering = ['-no']  # 최신순 정렬

    def save(self, *args, **kwargs):
        """저장 시 수수료 자동 계산"""
        if not self.nFee:  # 수수료가 설정되지 않았다면 자동 계산
            self.nFee = self.calculate_fee()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"보고 {self.no} - {self.sName} ({self.get_nType_display()})"

    def get_company_name(self):
        """연결된 업체명 반환"""
        try:
            from company.models import Company
            company = Company.objects.get(no=self.noCompany)
            return company.sCompanyName or f"업체{self.noCompany}"
        except:
            return f"업체{self.noCompany}"

    def get_assign_info(self):
        """연결된 할당 정보 반환"""
        if not self.noAssign:
            return None
        try:
            from order.models import Assign
            assign = Assign.objects.get(no=self.noAssign)
            return assign
        except:
            return None

    def calculate_fee(self):
        """공사유형에 따른 수수료 자동 계산"""
        if self.nConMoney <= 0:
            return 0

        if self.nConType == 0:  # [카페건]인테리어/리모델링/기타 (5.5%)
            if self.nConMoney < 50000000:
                return int(self.nConMoney * 0.055)
            else:
                return int(50000000 * 0.055 + (self.nConMoney - 50000000) * 0.033)
        elif self.nConType == 1:  # [카테건]신축/증축/개축 (3.3%)
            return int(self.nConMoney * 0.033)
        elif self.nConType == 2:  # [소개건]인테리어/리모델링/기타 (3.3%)
            return int(self.nConMoney * 0.033)
        elif self.nConType == 3:  # [소개건]신축/증축/개축 (2.2%)
            return int(self.nConMoney * 0.022)
        else:
            return 0

    def get_type_display_with_color(self):
        """보고구분과 색상 정보 반환"""
        type_colors = {
            0: ('계약(입금X)', 'info'),      # 파란색
            1: ('계약(입금O)', 'success'),   # 초록색
            2: ('증액(입금X)', 'info'),      # 파란색
            3: ('증액(입금O)', 'success'),   # 초록색
            4: ('감액(환불X)', 'warning'),   # 노란색
            5: ('감액(환불O)', 'secondary'), # 회색
            6: ('취소(환불X)', 'danger'),    # 빨간색
            7: ('취소(환불O)', 'dark'),      # 검은색
            8: ('수수료조정', 'primary'),    # 주황색
        }
        type_name, color = type_colors.get(self.nType, ('알 수 없음', 'secondary'))
        return {'type': type_name, 'color': color}

    def get_construction_type_short(self):
        """공사유형 짧은 표시"""
        type_map = {
            0: '카페-인테리어', 1: '카테-신축', 2: '소개-인테리어', 3: '소개-신축'
        }
        return type_map.get(self.nConType, '기타')

    def get_money_summary(self):
        """금액 요약 정보 반환"""
        return {
            'contract_money': self.nConMoney,
            'fee': self.nFee,
            'demand': self.nDemand,
            'deposit': self.nDeposit,
            'excess': self.nExcess
        }

    def get_profit_margin(self):
        """수익률 계산 (수수료/공사금액*100)"""
        if self.nConMoney > 0:
            return round((self.nFee / self.nConMoney) * 100, 2)
        return 0


class CompanyReportFile(models.Model):
    """업체계약보고 첨부파일 모델"""

    no = models.AutoField(primary_key=True, verbose_name='파일ID')
    report = models.ForeignKey(
        CompanyReport,
        on_delete=models.CASCADE,
        related_name='report_files',
        verbose_name='계약보고'
    )
    file = models.FileField(upload_to='company_report_files/%Y/%m/', verbose_name='파일')
    original_name = models.CharField(max_length=255, verbose_name='원본 파일명')
    file_size = models.IntegerField(verbose_name='파일 크기')
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name='업로드 시간')
    uploaded_by = models.CharField(max_length=50, blank=True, verbose_name='업로드한 사람')

    class Meta:
        db_table = 'company_report_file'
        verbose_name = '업체계약보고 첨부파일'
        verbose_name_plural = '업체계약보고 첨부파일'
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.report.no} - {self.original_name}"

    def delete(self, *args, **kwargs):
        """파일 삭제 시 실제 파일도 함께 삭제"""
        if self.file:
            self.file.delete()
        super().delete(*args, **kwargs)

    def is_paid(self):
        """입금 완료 여부"""
        return self.nType in [1, 3, 5, 7]  # 입금O 상태들

    def is_contract_completed(self):
        """계약 완료 여부"""
        return self.nType >= 0

    def is_cancelled(self):
        """취소 여부"""
        return self.nType in [6, 7]

    def get_order_info(self):
        """연결된 의뢰 정보 반환"""
        if not self.noOrder:
            return None
        try:
            from order.models import Order
            order = Order.objects.get(no=self.noOrder)
            return order
        except:
            return None

    def get_schedule_status(self):
        """공사 일정 상태 반환"""
        if not self.dateSchedule:
            return "일정 미정"

        today = timezone.localtime().date()
        diff_days = (self.dateSchedule - today).days

        if diff_days < 0:
            return f"완료 예정일 지남 ({abs(diff_days)}일)"
        elif diff_days == 0:
            return "완료 예정일 당일"
        elif diff_days <= 7:
            return f"완료 예정일 {diff_days}일 전"
        else:
            return f"완료까지 {diff_days}일"

    def get_contract_duration(self):
        """계약일부터 완료예정일까지 기간"""
        if self.dateContract and self.dateSchedule:
            return (self.dateSchedule - self.dateContract).days
        return None

    def get_related_reports(self):
        """관련 보고서들 반환 (이전/이후)"""
        related = {}
        if self.noPre:
            try:
                related['previous'] = CompanyReport.objects.get(no=self.noPre)
            except CompanyReport.DoesNotExist:
                pass
        if self.noNext:
            try:
                related['next'] = CompanyReport.objects.get(no=self.noNext)
            except CompanyReport.DoesNotExist:
                pass
        return related



class ClientReport(models.Model):
    """고객계약보고(ClientReport) 모델"""

    # 확인 상태 선택지
    CHECK_CHOICES = [
        (0, '미확인'),
        (1, '불필요'),
        (2, '계약O'),
        (3, '계약X'),
    ]

    # 기본 정보 - ID
    no = models.AutoField(primary_key=True, verbose_name='고객계약보고ID')

    # 구글 시트 원본 텍스트 필드들
    sTimeStamp = models.CharField(max_length=50, blank=True, verbose_name='타임스탬프(구글)')
    sCompanyName = models.CharField(max_length=200, blank=True, verbose_name='업체명(구글)')
    sName = models.CharField(max_length=50, blank=True, verbose_name='고객')
    sArea = models.CharField(max_length=200, blank=True, verbose_name='공사지역')
    sPhone = models.CharField(max_length=50, blank=True, verbose_name='고객핸드폰')
    sConMoney = models.CharField(max_length=50, blank=True, verbose_name='공사금액(원)')
    sDateContract = models.CharField(max_length=50, blank=True, verbose_name='공사계약일(구글)')
    sFile = models.TextField(blank=True, verbose_name='계약서 링크')
    sClientMemo = models.TextField(blank=True, verbose_name='남긴 말씀')

    # 변환된 필드들
    timeStamp = models.DateTimeField(null=True, blank=True, verbose_name='타임스탬프')
    noCompany = models.IntegerField(default=0, verbose_name='업체ID')
    dateContract = models.DateField(null=True, blank=True, verbose_name='공사계약일')

    # 추가 링크 및 관련 ID
    sPost = models.CharField(max_length=200, blank=True, verbose_name='게시글 링크')
    noAssign = models.IntegerField(null=True, blank=True, verbose_name='할당ID')
    noCompanyReport = models.IntegerField(null=True, blank=True, verbose_name='업체계약보고ID')

    # 확인 및 처리
    nCheck = models.IntegerField(
        choices=CHECK_CHOICES,
        default=0,
        verbose_name='확인'
    )
    sMemo = models.TextField(blank=True, verbose_name='메모')

    # 소명 관련
    dateExplain0 = models.DateField(null=True, blank=True, verbose_name='소명요청 예정일')
    dateExplain1 = models.DateField(null=True, blank=True, verbose_name='소명요청 실제일')
    sExplain = models.TextField(blank=True, verbose_name='소명 내용')
    sPunish = models.TextField(blank=True, verbose_name='징계 내용')

    # 자동 생성 필드
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일시')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일시')

    class Meta:
        db_table = 'client_report'
        verbose_name = '고객계약보고'
        verbose_name_plural = '고객계약보고'
        ordering = ['-no']  # 최신순 정렬

    def __str__(self):
        return f"고객보고 {self.no} - {self.sName} ({self.sCompanyName})"

    def get_company_name(self):
        """연결된 업체명 반환"""
        try:
            from company.models import Company
            company = Company.objects.get(no=self.noCompany)
            return company.sCompanyName or f"업체{self.noCompany}"
        except:
            return self.sCompanyName or f"업체{self.noCompany}"

    def get_check_status_color(self):
        """확인 상태에 따른 색상 반환"""
        status_colors = {
            0: ('미확인', 'warning'),     # 노란색
            1: ('불필요', 'secondary'),   # 회색
            2: ('계약O', 'success'),     # 초록색
            3: ('계약X', 'danger'),      # 빨간색
        }
        status, color = status_colors.get(self.nCheck, ('미확인', 'warning'))
        return {'status': status, 'color': color}

    def has_punishment(self):
        """징계 여부 확인"""
        return bool(self.sPunish.strip()) if self.sPunish else False

    def has_explanation(self):
        """소명 여부 확인"""
        return bool(self.sExplain.strip()) if self.sExplain else False

    def is_confirmed_contract(self):
        """계약 확정 여부 확인 (계약O 상태)"""
        return self.nCheck == 2

    def needs_review(self):
        """검토 필요 여부 (미확인 상태)"""
        return self.nCheck == 0

    def get_report_summary(self):
        """보고서 요약 정보"""
        return {
            'company_name': self.get_company_name(),
            'client_name': self.sName,
            'area': self.sArea,
            'contract_money': self.sConMoney,
            'check_status': self.get_nCheck_display(),
            'has_explanation': self.has_explanation(),
            'has_punishment': self.has_punishment(),
            'report_date': self.timeStamp.date() if self.timeStamp else None
        }

    def get_status_display(self):
        """보고서 상태 표시"""
        if self.has_punishment():
            return "징계"
        elif self.has_explanation():
            return "소명"
        elif self.is_confirmed_contract():
            return "계약확정"
        elif self.nCheck == 3:
            return "계약취소"
        elif self.nCheck == 1:
            return "불필요"
        else:
            return "미확인"

    def get_phone_masked(self):
        """전화번호 마스킹 처리"""
        if not self.sPhone:
            return ""

        phone = self.sPhone.replace("-", "").replace(" ", "")
        if len(phone) >= 8:
            return f"{phone[:3]}-****-{phone[-4:]}"
        return self.sPhone

    def get_formatted_timestamp(self):
        """타임스탬프를 250925 형식으로 반환"""
        if self.timeStamp:
            return self.timeStamp.strftime('%y%m%d')
        elif self.sTimeStamp:
            # sTimeStamp 문자열 파싱 시도
            try:
                from datetime import datetime
                import re

                # 한국어 날짜 형식 처리 (예: "2025. 9. 28 오후 6:50:46")
                if '. ' in self.sTimeStamp:
                    # 날짜 부분만 추출
                    date_match = re.match(r'(\d{4})\.\s*(\d{1,2})\.\s*(\d{1,2})', self.sTimeStamp)
                    if date_match:
                        year = int(date_match.group(1))
                        month = int(date_match.group(2))
                        day = int(date_match.group(3))
                        return f"{year%100:02d}{month:02d}{day:02d}"

                # 다른 형식들 시도
                for fmt in ['%Y-%m-%d %H:%M:%S', '%Y/%m/%d %H:%M:%S', '%m/%d/%Y %H:%M:%S',
                           '%Y년 %m월 %d일 %H시 %M분 %S초', '%Y년 %m월 %d일']:
                    try:
                        dt = datetime.strptime(self.sTimeStamp.split()[0] if ' ' in self.sTimeStamp else self.sTimeStamp, fmt.split()[0])
                        return dt.strftime('%y%m%d')
                    except:
                        continue
            except:
                pass
        return "-"

    def get_formatted_contract_date(self):
        """계약일을 250925 형식으로 반환"""
        if self.dateContract:
            return self.dateContract.strftime('%y%m%d')
        elif self.sDateContract:
            # sDateContract 문자열 파싱 시도
            try:
                from datetime import datetime
                import re

                # 한국어 날짜 형식 처리 (예: "2025. 9. 28")
                if '. ' in self.sDateContract:
                    date_match = re.match(r'(\d{4})\.\s*(\d{1,2})\.\s*(\d{1,2})', self.sDateContract)
                    if date_match:
                        year = int(date_match.group(1))
                        month = int(date_match.group(2))
                        day = int(date_match.group(3))
                        return f"{year%100:02d}{month:02d}{day:02d}"

                # 다른 형식들 시도
                for fmt in ['%Y-%m-%d', '%Y/%m/%d', '%m/%d/%Y', '%Y년 %m월 %d일']:
                    try:
                        dt = datetime.strptime(self.sDateContract, fmt)
                        return dt.strftime('%y%m%d')
                    except:
                        continue
            except:
                pass
        return "-"

    def get_company_report(self):
        """연결된 업체계약보고 반환"""
        if not self.noCompanyReport:
            return None
        try:
            return CompanyReport.objects.get(no=self.noCompanyReport)
        except CompanyReport.DoesNotExist:
            return None

    def get_assign(self):
        """연결된 할당 정보 반환"""
        if not self.noAssign:
            return None
        try:
            from order.models import Assign
            return Assign.objects.get(no=self.noAssign)
        except:
            return None

    def get_explain_days_remaining(self):
        """소명요청 예정일까지 남은 일수"""
        if not self.dateExplain0:
            return None
        today = timezone.localtime().date()
        diff_days = (self.dateExplain0 - today).days
        return diff_days

    def is_explain_overdue(self):
        """소명요청 기한 초과 여부"""
        if not self.dateExplain0:
            return False
        if self.dateExplain1:  # 이미 소명요청 완료
            return False
        today = timezone.localtime().date()
        return self.dateExplain0 < today
