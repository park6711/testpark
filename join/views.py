from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import transaction
from company.models import Company, ContractFile
from member.models import Member
from datetime import date


def safe_int(value, default=0):
    """안전한 정수 변환 함수"""
    try:
        if value is None or value == '':
            return default
        return int(value)
    except (ValueError, TypeError):
        return default


def company_registration(request):
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Company 데이터 생성
                company = Company.objects.create(
                    sName1=request.POST.get('sNaverID', ''),  # 열린업체명1에 네이버ID 저장
                    sName2=request.POST.get('sNaverID', ''),  # 열린업체명2에 네이버ID 저장
                    sName3=request.POST.get('sNaverID', ''),  # 열린업체명3에 네이버ID 저장
                    sNaverID=request.POST.get('sNaverID', ''),
                    nType=0,  # 기본값: 일반토탈
                    nCondition=0,  # 기본값: 준비중
                    sCompanyName=request.POST.get('sCompanyName', ''),
                    sAddress=request.POST.get('sAddress', ''),
                    nMember=safe_int(request.POST.get('nMember')),
                    sBuildLicense=request.POST.get('sBuildLicense', ''),
                    fileBuildLicense=request.FILES.get('fileBuildLicense'),
                    sStrength=request.POST.get('sStrength', ''),
                    sCeoName=request.POST.get('sCeoName', ''),
                    sCeoPhone=request.POST.get('sCeoPhone', ''),
                    sCeoMail=request.POST.get('sCeoMail', ''),
                    fileCeo=request.FILES.get('fileCeo'),
                    sSaleName=request.POST.get('sSaleName', ''),
                    sSalePhone=request.POST.get('sSalePhone', ''),
                    sSaleMail=request.POST.get('sSaleMail', ''),
                    fileSale=request.FILES.get('fileSale'),
                    sAccoutName=request.POST.get('sAccoutName', ''),
                    sAccoutPhone=request.POST.get('sAccoutPhone', ''),
                    sAccoutMail=request.POST.get('sAccoutMail', ''),
                    fileLicense=request.FILES.get('fileLicense'),
                    sEmergencyName=request.POST.get('sEmergencyName', ''),
                    sEmergencyPhone=request.POST.get('sEmergencyPhone', ''),
                    sEmergencyRelation=request.POST.get('sEmergencyRelation', ''),
                    dateJoin=date.today(),
                    nJoinFee=0,
                    nDeposit=0,
                    nFixFee=0,
                    fFeePercent=0.0,
                    nOrderFee=0,
                    nReportPeriod=0,
                    fileCampaignAgree=request.FILES.get('fileCampaignAgree'),
                    bPrivacy=request.POST.get('bPrivacy') == 'on',
                    bCompetition=request.POST.get('bCompetition') == 'on',
                    bAptAll=request.POST.get('bAptAll') == 'on',
                    bAptPart=request.POST.get('bAptPart') == 'on',
                    bHouseAll=request.POST.get('bHouseAll') == 'on',
                    bHousePart=request.POST.get('bHousePart') == 'on',
                    bCommerceAll=request.POST.get('bCommerceAll') == 'on',
                    bCommercePart=request.POST.get('bCommercePart') == 'on',
                    bBuild=request.POST.get('bBuild') == 'on',
                    bExtra=False,
                    bUnion=False,
                    bMentor=False,
                    sMentee='',
                    nRefund=0,
                    sManager='',
                    dateWithdraw=None,
                    sWithdraw='',
                    sMemo='가입신청서를 통해 등록됨',
                    sPicture='',
                    sGallery='',
                    sEstimate=''
                )

                # 협약서 파일들 처리
                contract_files = request.FILES.getlist('fileContract')
                for contract_file in contract_files:
                    ContractFile.objects.create(
                        company=company,
                        file=contract_file
                    )

                # Member 데이터 생성
                Member.objects.create(
                    sNaverID0='',  # 식별자는 빈값으로
                    sNaverID=request.POST.get('sNaverID', ''),  # 네이버 ID
                    sCompanyName=request.POST.get('sCompanyName', ''),  # 업체명
                    sName=request.POST.get('sCeoName', ''),  # 대표자 이름
                    sPhone=request.POST.get('sCeoPhone', ''),  # 대표 핸드폰번호
                    noCompany=company.no,  # 자동으로 company 연결
                    nCafeGrade=0,  # 기본값: 일반
                    nNick='',
                    bMaster=True,  # 마스터로 설정 (bMaster=1)
                    bApproval=False,  # 비승인 상태 (bApproval=0)
                    # 나머지 권한은 모두 쓰기권한(2)으로 설정
                    nCompanyAuthority=2,
                    nOrderAuthority=2,
                    nContractAuthority=2,
                    nEvaluationAuthority=2
                )

                messages.success(request, f'가입신청이 완료되었습니다. 업체명: {company.sCompanyName}')
                return redirect('join:registration_success')

        except Exception as e:
            messages.error(request, f'가입신청 중 오류가 발생했습니다: {str(e)}')
            return render(request, 'join/company_registration.html')

    return render(request, 'join/company_registration.html')


