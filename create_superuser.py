#!/usr/bin/env python
"""
슈퍼유저 및 Staff 데이터 생성 스크립트
"""
import os
import sys
import django

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testpark_project.settings')
django.setup()

from accounts.models import CustomUser

def create_superuser():
    """슈퍼유저 생성"""
    try:
        # 기존 luke 사용자가 있는지 확인
        existing_user = CustomUser.objects.filter(username='luke').first()
        if existing_user:
            print("기존 luke 사용자를 삭제합니다.")
            existing_user.delete()

        # 새 슈퍼유저 생성
        superuser = CustomUser.objects.create_superuser(
            username='luke',
            email='pcarpenter0011@gmail.com',
            password='1024',
            name='하성달',
            phone='010-3377-8624',
            department='기획팀',
            position='과장'
        )

        print(f"✅ 슈퍼유저 생성 완료: {superuser.username} ({superuser.email})")
        return True

    except Exception as e:
        print(f"❌ 슈퍼유저 생성 실패: {e}")
        return False

def create_staff_users():
    """Staff 데이터 생성"""
    staff_data = [
        {
            'username': 'nuloonggee',
            'email': 'nuloonggee@naver.com',
            'name': '박세욱',
            'department': '임원',
            'position': '대표이사',
            'phone': '010-4797-0947',
            'is_staff': True,
            'is_superuser': True,
        },
        {
            'username': '7171man',
            'email': '7171man@naver.com',
            'name': '카페지기',
            'department': '',
            'position': '',
            'phone': '010-6711-8624',
            'is_staff': False,
            'is_superuser': False,
        },
        {
            'username': 'pcarpenter1',
            'email': 'pcarpenter1@naver.com',
            'name': '곽은주',
            'department': '기획팀',
            'position': '팀장',
            'phone': '010-9211-8624',
            'is_staff': True,
            'is_superuser': False,
        },
        {
            'username': '7171duman',
            'email': '7171duman@naver.com',
            'name': '강명순',
            'department': '회계팀',
            'position': '차장',
            'phone': '010-3011-8624',
            'is_staff': True,
            'is_superuser': False,
        },
        {
            'username': 'parkrady1004',
            'email': 'parkrady1004@naver.com',
            'name': '이승엽',
            'department': '기획팀',
            'position': '차장',
            'phone': '010-4476-8624',
            'is_staff': True,
            'is_superuser': False,
        },
        {
            'username': 'parkgeehyung',
            'email': 'parkgeehyung@naver.com',
            'name': '장향숙',
            'department': '업무팀',
            'position': '과장',
            'phone': '010-5011-8624',
            'is_staff': True,
            'is_superuser': False,
        },
        {
            'username': 'pcarpenter2',
            'email': 'pcarpenter2@naver.com',
            'name': '성경희',
            'department': '닷컴팀',
            'position': '차장',
            'phone': '010-4211-8624',
            'is_staff': True,
            'is_superuser': False,
        },
        {
            'username': 'ekwak1004',
            'email': 'ekwak1004@naver.com',
            'name': '권지은',
            'department': '업무팀',
            'position': '대리',
            'phone': '010-3521-4391',
            'is_staff': True,
            'is_superuser': False,
        },
    ]

    created_users = []

    for data in staff_data:
        try:
            # 기존 사용자가 있는지 확인
            existing_user = CustomUser.objects.filter(
                username=data['username']
            ).first()

            if existing_user:
                print(f"기존 사용자 업데이트: {data['username']}")
                for key, value in data.items():
                    if key != 'username':  # username은 변경하지 않음
                        setattr(existing_user, key, value)
                existing_user.set_password('1024')  # 기본 비밀번호 설정
                existing_user.save()
                created_users.append(existing_user)
            else:
                print(f"새 사용자 생성: {data['username']}")
                user = CustomUser.objects.create_user(
                    password='1024',  # 기본 비밀번호
                    **data
                )
                created_users.append(user)

        except Exception as e:
            print(f"❌ 사용자 {data['username']} 생성/업데이트 실패: {e}")

    print(f"✅ {len(created_users)}명의 사용자 처리 완료")
    return created_users

def main():
    print("🚀 슈퍼유저 및 Staff 데이터 생성 시작...")

    # 1. 슈퍼유저 생성
    print("\n1. 슈퍼유저 생성 중...")
    create_superuser()

    # 2. Staff 사용자들 생성
    print("\n2. Staff 사용자들 생성 중...")
    create_staff_users()

    # 3. 생성된 사용자 목록 출력
    print("\n3. 생성된 사용자 목록:")
    users = CustomUser.objects.all().order_by('id')
    for user in users:
        status = []
        if user.is_superuser:
            status.append("슈퍼유저")
        if user.is_staff:
            status.append("스태프")
        status_text = ", ".join(status) if status else "일반유저"

        print(f"  - {user.username} ({user.name}) - {user.email} [{status_text}]")

    print(f"\n🎉 총 {users.count()}명의 사용자가 등록되었습니다!")
    print("\n로그인 테스트를 위해 다음 계정들을 사용하세요:")
    print("  - luke/1024 (슈퍼유저)")
    print("  - 7171man/1024 (일반유저, 네이버 ID: 7171man@naver.com)")

if __name__ == '__main__':
    main()