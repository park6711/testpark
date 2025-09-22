#!/usr/bin/env python
import os
import sys
import django
from datetime import datetime, timedelta, time
import random
from faker import Faker

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testpark_project.settings')
django.setup()

from evaluation.models import EvaluationNo, FixFee, Complain, Satisfy, Evaluation, YearEvaluation
from company.models import Company

fake = Faker('ko_KR')

def create_evaluation_no_data():
    """EvaluationNo 테스트 데이터 30개 생성"""
    print("EvaluationNo 테스트 데이터 생성 중...")

    evaluations = []
    for i in range(30):
        # 평가 기간 (월별 또는 분기별)
        start_date = fake.date_between(start_date='-2y', end_date='+6m')
        end_date = start_date + timedelta(days=random.randint(30, 90))

        # 포인트 적용 기간 (평가 종료 후)
        point_start = end_date + timedelta(days=random.randint(1, 7))
        point_end = point_start + timedelta(days=random.randint(30, 60))

        # 계약률 데이터
        avg_all = random.uniform(15.0, 35.0)
        avg_excel = avg_all + random.uniform(5.0, 15.0)

        # 예약문자 시간
        excel_time = time(hour=random.randint(9, 17), minute=random.choice([0, 30]))
        week_time = time(hour=random.randint(9, 17), minute=random.choice([0, 30]))

        evaluation = EvaluationNo(
            dateStart=start_date,
            dateEnd=end_date,
            datePointStart=point_start,
            datePointEnd=point_end,
            fAverageAll=round(avg_all, 2),
            fAverageExcel=round(avg_excel, 2),
            timeExcel=excel_time,
            timeWeek=week_time
        )
        evaluations.append(evaluation)

    EvaluationNo.objects.bulk_create(evaluations)
    print(f"EvaluationNo {len(evaluations)}개 생성 완료!")
    return [eval.no for eval in EvaluationNo.objects.all()]

def create_fix_fee_data():
    """FixFee 테스트 데이터 30개 생성"""
    print("FixFee 테스트 데이터 생성 중...")

    company_ids = list(Company.objects.values_list('no', flat=True))
    if not company_ids:
        company_ids = list(range(1, 21))

    fees = []
    for i in range(30):
        # 납부기준일 (매월)
        todo_date = fake.date_between(start_date='-6m', end_date='+3m')

        # 납부일자 (기준일 전후 랜덤)
        has_deposit = random.random() > 0.2  # 80% 납부율
        deposit_date = None
        deposit_amount = 0
        is_paid = False

        if has_deposit:
            deposit_date = todo_date + timedelta(days=random.randint(-5, 15))
            deposit_amount = random.randint(10, 100) * 10000  # 10만~100만원
            is_paid = random.random() > 0.1  # 90% 완납

        fee = FixFee(
            noCompany=random.choice(company_ids),
            dateToDo=todo_date,
            dateDeposit=deposit_date,
            nDeposit=deposit_amount,
            bDeposit=is_paid,
            sMemo=fake.text(max_nb_chars=100) if random.random() > 0.7 else ''
        )
        fees.append(fee)

    FixFee.objects.bulk_create(fees)
    print(f"FixFee {len(fees)}개 생성 완료!")

def create_complain_data(evaluation_ids):
    """Complain 테스트 데이터 30개 생성"""
    print("Complain 테스트 데이터 생성 중...")

    company_ids = list(Company.objects.values_list('no', flat=True))
    if not company_ids:
        company_ids = list(range(1, 21))

    complaint_samples = [
        "공사 일정이 계속 지연되고 있습니다.",
        "시공 품질이 약속과 다릅니다.",
        "연락이 잘 안되고 응답이 늦습니다.",
        "추가 비용을 계속 요구합니다.",
        "A/S가 제대로 이루어지지 않습니다.",
        "약속한 자재와 다른 자재를 사용했습니다.",
        "소음과 먼지 관리가 안됩니다.",
        "기술자의 태도가 불친절합니다."
    ]

    paths = ["카페", "전화", "이메일", "방문", "온라인"]
    workers = ["김관리", "이담당", "박실장", "최팀장"]

    complains = []
    for i in range(30):
        complain_score = random.uniform(1.0, 10.0)

        complain = Complain(
            noEvaluation=random.choice(evaluation_ids),
            noCompany=random.choice(company_ids),
            sTime=fake.date_time_between(start_date='-1y', end_date='now').strftime('%Y-%m-%d %H:%M'),
            sComName=fake.company(),
            sPass=random.choice(paths),
            sComplain=random.choice(complaint_samples),
            sComplainPost=f"http://cafe.naver.com/post/{fake.numerify('######')}",
            sPost=fake.numerify('###-####'),
            sFile=f"complain_{i+1}.jpg" if random.random() > 0.5 else '',
            sCheck="확인완료" if random.random() > 0.3 else "확인중",
            sWorker=random.choice(workers),
            fComplain=round(complain_score, 1)
        )
        complains.append(complain)

    Complain.objects.bulk_create(complains)
    print(f"Complain {len(complains)}개 생성 완료!")

