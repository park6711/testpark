"""
TestPark 프로젝트 전역 유틸리티 함수
모든 앱에서 공통으로 사용하는 헬퍼 함수
"""

from datetime import datetime, timedelta
from typing import Optional, Any
from django.utils import timezone
from .constants import URGENCY_THRESHOLD_DAYS, DATE_FORMATS


def format_date(date: Optional[datetime], format_type: str = 'DATE') -> str:
    """
    날짜 포맷팅

    Args:
        date: datetime 객체
        format_type: DATE_FORMATS에 정의된 포맷 타입

    Returns:
        포맷팅된 날짜 문자열
    """
    if not date:
        return '-'

    format_string = DATE_FORMATS.get(format_type, DATE_FORMATS['DATE'])
    return date.strftime(format_string)


def format_phone(phone: Optional[str]) -> str:
    """
    전화번호 포맷팅 (010-1234-5678)

    Args:
        phone: 전화번호 문자열

    Returns:
        포맷팅된 전화번호
    """
    if not phone:
        return '-'

    # 숫자만 추출
    digits = ''.join(filter(str.isdigit, phone))

    # 길이에 따라 포맷팅
    if len(digits) == 11:
        return f"{digits[:3]}-{digits[3:7]}-{digits[7:]}"
    elif len(digits) == 10:
        return f"{digits[:3]}-{digits[3:6]}-{digits[6:]}"
    else:
        return phone


def is_urgent(scheduled_date: Optional[datetime],
               threshold_days: int = URGENCY_THRESHOLD_DAYS) -> bool:
    """
    일정이 긴급한지 체크 (기본 3일 이내)

    Args:
        scheduled_date: 예정일
        threshold_days: 긴급 임계값 (일)

    Returns:
        긴급 여부
    """
    if not scheduled_date:
        return False

    now = timezone.now()
    diff = scheduled_date - now

    return 0 <= diff.days <= threshold_days


def get_status_badge_class(status: str) -> str:
    """
    상태에 맞는 CSS 클래스 반환

    Args:
        status: 상태 문자열

    Returns:
        Bootstrap badge 클래스
    """
    from .constants import STATUS_BADGE_MAP

    badge_type = STATUS_BADGE_MAP.get(status, 'secondary')
    return f'badge bg-{badge_type}'


def paginate_queryset(queryset, page: int = 1, page_size: int = 20):
    """
    QuerySet 페이지네이션

    Args:
        queryset: Django QuerySet
        page: 페이지 번호 (1부터 시작)
        page_size: 페이지당 항목 수

    Returns:
        페이지네이션된 QuerySet과 메타 정보
    """
    from django.core.paginator import Paginator, EmptyPage

    paginator = Paginator(queryset, page_size)

    try:
        page_obj = paginator.page(page)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    return {
        'results': list(page_obj),
        'pagination': {
            'current_page': page_obj.number,
            'total_pages': paginator.num_pages,
            'total_items': paginator.count,
            'page_size': page_size,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
        }
    }


def safe_int(value: Any, default: int = 0) -> int:
    """
    안전한 정수 변환

    Args:
        value: 변환할 값
        default: 변환 실패 시 기본값

    Returns:
        정수 값
    """
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def safe_bool(value: Any, default: bool = False) -> bool:
    """
    안전한 불리언 변환

    Args:
        value: 변환할 값
        default: 변환 실패 시 기본값

    Returns:
        불리언 값
    """
    if isinstance(value, bool):
        return value

    if isinstance(value, str):
        return value.lower() in ('true', '1', 'yes', 'on')

    return bool(value) if value is not None else default


def truncate_string(text: Optional[str], length: int = 50,
                     suffix: str = '...') -> str:
    """
    문자열 자르기

    Args:
        text: 원본 문자열
        length: 최대 길이
        suffix: 말줄임 표시

    Returns:
        자른 문자열
    """
    if not text:
        return ''

    if len(text) <= length:
        return text

    return text[:length - len(suffix)] + suffix


def get_client_ip(request) -> str:
    """
    클라이언트 IP 주소 가져오기

    Args:
        request: Django request 객체

    Returns:
        IP 주소
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def dict_to_query_string(params: dict) -> str:
    """
    딕셔너리를 쿼리 스트링으로 변환

    Args:
        params: 파라미터 딕셔너리

    Returns:
        쿼리 스트링
    """
    from urllib.parse import urlencode

    # None 값 제거
    filtered_params = {k: v for k, v in params.items() if v is not None}

    return urlencode(filtered_params)
