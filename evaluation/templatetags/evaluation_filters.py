# evaluation/templatetags/evaluation_filters.py
from django import template
from datetime import datetime
import re

register = template.Library()

@register.filter(name='format_date_short')
def format_date_short(value):
    """
    날짜를 YYMMDD 형식으로 변환
    예: 2025-09-26 -> 250926
        2025-09-26T13:15:22.929Z -> 250926
        2025. 9. 2 -> 250902
        2025/09/26 -> 250926
    """
    if not value or value == '-':
        return '-'

    try:
        # 문자열로 변환
        date_str = str(value)

        # ISO 8601 형식 (2025-09-26T13:15:22.929Z) 처리
        if 'T' in date_str:
            date_str = date_str.split('T')[0]

        # 다양한 구분자 처리 (-, ., /, 공백)
        # 숫자만 추출
        numbers = re.findall(r'\d+', date_str)

        if len(numbers) >= 3:
            # 년, 월, 일 추출
            year = numbers[0]
            month = numbers[1]
            day = numbers[2]

            # 년도가 4자리면 뒤 2자리만 사용
            if len(year) == 4:
                year = year[-2:]
            elif len(year) == 2:
                # 이미 2자리
                pass
            else:
                # 예상치 못한 형식
                return date_str[:10]

            # 월과 일을 2자리로 패딩
            month = month.zfill(2)
            day = day.zfill(2)

            return f"{year}{month}{day}"

        # 날짜 파싱 실패 시 원본의 처음 10자 반환
        return date_str[:10]

    except Exception as e:
        # 변환 실패 시 원본 반환
        return str(value)[:10] if value else '-'