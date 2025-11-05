"""
Order 앱 전용 상수
"""

# Order 앱의 고유 상수들
class AssignStatus:
    """할당 상태"""
    PENDING = '대기'
    SENT = '발송'
    VIEWED = '확인'
    RESPONDED = '응답'
    ACCEPTED = '수락'
    REJECTED = '거절'

    CHOICES = [
        (PENDING, '대기'),
        (SENT, '발송'),
        (VIEWED, '확인'),
        (RESPONDED, '응답'),
        (ACCEPTED, '수락'),
        (REJECTED, '거절'),
    ]


# Order 관련 설정
ORDER_SETTINGS = {
    'AUTO_ASSIGN_ENABLED': True,
    'MAX_ASSIGN_COMPANIES': 10,
    'ASSIGN_TIMEOUT_HOURS': 24,
    'REMINDER_INTERVAL_HOURS': 6,
}


# 견적서 설정
ESTIMATE_SETTINGS = {
    'MAX_ESTIMATES_PER_ORDER': 20,
    'ESTIMATE_VALID_DAYS': 30,
}