def create_satisfy_data(evaluation_ids):
    """Satisfy 테스트 데이터 30개 생성"""
    print("Satisfy 테스트 데이터 생성 중...")

    company_ids = list(Company.objects.values_list('no', flat=True))
    if not company_ids:
        company_ids = list(range(1, 21))

    feedback_samples = [
        "매우 만족합니다. 깔끔하고 빠른 시공이었습니다.",
        "전반적으로 만족하지만 일정이 조금 늦었습니다.",
        "품질은 좋으나 소음 관리가 아쉬웠습니다.",
        "친절하고 꼼꼼한 시공에 감사드립니다.",
        "기대 이상의 결과물에 만족합니다.",
        "A/S까지 완벽했습니다.",
        "가격 대비 만족스러운 결과입니다."
    ]

    satisfies = []
    for i in range(30):
        satisfy_score = random.uniform(3.0, 10.0)

        satisfy = Satisfy(
            noEvaluation=random.choice(evaluation_ids),
            noCompany=random.choice(company_ids),
            sCompanyName=fake.company(),
            sTime=fake.date_time_between(start_date='-1y', end_date='now').strftime('%Y-%m-%d %H:%M'),
            sAddress=fake.address(),
            sMemo=random.choice(feedback_samples) if random.random() > 0.3 else '',
            fSatisfy=round(satisfy_score, 1)
        )
        satisfies.append(satisfy)

    Satisfy.objects.bulk_create(satisfies)
    print(f"Satisfy {len(satisfies)}개 생성 완료!")