def registration_success(request):
    return render(request, 'join/registration_success.html')


def btoc_registration(request):
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Company 데이터 생성 (nType=4: btoc제휴)
                company = Company.objects.create(
                    sName1=request.POST.get('sNaverID', ''),  # 열린업체명1에 네이버ID 저장
                    sName2=request.POST.get('sNaverID', ''),  # 열린업체명2에 네이버ID 저장
                    sName3=request.POST.get('sNaverID', ''),  # 열린업체명3에 네이버ID 저장
                    sNaverID=request.POST.get('sNaverID', ''),
                    nType=4,  # btoc제휴
                    nCondition=0,  # 기본값: 준비중
                    sCompanyName=request.POST.get('sCompanyName', ''),
                    sAddress=request.POST.get('sAddress', ''),
                    nMember=safe_int(request.POST.get('nMember')),
                    sBuildLicense='',  # btoc제휴는 건설면허 불필요
                    fileBuildLicense=None,
                    sStrength=request.POST.get('sStrength', ''),
                    sCeoName=request.POST.get('sCeoName', ''),
                    sCeoPhone=request.POST.get('sCeoPhone', ''),
                    sCeoMail=request.POST.get('sCeoMail', ''),
                    fileCeo=request.FILES.get('fileCeo'),
                    sSaleName=request.POST.get('sSaleName', ''),
                    sSalePhone=request.POST.get('sSalePhone', ''),
                    sSaleMail=request.POST.get('sSaleMail', ''),
                    fileSale=request.FILES.get('fileSale'),
                    sAccoutName=request.POST.get('sAccoutName', ''),
                    sAccoutPhone=request.POST.get('sAccoutPhone', ''),
                    sAccoutMail=request.POST.get('sAccoutMail', ''),
                    fileLicense=request.FILES.get('fileLicense'),
                    sEmergencyName='',  # btoc제휴는 비상연락처 불필요
                    sEmergencyPhone='',
                    sEmergencyRelation='',
                    dateJoin=date.today(),
                    nJoinFee=0,
                    nDeposit=0,
                    nFixFee=0,
                    fFeePercent=0.0,
                    nOrderFee=0,
                    nReportPeriod=0,
                    fileCampaignAgree=None,  # btoc제휴는 캠페인 동의서 불필요
                    bPrivacy=request.POST.get('bPrivacy') == 'on',
                    bCompetition=False,  # btoc제휴는 경업금지 동의 불필요
                    bAptAll=False,
                    bAptPart=False,
                    bHouseAll=False,
                    bHousePart=False,
                    bCommerceAll=False,
                    bCommercePart=False,
                    bBuild=False,
                    bExtra=False,
                    bUnion=False,
                    bMentor=False,
                    sMentee='',
                    nRefund=0,
                    sManager='',
                    dateWithdraw=None,
                    sWithdraw='',
                    sMemo='btoc제휴 가입신청서를 통해 등록됨',
                    sPicture='',
                    sGallery='',
                    sEstimate=''
                )

                # 협약서 파일들 처리
                contract_files = request.FILES.getlist('fileContract')
                for contract_file in contract_files:
                    ContractFile.objects.create(
                        company=company,
                        file=contract_file
                    )

                # Member 데이터 생성
                Member.objects.create(
                    sNaverID0='',  # 식별자는 빈값으로
                    sNaverID=request.POST.get('sNaverID', ''),  # 네이버 ID
                    sCompanyName=request.POST.get('sCompanyName', ''),  # 업체명
                    sName=request.POST.get('sCeoName', ''),  # 대표자 이름
                    sPhone=request.POST.get('sCeoPhone', ''),  # 대표 핸드폰번호
                    noCompany=company.no,  # 자동으로 company 연결
                    nCafeGrade=0,  # 기본값: 일반
                    nNick='',
                    bMaster=True,  # 마스터로 설정 (bMaster=1)
                    bApproval=False,  # 비승인 상태 (bApproval=0)
                    # 기본 권한들을 쓰기권한(2)으로 설정
                    nCompanyAuthority=2,
                    nOrderAuthority=2,
                    nContractAuthority=2,
                    nEvaluationAuthority=2
                )

                messages.success(request, f'btoc제휴 가입신청이 완료되었습니다. 업체명: {company.sCompanyName}')
                return redirect('join:registration_success')

        except Exception as e:
            messages.error(request, f'가입신청 중 오류가 발생했습니다: {str(e)}')
            return render(request, 'join/btoc_registration.html')

    return render(request, 'join/btoc_registration.html')


