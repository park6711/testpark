"""
Order 앱 전용 유틸리티 함수
"""

from typing import Optional, List
from datetime import datetime
from django.db.models import QuerySet
from testpark_project.utils import is_urgent, format_date


def get_order_display_name(order) -> str:
    """
    의뢰 표시 이름 생성

    Args:
        order: Order 모델 인스턴스

    Returns:
        표시 이름 (예: "홍길동 - 서울 강남")
    """
    name = order.sName or '이름없음'
    area = order.sArea or '지역없음'
    return f"{name} - {area}"


def calculate_assign_priority(order, company) -> int:
    """
    할당 우선순위 계산

    Args:
        order: Order 모델 인스턴스
        company: Company 모델 인스턴스

    Returns:
        우선순위 점수 (높을수록 우선)
    """
    priority = 0

    # 등급별 가중치 (낮은 등급이 높은 점수)
    if company.grade:
        priority += (5 - company.grade) * 10

    # 지역 일치 보너스
    if order.sArea and company.sArea and order.sArea in company.sArea:
        priority += 20

    # 전문 분야 일치 보너스
    if order.sArea and company.specialty and order.sArea in company.specialty:
        priority += 15

    # 할당 횟수 페널티 (많이 받은 업체는 점수 감소)
    priority -= (company.assignCount or 0) * 2

    return priority


def filter_available_companies(companies: QuerySet, order) -> List:
    """
    할당 가능한 업체 필터링

    Args:
        companies: Company QuerySet
        order: Order 모델 인스턴스

    Returns:
        필터링된 업체 리스트
    """
    available = []

    for company in companies:
        # 활성 상태 체크
        if not company.is_active:
            continue

        # 지역 체크 (가능 지역이 설정된 경우)
        if hasattr(company, 'possiblearea_set'):
            possible_areas = [pa.sArea for pa in company.possiblearea_set.all()]
            if possible_areas and order.sArea not in possible_areas:
                continue

        # 불가능 일정 체크
        if hasattr(company, 'impossibleterm_set') and order.dateSchedule:
            impossible_dates = [it.date for it in company.impossibleterm_set.all()]
            if order.dateSchedule.date() in impossible_dates:
                continue

        available.append(company)

    return available


def generate_estimate_summary(estimate) -> str:
    """
    견적서 요약 생성

    Args:
        estimate: Estimate 모델 인스턴스

    Returns:
        요약 문자열
    """
    parts = []

    if estimate.noCompany:
        parts.append(f"업체: {estimate.noCompany.sCompanyName}")

    if estimate.time:
        parts.append(f"등록: {format_date(estimate.time, 'DATETIME')}")

    if estimate.sPost:
        parts.append(f"링크: {estimate.sPost[:50]}...")

    return " | ".join(parts) if parts else "정보 없음"
