#!/usr/bin/env python
"""
Template 테스트 데이터 생성 스크립트
기존 Template 데이터를 삭제하고 30개의 새로운 테스트 데이터를 생성합니다.
"""

import os
import sys
import django
from datetime import datetime
import random

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testpark_project.settings')
django.setup()

from template.models import Template

def delete_existing_templates():
    """기존 Template 데이터 삭제"""
    print("기존 Template 데이터 삭제 중...")
    deleted_count = Template.objects.all().count()
    Template.objects.all().delete()
    print(f"✅ {deleted_count}개의 기존 Template 데이터가 삭제되었습니다.")

def create_test_templates():
    """30개의 테스트 Template 데이터 생성"""
    print("새로운 Template 테스트 데이터 생성 중...")

    # 템플릿 내용 샘플
    template_data = [
        # 기타 (nType=0)
        {
            'nType': 0, 'nReceiver': 0,
            'sTitle': '기타 공지사항',
            'sContent': '안녕하세요. 중요한 공지사항이 있어 연락드립니다. 자세한 내용은 첨부파일을 확인해주세요.',
            'nUse': random.randint(0, 15)
        },
        {
            'nType': 0, 'nReceiver': 1,
            'sTitle': '업체 일반 안내',
            'sContent': '{업체명} 관계자님께 안내드립니다. 시스템 점검으로 인해 {날짜} {시간}에 일시적으로 서비스가 중단됩니다.',
            'nUse': random.randint(0, 20)
        },
        {
            'nType': 0, 'nReceiver': 2,
            'sTitle': '고객 안내문',
            'sContent': '{고객명}님, 안녕하세요. 서비스 이용에 감사드리며, 새로운 소식을 전해드립니다.',
            'nUse': random.randint(0, 10)
        },

        # 문자 (nType=1)
        {
            'nType': 1, 'nReceiver': 0,
            'sTitle': '문자 발송 테스트',
            'sContent': '[테스트] 문자 발송 기능을 확인합니다. 수신확인 부탁드립니다.',
            'nUse': random.randint(5, 25)
        },
        {
            'nType': 1, 'nReceiver': 1,
            'sTitle': '업체 문자 알림',
            'sContent': '[{업체명}] 새로운 의뢰가 접수되었습니다. 확인 부탁드립니다. 문의: {전화번호}',
            'nUse': random.randint(10, 50)
        },
        {
            'nType': 1, 'nReceiver': 2,
            'sTitle': '고객 문자 알림',
            'sContent': '{고객명}님, 작업이 완료되었습니다. 확인 후 평가 부탁드립니다. 담당: {담당자}',
            'nUse': random.randint(15, 40)
        },
        {
            'nType': 1, 'nReceiver': 1,
            'sTitle': '긴급 업체 연락',
            'sContent': '[긴급] {업체명} 관계자님, 즉시 연락 부탁드립니다. 담당자: {담당자} / 연락처: {전화번호}',
            'nUse': random.randint(20, 60)
        },
        {
            'nType': 1, 'nReceiver': 2,
            'sTitle': '일정 변경 안내',
            'sContent': '{고객명}님, 예정된 {날짜} 작업 일정이 변경되었습니다. 새 일정: {시간}',
            'nUse': random.randint(8, 30)
        },

        # 의뢰할당 (nType=2)
        {
            'nType': 2, 'nReceiver': 1,
            'sTitle': '의뢰 할당 통보',
            'sContent': '{업체명}님께 새로운 의뢰가 할당되었습니다. 의뢰번호: {계약번호}, 고객: {고객명}, 주소: {주소}',
            'nUse': random.randint(25, 80)
        },
        {
            'nType': 2, 'nReceiver': 1,
            'sTitle': '할당 취소 안내',
            'sContent': '{업체명}님, 할당된 의뢰({계약번호})가 취소되었습니다. 사유: 고객 사정으로 인한 취소',
            'nUse': random.randint(5, 20)
        },
        {
            'nType': 2, 'nReceiver': 1,
            'sTitle': '긴급 의뢰 할당',
            'sContent': '[긴급] {업체명}님, 긴급 의뢰가 할당되었습니다. 24시간 내 연락 필수. 고객: {고객명} / {전화번호}',
            'nUse': random.randint(15, 45)
        },
        {
            'nType': 2, 'nReceiver': 2,
            'sTitle': '업체 배정 완료',
            'sContent': '{고객명}님, 요청하신 서비스에 {업체명}이 배정되었습니다. 담당자가 곧 연락드리겠습니다.',
            'nUse': random.randint(30, 70)
        },
        {
            'nType': 2, 'nReceiver': 1,
            'sTitle': '재할당 안내',
            'sContent': '{업체명}님, 기존 할당 업체의 사정으로 재할당되었습니다. 의뢰번호: {계약번호}, 작업예정일: {날짜}',
            'nUse': random.randint(10, 35)
        },

        # 업체관리 (nType=3)
        {
            'nType': 3, 'nReceiver': 1,
            'sTitle': '업체 등록 승인',
            'sContent': '{업체명}님의 업체 등록이 승인되었습니다. 시스템 접속 후 상세 정보를 확인해주세요.',
            'nUse': random.randint(5, 15)
        },
        {
            'nType': 3, 'nReceiver': 1,
            'sTitle': '서류 제출 요청',
            'sContent': '{업체명}님, 사업자등록증 갱신 서류 제출이 필요합니다. 마감일: {날짜}',
            'nUse': random.randint(10, 30)
        },
        {
            'nType': 3, 'nReceiver': 1,
            'sTitle': '업체 정보 업데이트',
            'sContent': '{업체명}님, 업체 정보 업데이트가 완료되었습니다. 변경사항을 확인해주세요.',
            'nUse': random.randint(8, 25)
        },
        {
            'nType': 3, 'nReceiver': 1,
            'sTitle': '활동 중지 해제',
            'sContent': '{업체명}님의 활동 중지가 해제되었습니다. 의뢰 수주가 가능합니다.',
            'nUse': random.randint(3, 12)
        },
        {
            'nType': 3, 'nReceiver': 1,
            'sTitle': '업체 교육 안내',
            'sContent': '{업체명}님, {날짜}에 업체 교육이 예정되어 있습니다. 참석 여부를 알려주세요.',
            'nUse': random.randint(15, 40)
        },

        # 업체평가 (nType=4)
        {
            'nType': 4, 'nReceiver': 1,
            'sTitle': '평가 결과 통보',
            'sContent': '{업체명}님의 이번 분기 평가 결과를 안내드립니다. 상세 내용은 시스템에서 확인 가능합니다.',
            'nUse': random.randint(20, 50)
        },
        {
            'nType': 4, 'nReceiver': 1,
            'sTitle': '평가 개선 요청',
            'sContent': '{업체명}님, 고객 만족도 향상을 위한 개선사항이 있습니다. 담당자: {담당자}',
            'nUse': random.randint(12, 35)
        },
        {
            'nType': 4, 'nReceiver': 2,
            'sTitle': '고객 평가 요청',
            'sContent': '{고객명}님, 서비스 이용에 대한 평가를 부탁드립니다. 평가 링크: http://example.com/evaluate',
            'nUse': random.randint(40, 90)
        },
        {
            'nType': 4, 'nReceiver': 1,
            'sTitle': '우수 업체 선정',
            'sContent': '축하합니다! {업체명}님이 이번 분기 우수 업체로 선정되었습니다. 인센티브가 지급됩니다.',
            'nUse': random.randint(5, 18)
        },
        {
            'nType': 4, 'nReceiver': 1,
            'sTitle': '평가 설문 참여',
            'sContent': '{업체명}님, 시스템 개선을 위한 설문조사에 참여해주세요. 소요시간: 5분',
            'nUse': random.randint(18, 45)
        },

        # 계약회계 (nType=5)
        {
            'nType': 5, 'nReceiver': 1,
            'sTitle': '정산 완료 안내',
            'sContent': '{업체명}님, {날짜} 정산이 완료되었습니다. 입금 예정일: {시간}',
            'nUse': random.randint(30, 70)
        },
        {
            'nType': 5, 'nReceiver': 1,
            'sTitle': '계약서 갱신',
            'sContent': '{업체명}님, 계약 갱신 시기입니다. 새 계약서를 확인하고 서명해주세요.',
            'nUse': random.randint(8, 25)
        },
        {
            'nType': 5, 'nReceiver': 2,
            'sTitle': '결제 확인',
            'sContent': '{고객명}님, 서비스 이용료 {금액}원이 결제되었습니다. 영수증은 이메일로 발송됩니다.',
            'nUse': random.randint(50, 100)
        },
        {
            'nType': 5, 'nReceiver': 1,
            'sTitle': '세금계산서 발행',
            'sContent': '{업체명}님, 세금계산서가 발행되었습니다. 이메일을 확인해주세요.',
            'nUse': random.randint(25, 60)
        },
        {
            'nType': 5, 'nReceiver': 1,
            'sTitle': '수수료 정산',
            'sContent': '{업체명}님의 {날짜} 수수료 정산 내역입니다. 총 금액: {금액}원',
            'nUse': random.randint(20, 55)
        },
        {
            'nType': 5, 'nReceiver': 2,
            'sTitle': '환불 처리',
            'sContent': '{고객명}님, 요청하신 환불이 처리되었습니다. 환불액: {금액}원, 처리일: {날짜}',
            'nUse': random.randint(10, 30)
        },
        {
            'nType': 5, 'nReceiver': 1,
            'sTitle': '월정산 보고서',
            'sContent': '{업체명}님의 월정산 보고서가 준비되었습니다. 총 수익: {금액}원, 건수: 25건',
            'nUse': random.randint(15, 40)
        }
    ]

    created_count = 0
    for data in template_data:
        template = Template.objects.create(**data)
        created_count += 1
        print(f"  ✓ Template {template.no}: {template.sTitle} (분류: {template.get_nType_display()}, 수신: {template.get_nReceiver_display()}, 사용: {template.nUse}회)")

    print(f"✅ {created_count}개의 새로운 Template 테스트 데이터가 생성되었습니다.")

def main():
    """메인 실행 함수"""
    print("=" * 60)
    print("Template 테스트 데이터 생성 스크립트")
    print("=" * 60)

    # 기존 데이터 삭제
    delete_existing_templates()
    print()

    # 새 데이터 생성
    create_test_templates()
    print()

    # 결과 요약
    total_count = Template.objects.count()
    print("=" * 60)
    print(f"🎉 작업 완료! 총 {total_count}개의 Template이 생성되었습니다.")
    print("=" * 60)

    # 분류별 통계
    print("\n📊 분류별 생성 현황:")
    for choice_value, choice_label in Template.TYPE_CHOICES:
        count = Template.objects.filter(nType=choice_value).count()
        print(f"  {choice_label}: {count}개")

    print("\n📊 수신대상별 생성 현황:")
    for choice_value, choice_label in Template.SORT_CHOICES:
        count = Template.objects.filter(nReceiver=choice_value).count()
        print(f"  {choice_label}: {count}개")

if __name__ == "__main__":
    main()
