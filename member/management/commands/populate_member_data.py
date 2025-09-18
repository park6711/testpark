from django.core.management.base import BaseCommand
from member.models import Member


class Command(BaseCommand):
    help = '회원 샘플 데이터를 생성합니다'

    def handle(self, *args, **options):
        # 기존 데이터 삭제
        Member.objects.all().delete()

        # 샘플 회원 데이터
        members_data = [
            {
                'sNaverID0': 'naverid1',
                'bApproval': True,
                'sNaverID': 'company1@naver.com',
                'sCompanyName': '삼성건설',
                'sName2': '김대표',
                'noCompany': 1001,
                'sName': '김철수',
                'sPhone': '010-1234-5678',
                'nCafeGrade': 4,  # 연합회
                'nNick': '철수',
                'bMaster': True,
                'nCompanyAuthority': 2,
                'nOrderAuthority': 2,
                'nContractAuthority': 2,
                'nEvaluationAuthority': 2,
            },
            {
                'sNaverID0': 'naverid2',
                'bApproval': True,
                'sNaverID': 'company2@naver.com',
                'sCompanyName': 'LG건설',
                'sName2': '박대표',
                'noCompany': 1002,
                'sName': '박영희',
                'sPhone': '010-2345-6789',
                'nCafeGrade': 3,  # 토탈열린
                'nNick': '영희',
                'bMaster': False,
                'nCompanyAuthority': 1,
                'nOrderAuthority': 1,
                'nContractAuthority': 1,
                'nEvaluationAuthority': 0,
            },
            {
                'sNaverID0': 'naverid3',
                'bApproval': False,
                'sNaverID': 'company3@naver.com',
                'sCompanyName': '현대건설',
                'sName2': '이대표',
                'noCompany': 1003,
                'sName': '이민수',
                'sPhone': '010-3456-7890',
                'nCafeGrade': 2,  # 단종열린
                'nNick': '민수',
                'bMaster': False,
                'nCompanyAuthority': 0,
                'nOrderAuthority': 0,
                'nContractAuthority': 0,
                'nEvaluationAuthority': 0,
            },
            {
                'sNaverID0': 'naverid4',
                'bApproval': True,
                'sNaverID': 'company4@naver.com',
                'sCompanyName': '대우건설',
                'sName2': '정대표',
                'noCompany': 1004,
                'sName': '정수진',
                'sPhone': '010-4567-8901',
                'nCafeGrade': 1,  # 광고제휴
                'nNick': '수진',
                'bMaster': False,
                'nCompanyAuthority': 2,
                'nOrderAuthority': 1,
                'nContractAuthority': 1,
                'nEvaluationAuthority': 1,
            },
            {
                'sNaverID0': 'naverid5',
                'bApproval': True,
                'sNaverID': 'company5@naver.com',
                'sCompanyName': 'GS건설',
                'sName2': '최대표',
                'noCompany': 1005,
                'sName': '최동혁',
                'sPhone': '010-5678-9012',
                'nCafeGrade': 0,  # 일반
                'nNick': '동혁',
                'bMaster': False,
                'nCompanyAuthority': 1,
                'nOrderAuthority': 2,
                'nContractAuthority': 0,
                'nEvaluationAuthority': 1,
            },
        ]

        # 회원 데이터 생성
        for member_data in members_data:
            member = Member.objects.create(**member_data)
            self.stdout.write(
                self.style.SUCCESS(f'회원 생성: {member.sName} ({member.sCompanyName})')
            )

        self.stdout.write(
            self.style.SUCCESS(f'총 {len(members_data)}명의 회원 데이터가 생성되었습니다.')
        )