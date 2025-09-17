#!/usr/bin/env python
"""
네이버 이메일 ID 기준으로 사용자 이메일 업데이트 스크립트
"""
import os
import sys
import django

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testpark_project.settings')
django.setup()

from accounts.models import CustomUser

def update_naver_emails():
    """네이버 이메일 ID 기준으로 사용자 이메일 업데이트"""

    # 네이버 이메일 ID 목록 (사용자 제공)
    naver_email_mapping = {
        'nuloonggee': 'nuloonggee@naver.com',
        '7171man': '7171man@naver.com',
        'pcarpenter1': 'pcarpenter1@naver.com',
        '7171duman': '7171duman@naver.com',
        'parkrady1004': 'parkrady1004@naver.com',
        'parkgeehyung': 'parkgeehyung@naver.com',
        'pcarpenter2': 'pcarpenter2@naver.com',
        'pcarpenter3': 'pcarpenter3@naver.com',  # 하성달(luke) 사용자
        'ekwak1004': 'ekwak1004@naver.com'
    }

    # 기존 사용자 username과 새 이메일 매핑
    user_email_updates = {
        'nuloonggee': 'nuloonggee@naver.com',
        '7171man': '7171man@naver.com',
        'pcarpenter1': 'pcarpenter1@naver.com',
        '7171duman': '7171duman@naver.com',
        'parkrady1004': 'parkrady1004@naver.com',
        'parkgeehyung': 'parkgeehyung@naver.com',
        'pcarpenter2': 'pcarpenter2@naver.com',
        'luke': 'pcarpenter3@naver.com',  # luke -> pcarpenter3@naver.com
        'ekwak1004': 'ekwak1004@naver.com'
    }

    updated_users = []

    for username, new_email in user_email_updates.items():
        try:
            user = CustomUser.objects.get(username=username)
            old_email = user.email
            user.email = new_email
            user.save()

            print(f"✅ {username}: {old_email} → {new_email}")
            updated_users.append(user)

        except CustomUser.DoesNotExist:
            print(f"❌ 사용자 '{username}'를 찾을 수 없습니다.")
        except Exception as e:
            print(f"❌ {username} 업데이트 실패: {e}")

    return updated_users

def verify_naver_email_mapping():
    """네이버 이메일 매핑 확인"""
    print("\n📧 현재 네이버 이메일 매핑 상황:")

    naver_emails = [
        'nuloonggee@naver.com',
        '7171man@naver.com',
        'pcarpenter1@naver.com',
        '7171duman@naver.com',
        'parkrady1004@naver.com',
        'parkgeehyung@naver.com',
        'pcarpenter2@naver.com',
        'pcarpenter3@naver.com',
        'ekwak1004@naver.com'
    ]

    print(f"예상 네이버 이메일 총 {len(naver_emails)}개:")
    for email in naver_emails:
        print(f"  - {email}")

    print(f"\nDB에 등록된 해당 이메일 사용자:")
    for email in naver_emails:
        try:
            user = CustomUser.objects.get(email=email)
            print(f"  ✅ {email} → {user.name} ({user.username})")
        except CustomUser.DoesNotExist:
            print(f"  ❌ {email} → 사용자 없음")

def main():
    print("🔄 네이버 이메일 ID 기준 사용자 이메일 업데이트...")

    # 1. 기존 사용자 이메일 업데이트
    print("\n1. 사용자 이메일 업데이트 중...")
    updated_users = update_naver_emails()

    print(f"\n✅ {len(updated_users)}명의 사용자 이메일 업데이트 완료")

    # 2. 네이버 이메일 매핑 확인
    print("\n2. 네이버 이메일 매핑 검증...")
    verify_naver_email_mapping()

    # 3. 전체 사용자 목록 출력
    print("\n3. 전체 사용자 목록:")
    users = CustomUser.objects.all().order_by('username')
    for user in users:
        status = []
        if user.is_superuser:
            status.append("슈퍼유저")
        if user.is_staff:
            status.append("스태프")
        status_text = ", ".join(status) if status else "일반유저"

        print(f"  - {user.username} ({user.name}) - {user.email} [{status_text}]")

    print(f"\n🎉 네이버 로그인 테스트 준비 완료!")
    print("\n테스트 가능한 네이버 이메일:")
    print("  - 7171man@naver.com (카페지기)")
    print("  - pcarpenter3@naver.com (하성달/luke)")

if __name__ == '__main__':
    main()