"""
TestPark 프로젝트 전역 상수
모든 앱에서 공통으로 사용하는 상수 정의
"""

# 상태 관련 상수
class OrderStatus:
    """의뢰 상태"""
    WAITING = '대기중'
    ASSIGNED = '할당'
    REJECTED = '반려'
    CANCELLED = '취소'
    EXCLUDED = '제외'
    CONTRACTED = '계약'
    COMPANY_INSUFFICIENT = '업체미비'
    DUPLICATE = '중복접수'
    CONTACT_ERROR = '연락처오류'
    INQUIRY_AVAILABLE = '가능문의'
    INQUIRY_UNAVAILABLE = '불가능답변(X)'
    CUSTOMER_INQUIRY = '고객문의'

    CHOICES = [
        (WAITING, '대기중'),
        (ASSIGNED, '할당'),
        (REJECTED, '반려'),
        (CANCELLED, '취소'),
        (EXCLUDED, '제외'),
        (CONTRACTED, '계약'),
        (COMPANY_INSUFFICIENT, '업체미비'),
        (DUPLICATE, '중복접수'),
        (CONTACT_ERROR, '연락처오류'),
        (INQUIRY_AVAILABLE, '가능문의'),
        (INQUIRY_UNAVAILABLE, '불가능답변(X)'),
        (CUSTOMER_INQUIRY, '고객문의'),
    ]


class CompanyStatus:
    """업체 상태"""
    ACTIVE = '활성'
    INACTIVE = '비활성'
    SUSPENDED = '정지'

    CHOICES = [
        (ACTIVE, '활성'),
        (INACTIVE, '비활성'),
        (SUSPENDED, '정지'),
    ]


class DesignationType:
    """지정 유형"""
    NONE = '지정없음'
    DIRECT = '지정'
    GROUP_PURCHASE = '공동구매'

    CHOICES = [
        (NONE, '지정없음'),
        (DIRECT, '지정'),
        (GROUP_PURCHASE, '공동구매'),
    ]


# UI 관련 상수
class BadgeType:
    """배지 타입 (Bootstrap 기반)"""
    PRIMARY = 'primary'
    SECONDARY = 'secondary'
    SUCCESS = 'success'
    DANGER = 'danger'
    WARNING = 'warning'
    INFO = 'info'
    LIGHT = 'light'
    DARK = 'dark'


# 상태별 배지 매핑
STATUS_BADGE_MAP = {
    OrderStatus.WAITING: BadgeType.WARNING,
    OrderStatus.ASSIGNED: BadgeType.SUCCESS,
    OrderStatus.REJECTED: BadgeType.DANGER,
    OrderStatus.CANCELLED: BadgeType.SECONDARY,
    OrderStatus.EXCLUDED: BadgeType.DARK,
    OrderStatus.CONTRACTED: BadgeType.SUCCESS,
    OrderStatus.COMPANY_INSUFFICIENT: BadgeType.INFO,
    OrderStatus.DUPLICATE: BadgeType.WARNING,
    OrderStatus.CONTACT_ERROR: BadgeType.DANGER,
    OrderStatus.INQUIRY_AVAILABLE: BadgeType.INFO,
    OrderStatus.INQUIRY_UNAVAILABLE: BadgeType.SECONDARY,
    OrderStatus.CUSTOMER_INQUIRY: BadgeType.INFO,
}


# 페이지네이션 설정
PAGINATION = {
    'DEFAULT_PAGE_SIZE': 20,
    'MAX_PAGE_SIZE': 100,
    'PAGE_SIZE_OPTIONS': [10, 20, 50, 100],
}


# 날짜/시간 형식
DATE_FORMATS = {
    'DATE': '%Y-%m-%d',
    'DATETIME': '%Y-%m-%d %H:%M',
    'DATETIME_FULL': '%Y-%m-%d %H:%M:%S',
    'TIME': '%H:%M',
}


# API 설정
API_SETTINGS = {
    'VERSION': 'v1',
    'TIMEOUT': 30,  # seconds
    'MAX_RETRIES': 3,
}


# 파일 업로드 설정
UPLOAD_SETTINGS = {
    'MAX_FILE_SIZE': 10 * 1024 * 1024,  # 10MB
    'ALLOWED_EXTENSIONS': ['.jpg', '.jpeg', '.png', '.pdf', '.doc', '.docx'],
    'UPLOAD_PATH': 'uploads/',
}


# 긴급성 임계값 (일)
URGENCY_THRESHOLD_DAYS = 3