def create_evaluation_data(evaluation_ids):
    """Evaluation 테스트 데이터 100개 생성"""
    print("Evaluation 테스트 데이터 생성 중...")

    company_ids = list(Company.objects.values_list('no', flat=True))
    if not company_ids:
        company_ids = list(range(1, 51))

    evaluations = []
    for i in range(100):
        # 업무 실적 생성
        n_all = random.randint(10, 100)
        n_part = random.randint(0, n_all // 3)
        n_contract = random.randint(n_all // 4, n_all)
        n_return = random.randint(0, n_all // 5)
        n_cancel = random.randint(0, n_all // 10)
        n_except = random.randint(0, n_all // 20)
        n_sum = n_all + n_part

        # 계약률 계산
        contract_rate = (n_contract / n_sum * 100) if n_sum > 0 else 0

        # 금액 정보
        fee = random.randint(100, 2000) * 10000
        fix_fee = random.randint(10, 50) * 10000
        dot_com = random.randint(0, 500) * 10000
        btob = random.randint(0, 300) * 10000

        # 포인트 정보
        pre_point = random.randint(0, 10000)
        payback_point = random.randint(1000, 50000)
        sum_point = pre_point + payback_point
        use_point = random.randint(0, sum_point)
        remain_point = sum_point - use_point

        # 세부 점수 계산
        scores = {
            'percent': random.uniform(10.0, 30.0),
            'fee': random.uniform(5.0, 20.0),
            'fix_fee': random.uniform(5.0, 15.0),
            'btob': random.uniform(0.0, 10.0),
            'review': random.uniform(0.0, 15.0),
            'complain': random.uniform(-5.0, 0.0),
            'satisfy': random.uniform(0.0, 10.0),
            'answer1': random.uniform(0.0, 5.0),
            'answer2': random.uniform(0.0, 5.0),
            'seminar': random.uniform(0.0, 3.0),
            'mento': random.uniform(0.0, 5.0),
            'warranty': random.uniform(0.0, 5.0),
            'safe': random.uniform(0.0, 3.0),
            'special': random.uniform(-5.0, 10.0)
        }

        # 총합 점수 계산
        total_score = sum(scores.values())

        # 등급 결정
        if total_score >= 80:
            grade = 1  # A급
            level = random.randint(4, 5)
        elif total_score >= 60:
            grade = 2  # B급
            level = random.randint(3, 4)
        elif total_score >= 40:
            grade = 3  # C급
            level = random.randint(2, 3)
        else:
            grade = 4  # D급
            level = random.randint(1, 2)

        evaluation = Evaluation(
            noEvaluationNo=random.choice(evaluation_ids),
            noCompany=random.choice(company_ids),
            fTotalScore=round(total_score, 2),
            nLevel=level,
            nGrade=grade,
            fPercent=round(contract_rate, 2),
            bWeak=total_score < 50,
            nReturn=n_return,
            nCancel=n_cancel,
            nExcept=n_except,
            nPart=n_part,
            nAll=n_all,
            nSum=n_sum,
            nContract=n_contract,
            nFee=fee,
            nFixFee=fix_fee,
            nDotCom=dot_com,
            nBtoB=btob,
            fReview=random.uniform(0.0, 10.0),
            fComplain=random.uniform(0.0, 5.0),
            nSatisfy=random.randint(0, 20),
            fSatisfy=random.uniform(5.0, 10.0),
            nAnswer1=random.randint(0, 50),
            nAnswer2=random.randint(0, 30),
            nSeminar=random.randint(0, 10),
            bMento=random.random() > 0.8,
            nWarranty1=random.randint(0, 5),
            nWarranty2=random.randint(0, 5),
            nWarranty3=random.randint(0, 5),
            nSafe=random.randint(0, 10),
            fSpecial=random.uniform(-5.0, 10.0),
            nPayBackPoint=payback_point,
            nPrePoint=pre_point,
            nSumPoint=sum_point,
            nUsePoint=use_point,
            nRemainPoint=remain_point,
            fPercentScore=round(scores['percent'], 2),
            fFeeScore=round(scores['fee'], 2),
            fFixFeeScore=round(scores['fix_fee'], 2),
            fBtoBScore=round(scores['btob'], 2),
            fReviewScore=round(scores['review'], 2),
            fComplainScore=round(scores['complain'], 2),
            fSafistyScore=round(scores['satisfy'], 2),
            fAnswer1Score=round(scores['answer1'], 2),
            fAnswer2Socre=round(scores['answer2'], 2),
            fSeminarScore=round(scores['seminar'], 2),
            fMentoScore=round(scores['mento'], 2),
            fWarrantyScore=round(scores['warranty'], 2),
            fSafeScore=round(scores['safe'], 2),
            fSpecialScore=round(scores['special'], 2),
            bExcept=random.random() > 0.95
        )
        evaluations.append(evaluation)

    Evaluation.objects.bulk_create(evaluations)
    print(f"Evaluation {len(evaluations)}개 생성 완료!")

def create_year_evaluation_data():
    """YearEvaluation 테스트 데이터 100개 생성"""
    print("YearEvaluation 테스트 데이터 생성 중...")

    company_ids = list(Company.objects.values_list('no', flat=True))
    if not company_ids:
        company_ids = list(range(1, 51))

    years = [2022, 2023, 2024]
    awards = ['대상', '최우수상', '우수상', '장려상', '참여상']

    year_evaluations = []
    for year in years:
        # 해당 연도의 업체들 평가
        companies_for_year = random.sample(company_ids, min(35, len(company_ids)))

        # 점수 생성 및 정렬
        company_scores = []
        for company_id in companies_for_year:
            score = random.uniform(30.0, 95.0)
            company_scores.append((company_id, score))

        # 점수순으로 정렬
        company_scores.sort(key=lambda x: x[1], reverse=True)

        # 순위 부여 및 상패 결정
        for rank, (company_id, score) in enumerate(company_scores, 1):
            # 상패 결정
            award = ''
            if rank == 1:
                award = '대상'
            elif rank <= 3:
                award = '최우수상'
            elif rank <= 10:
                award = '우수상'
            elif rank <= 20:
                award = '장려상'
            elif rank <= 30:
                award = '참여상'

            year_eval = YearEvaluation(
                nYear=year,
                noCompany=company_id,
                fScore=round(score, 2),
                nRank=rank,
                sAward=award
            )
            year_evaluations.append(year_eval)

    YearEvaluation.objects.bulk_create(year_evaluations)
    print(f"YearEvaluation {len(year_evaluations)}개 생성 완료!")

def main():
    print("Evaluation 앱 테스트 데이터 생성을 시작합니다...")

    try:
        # 기존 데이터 확인
        print("기존 데이터 현황:")
        print(f"EvaluationNo: {EvaluationNo.objects.count()}개")
        print(f"FixFee: {FixFee.objects.count()}개")
        print(f"Complain: {Complain.objects.count()}개")
        print(f"Satisfy: {Satisfy.objects.count()}개")
        print(f"Evaluation: {Evaluation.objects.count()}개")
        print(f"YearEvaluation: {YearEvaluation.objects.count()}개")

        # 1. EvaluationNo 생성
        evaluation_ids = create_evaluation_no_data()

        # 2. FixFee 생성
        create_fix_fee_data()

        # 3. Complain 생성
        create_complain_data(evaluation_ids)

        # 4. Satisfy 생성
        create_satisfy_data(evaluation_ids)

        # 5. Evaluation 생성
        create_evaluation_data(evaluation_ids)

        # 6. YearEvaluation 생성
        create_year_evaluation_data()

        print("\n=== 데이터 생성 완료 ===")
        print(f"총 EvaluationNo: {EvaluationNo.objects.count()}개")
        print(f"총 FixFee: {FixFee.objects.count()}개")
        print(f"총 Complain: {Complain.objects.count()}개")
        print(f"총 Satisfy: {Satisfy.objects.count()}개")
        print(f"총 Evaluation: {Evaluation.objects.count()}개")
        print(f"총 YearEvaluation: {YearEvaluation.objects.count()}개")

    except Exception as e:
        print(f"에러 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()