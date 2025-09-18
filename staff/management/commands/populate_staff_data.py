from django.core.management.base import BaseCommand
from staff.models import Staff


class Command(BaseCommand):
    help = '직원 데이터를 데이터베이스에 추가합니다'

    def handle(self, *args, **options):
        # 기존 데이터 삭제
        Staff.objects.all().delete()

        # 권한 매핑
        authority_map = {
            '권한없음': 0,
            '읽기권한': 1,
            '쓰기권한': 2
        }

        master_map = {
            '일반': 0,
            '마스터': 1,
            '슈퍼마스터': 2
        }

        # 직원 데이터
        staff_data = [
            {
                'no': 1,
                'sNaverID0': 'nuloonggee@gmail.com',
                'bApproval': True,
                'sNaverID': 'nuloonggee@gmail.com',
                'sName': '박세욱',
                'sTeam': '임원',
                'sTitle': '대표이사',
                'sNick': '샘',
                'sGoogleID': 'nuloonggee',
                'sPhone1': '010-4797-0947',
                'sPhone2': '010-4797-0947',
                'nMaster': master_map['슈퍼마스터'],
                'nStaffAuthority': authority_map['쓰기권한'],
                'nCompanyAuthority': authority_map['쓰기권한'],
                'nOrderAuthority': authority_map['쓰기권한'],
                'nContractAuthority': authority_map['쓰기권한'],
                'nEvaluationAuthority': authority_map['쓰기권한']
            },
            {
                'no': 2,
                'sNaverID0': '7171man@naver.com',
                'bApproval': False,
                'sNaverID': '7171man@naver.com',
                'sName': '카페지기',
                'sTeam': '',
                'sTitle': '',
                'sNick': '박목수',
                'sGoogleID': '7171duman',
                'sPhone1': '010-6711-8624',
                'sPhone2': '010-6711-8624',
                'nMaster': master_map['일반'],
                'nStaffAuthority': authority_map['읽기권한'],
                'nCompanyAuthority': authority_map['읽기권한'],
                'nOrderAuthority': authority_map['쓰기권한'],
                'nContractAuthority': authority_map['권한없음'],
                'nEvaluationAuthority': authority_map['읽기권한']
            },
            {
                'no': 3,
                'sNaverID0': 'pcarpenter1@naver.com',
                'bApproval': True,
                'sNaverID': 'pcarpenter1@naver.com',
                'sName': '곽은주',
                'sTeam': '기획팀',
                'sTitle': '팀장',
                'sNick': '아네스',
                'sGoogleID': 'pcarpenter0002',
                'sPhone1': '010-9211-8624',
                'sPhone2': '010-9211-8624',
                'nMaster': master_map['마스터'],
                'nStaffAuthority': authority_map['쓰기권한'],
                'nCompanyAuthority': authority_map['쓰기권한'],
                'nOrderAuthority': authority_map['쓰기권한'],
                'nContractAuthority': authority_map['쓰기권한'],
                'nEvaluationAuthority': authority_map['쓰기권한']
            },
            {
                'no': 4,
                'sNaverID0': '7171duman@naver.com',
                'bApproval': True,
                'sNaverID': '7171duman@naver.com',
                'sName': '강명순',
                'sTeam': '회계팀',
                'sTitle': '차장',
                'sNick': '안나',
                'sGoogleID': 'pcarepenter0006',
                'sPhone1': '010-3011-8624',
                'sPhone2': '010-3011-8624',
                'nMaster': master_map['일반'],
                'nStaffAuthority': authority_map['읽기권한'],
                'nCompanyAuthority': authority_map['쓰기권한'],
                'nOrderAuthority': authority_map['쓰기권한'],
                'nContractAuthority': authority_map['쓰기권한'],
                'nEvaluationAuthority': authority_map['쓰기권한']
            },
            {
                'no': 5,
                'sNaverID0': 'parkrady1004@naver.com',
                'bApproval': True,
                'sNaverID': 'parkrady1004@naver.com',
                'sName': '이승엽',
                'sTeam': '기획팀',
                'sTitle': '차장',
                'sNick': '댄',
                'sGoogleID': 'pcarpenter0007',
                'sPhone1': '010-4476-8624',
                'sPhone2': '010-4476-8624',
                'nMaster': master_map['일반'],
                'nStaffAuthority': authority_map['읽기권한'],
                'nCompanyAuthority': authority_map['쓰기권한'],
                'nOrderAuthority': authority_map['쓰기권한'],
                'nContractAuthority': authority_map['읽기권한'],
                'nEvaluationAuthority': authority_map['쓰기권한']
            },
            {
                'no': 6,
                'sNaverID0': 'parkgeehyung@naver.com',
                'bApproval': True,
                'sNaverID': 'parkgeehyung@naver.com',
                'sName': '장향숙',
                'sTeam': '업무팀',
                'sTitle': '과장',
                'sNick': '제니',
                'sGoogleID': 'pcarpenter0003',
                'sPhone1': '010-5011-8624',
                'sPhone2': '010-5011-8624',
                'nMaster': master_map['일반'],
                'nStaffAuthority': authority_map['읽기권한'],
                'nCompanyAuthority': authority_map['쓰기권한'],
                'nOrderAuthority': authority_map['쓰기권한'],
                'nContractAuthority': authority_map['읽기권한'],
                'nEvaluationAuthority': authority_map['쓰기권한']
            },
            {
                'no': 7,
                'sNaverID0': 'pcarpenter2@naver.com',
                'bApproval': True,
                'sNaverID': 'pcarpenter2@naver.com',
                'sName': '성경희',
                'sTeam': '닷컴팀',
                'sTitle': '차장',
                'sNick': '스텔라',
                'sGoogleID': 'pcarpenter0005',
                'sPhone1': '010-4211-8624',
                'sPhone2': '010-4211-8624',
                'nMaster': master_map['일반'],
                'nStaffAuthority': authority_map['읽기권한'],
                'nCompanyAuthority': authority_map['쓰기권한'],
                'nOrderAuthority': authority_map['쓰기권한'],
                'nContractAuthority': authority_map['읽기권한'],
                'nEvaluationAuthority': authority_map['쓰기권한']
            },
            {
                'no': 8,
                'sNaverID0': 'pcarpenter3@naver.com',
                'bApproval': True,
                'sNaverID': 'pcarpenter3@naver.com',
                'sName': '하성달',
                'sTeam': '기획팀',
                'sTitle': '과장',
                'sNick': '루크',
                'sGoogleID': 'pcarpenter0011@gmail.com, 7171man@naver.com',
                'sPhone1': '010-3377-8624',
                'sPhone2': '010-3377-8624',
                'nMaster': master_map['마스터'],
                'nStaffAuthority': authority_map['쓰기권한'],
                'nCompanyAuthority': authority_map['쓰기권한'],
                'nOrderAuthority': authority_map['쓰기권한'],
                'nContractAuthority': authority_map['쓰기권한'],
                'nEvaluationAuthority': authority_map['쓰기권한']
            },
            {
                'no': 9,
                'sNaverID0': 'ekwak1004@naver.com',
                'bApproval': True,
                'sNaverID': 'ekwak1004@naver.com',
                'sName': '권지은',
                'sTeam': '업무팀',
                'sTitle': '대리',
                'sNick': '비비안',
                'sGoogleID': 'pcarpenter0004',
                'sPhone1': '010-3521-4391',
                'sPhone2': '010-3521-4391',
                'nMaster': master_map['일반'],
                'nStaffAuthority': authority_map['읽기권한'],
                'nCompanyAuthority': authority_map['쓰기권한'],
                'nOrderAuthority': authority_map['쓰기권한'],
                'nContractAuthority': authority_map['권한없음'],
                'nEvaluationAuthority': authority_map['읽기권한']
            }
        ]

        # 데이터 생성
        created_count = 0
        for data in staff_data:
            staff = Staff.objects.create(**data)
            created_count += 1
            self.stdout.write(
                self.style.SUCCESS(f'직원 생성 완료: {staff.sName} (ID: {staff.no})')
            )

        self.stdout.write(
            self.style.SUCCESS(f'총 {created_count}명의 직원 데이터가 생성되었습니다.')
        )