def btob_registration(request):
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Company 데이터 생성 (nType=5: btob제휴)
                company = Company.objects.create(
                    sName1=request.POST.get('sNaverID', ''),  # 열린업체명1에 네이버ID 저장
                    sName2=request.POST.get('sNaverID', ''),  # 열린업체명2에 네이버ID 저장
                    sName3=request.POST.get('sNaverID', ''),  # 열린업체명3에 네이버ID 저장
                    sNaverID=request.POST.get('sNaverID', ''),
                    nType=5,  # btob제휴
                    nCondition=0,  # 기본값: 준비중
                    sCompanyName=request.POST.get('sCompanyName', ''),
                    sAddress=request.POST.get('sAddress', ''),
                    nMember=safe_int(request.POST.get('nMember')),
                    sBuildLicense='',  # btob제휴는 건설면허 불필요
                    fileBuildLicense=None,
                    sStrength=request.POST.get('sStrength', ''),
                    sCeoName=request.POST.get('sCeoName', ''),
                    sCeoPhone=request.POST.get('sCeoPhone', ''),
                    sCeoMail=request.POST.get('sCeoMail', ''),
                    fileCeo=None,  # btob제휴는 대표자 사진 불필요
                    sSaleName=request.POST.get('sSaleName', ''),
                    sSalePhone=request.POST.get('sSalePhone', ''),
                    sSaleMail=request.POST.get('sSaleMail', ''),
                    fileSale=None,  # btob제휴는 영업담당자 사진 불필요
                    sAccoutName=request.POST.get('sAccoutName', ''),
                    sAccoutPhone=request.POST.get('sAccoutPhone', ''),
                    sAccoutMail=request.POST.get('sAccoutMail', ''),
                    fileLicense=request.FILES.get('fileLicense'),
                    sEmergencyName='',  # btob제휴는 비상연락처 불필요
                    sEmergencyPhone='',
                    sEmergencyRelation='',
                    dateJoin=date.today(),
                    nJoinFee=0,
                    nDeposit=0,
                    nFixFee=0,
                    fFeePercent=0.0,
                    nOrderFee=0,
                    nReportPeriod=0,
                    fileCampaignAgree=None,  # btob제휴는 캠페인 동의서 불필요
                    bPrivacy=request.POST.get('bPrivacy') == 'on',
                    bCompetition=False,  # btob제휴는 경업금지 동의 불필요
                    bAptAll=False,
                    bAptPart=False,
                    bHouseAll=False,
                    bHousePart=False,
                    bCommerceAll=False,
                    bCommercePart=False,
                    bBuild=False,
                    bExtra=False,
                    bUnion=False,
                    bMentor=False,
                    sMentee='',
                    nRefund=0,
                    sManager='',
                    dateWithdraw=None,
                    sWithdraw='',
                    sMemo='btob제휴 가입신청서를 통해 등록됨',
                    sPicture='',
                    sGallery='',
                    sEstimate=''
                )

                # 협약서 파일들 처리
                contract_files = request.FILES.getlist('fileContract')
                for contract_file in contract_files:
                    ContractFile.objects.create(
                        company=company,
                        file=contract_file
                    )

                # Member 데이터 생성
                Member.objects.create(
                    sNaverID0='',  # 식별자는 빈값으로
                    sNaverID=request.POST.get('sNaverID', ''),  # 네이버 ID
                    sCompanyName=request.POST.get('sCompanyName', ''),  # 업체명
                    sName=request.POST.get('sCeoName', ''),  # 대표자 이름
                    sPhone=request.POST.get('sCeoPhone', ''),  # 대표 핸드폰번호
                    noCompany=company.no,  # 자동으로 company 연결
                    nCafeGrade=0,  # 기본값: 일반
                    nNick='',
                    bMaster=True,  # 마스터로 설정 (bMaster=1)
                    bApproval=False,  # 비승인 상태 (bApproval=0)
                    # 기본 권한들을 쓰기권한(2)으로 설정
                    nCompanyAuthority=2,
                    nOrderAuthority=2,
                    nContractAuthority=2,
                    nEvaluationAuthority=2
                )

                messages.success(request, f'btob제휴 가입신청이 완료되었습니다. 업체명: {company.sCompanyName}')
                return redirect('join:registration_success')

        except Exception as e:
            messages.error(request, f'가입신청 중 오류가 발생했습니다: {str(e)}')
            return render(request, 'join/btob_registration.html')

    return render(request, 'join/btob_registration.html')
