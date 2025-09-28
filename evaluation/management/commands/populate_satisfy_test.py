from django.core.management.base import BaseCommand
from django.db import transaction
from datetime import datetime
from evaluation.models import Satisfy
from company.models import Company
import re


class Command(BaseCommand):
    help = '테스트용 Satisfy 데이터를 입력합니다.'

    def handle(self, *args, **kwargs):
        # 테스트 데이터
        test_data = [
            {
                'sTimeStamp': '2025. 1. 1 오후 3:17:48',
                'sCompanyName': '서울1호',
                'sPhone': '01047340159',
                'sConMoney': '1,930,500원',
                'sArea': '서울시 노원구 월계동 현대아파트',
                'scores': [0, 1, 0, 0, 0, 0, 0, 0, 0, 0],  # 매우만족=0, 만족=1
                'sS11': '빠르게 잘 진행해 주셔서 너무 감사합니다'
            },
            {
                'sTimeStamp': '2025. 1. 4 오후 2:01:48',
                'sCompanyName': '서울2호',
                'sPhone': '01094589620',
                'sConMoney': '70만원',
                'sArea': '서울 도봉구 창동 주공19단지',
                'scores': [1, 1, 0, 0, 0, 0, 0, 1, 0, 0],
                'sS11': ''
            },
            {
                'sTimeStamp': '2025. 1. 4 오후 2:42:14',
                'sCompanyName': '서울3호',
                'sPhone': '01049245118',
                'sConMoney': '4500만원',
                'sArea': '시흥시 대동청구아파트',
                'scores': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                'sS11': '빠른 피드백이 너무 좋았습니다.'
            },
            {
                'sTimeStamp': '2025. 1. 5 오전 8:51:46',
                'sCompanyName': '서울4호',
                'sPhone': '01034485357',
                'sConMoney': '약 3000만원?',
                'sArea': '용인시 기흥구 마북동 블루밍구성더센트럴',
                'scores': [0, 1, 1, 0, 0, 0, 0, 0, 0, 0],
                'sS11': ''
            },
            {
                'sTimeStamp': '2025. 1. 6 오후 2:14:32',
                'sCompanyName': '서울5호',
                'sPhone': '01071028588',
                'sConMoney': '1,410,000',
                'sArea': '성남시 중원구 금광동 금빛그랑메종아파트',
                'scores': [0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
                'sS11': '저렴하지만 품질 우수했고, as까지 확실히 해주셨습니다. 다른 분에게 소개하고 싶어요.'
            },
            {
                'sTimeStamp': '2025. 1. 6 오후 4:55:10',
                'sCompanyName': '서울6호',
                'sPhone': '01097372018',
                'sConMoney': '64,460,000',
                'sArea': '군포시 산본동 수리한양아파트',
                'scores': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                'sS11': ''
            },
            {
                'sTimeStamp': '2025. 1. 6 오후 8:52:56',
                'sCompanyName': '서울7호',
                'sPhone': '01085862573',
                'sConMoney': '3900만원',
                'sArea': '서울시 동대문구 래미안크레시티',
                'scores': [1, 1, 1, 0, 1, 2, 1, 1, 0, 1],  # 보통=2
                'sS11': '서울 37호 사장님 실장님 친절하게 잘 해주셔서 감사했습니다'
            },
            {
                'sTimeStamp': '2025. 1. 10 오후 12:34:13',
                'sCompanyName': '서울8호',
                'sPhone': '01071187551',
                'sConMoney': '3710만원',
                'sArea': '인천시 부평구 청천동 청천푸루지오',
                'scores': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                'sS11': '추운 겨울날 인테리어하시느라 고생 많으셨고 친절한 서비스와 만족스러운 인테리어 결과가 너무 좋습니다. 다음 이사가게 될 때 또 견적 부탁 드리겠습니다. 감사합니다.'
            },
            {
                'sTimeStamp': '2025. 1. 10 오후 6:05:43',
                'sCompanyName': '서울9호',
                'sPhone': '01065464007',
                'sConMoney': '40,830,000',
                'sArea': '광명 하안동 광명두산위브트레지움 아파트',
                'scores': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                'sS11': '''저희는 매우 만족하고, 가성비 최고로 인테리어 하려는 분들께.. 그리고 할까 말까 고민하는 분들께 적극 추천하고 싶습니다.
AS 2년도 든든합니다.

많은 분들 중에 서울6호님을 만난건 큰 행운이었습니다. 인테리어 하면서 의견 충돌로 힘들었다는 이야기도 많이 들었는데, 단 한번도 그런적 없이 저희 의견 잘 경청해주시고, 친절하게 상담과 시공해 주셨습니다. ^^
덕분에 2025년 새해를 멋지게 밝게 시작합니다.
새해에도 건강하시고 ~ 더욱 번창하세요.
6호 사장님 ^^ 꾸벅.'''
            },
            {
                'sTimeStamp': '2025. 1. 12 오전 10:44:20',
                'sCompanyName': '서울1',
                'sPhone': '01067930731',
                'sConMoney': '3300만원',
                'sArea': '고양시 덕양구 래미안휴레스트',
                'scores': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                'sS11': ''
            },
            {
                'sTimeStamp': '2025. 1. 12 오후 2:08:40',
                'sCompanyName': '서울2',
                'sPhone': '01089196420',
                'sConMoney': '6,500',
                'sArea': '수원시 장안구 정자동 청솔마을한라아파트',
                'scores': [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
                'sS11': ''
            },
            {
                'sTimeStamp': '2025. 1. 13 오후 2:21:56',
                'sCompanyName': '서울3',
                'sPhone': '01076535396',
                'sConMoney': '37,560,000원',
                'sArea': '파주시 운정동 한라비발디',
                'scores': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                'sS11': ''
            },
            {
                'sTimeStamp': '2025. 1. 13 오후 3:28:30',
                'sCompanyName': '서울1호',
                'sPhone': '01085289298',
                'sConMoney': '2200만원',
                'sArea': '화성시 기산구 행림마을삼성래미안1차',
                'scores': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                'sS11': '적은 예산임에도 불구하고 최대한 해주실수 있는건 다 해주시려고 하셨습니다! 다음에 또 공사할 일이 생긴다면 경기32호에 하고 싶어요!'
            },
            {
                'sTimeStamp': '2025. 1. 13 오후 5:16:40',
                'sCompanyName': '서울2호',
                'sPhone': '01099830771',
                'sConMoney': '6,864,000',
                'sArea': '안산시 고잔동 롯데캐슬골드파크아파트',
                'scores': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                'sS11': '너무 잘 소통해주시고 설명해 주셔서 좋았습니다.'
            },
            {
                'sTimeStamp': '2025. 1. 13 오후 7:55:52',
                'sCompanyName': '서울3호',
                'sPhone': '01056702390',
                'sConMoney': '',
                'sArea': '서울 영등포구 양평동 삼호아파트',
                'scores': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                'sS11': ''
            },
            {
                'sTimeStamp': '2025. 1. 16 오후 8:49:26',
                'sCompanyName': '서울4호',
                'sPhone': '01093180566',
                'sConMoney': '부가세 포함 4700정도',
                'sArea': '서울시 송파구 풍납2동 한강극동아파트',
                'scores': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                'sS11': '굉장히 진정성있으신분이에요. 자재도 모두 설명해주셨습니다. 연세가 있으셔서 혹시나 소통이 안될가 염려했던거와 달리 오히려 뛰어난 지식과지적인모습으로 항상 따뜻하게 소통해주셨어요. 다른 인테리어는 상담했을시 굉장히 확고한 기준때문에 제가 원하는대로 하기 어려워서 고르고 고른업체인지라 소비자가 원하는 방향을 제일 존중해주시는 부분이 굉장히 만족스러웠습니다. 필요없는 부분은 절대 권유도 안하세요.ㅎㅎ 최고입니다.'
            },
            {
                'sTimeStamp': '2025. 1. 19 오후 1:27:56',
                'sCompanyName': '서울5호',
                'sPhone': '01065776218',
                'sConMoney': '435만원',
                'sArea': '서울 금천구 벽산5단지 안방화장실',
                'scores': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                'sS11': ''
            },
            {
                'sTimeStamp': '2025. 1. 19 오후 8:59:54',
                'sCompanyName': '서울6호',
                'sPhone': '01064835991',
                'sConMoney': '약7천만원',
                'sArea': '서울시 성북구 돈암동 돈암범양아파트',
                'scores': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                'sS11': '좋은견적, 깔끔한 작업, 빠른 커뮤니케이션 전체 과정이 정말 만족스러웠습니다!'
            },
            {
                'sTimeStamp': '2025. 1. 25 오후 4:32:17',
                'sCompanyName': '서울7호',
                'sPhone': '01075793012',
                'sConMoney': '5900만원',
                'sArea': '서울 강북구 SK북한산씨티아파트',
                'scores': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                'sS11': '박목수열린견적서를 통해 믿고 맡길 수 있는 업체 통해서 공사를 잘 마칠 수 있었습니다. 감사합니다.'
            },
            {
                'sTimeStamp': '2025. 1. 30 오후 4:13:32',
                'sCompanyName': '서울8호',
                'sPhone': '01084978000',
                'sConMoney': '약5800만원',
                'sArea': '수원시 권선구 권선동 삼천리1차아파트',
                'scores': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                'sS11': '공사전 걱정이 많았지만 소통도 잘되고 원하는대로 공사를 잘해주셔서 인테리어하는내내 걱정없이 잘마무리되었습니다 감사합니다'
            },
            {
                'sTimeStamp': '2025. 1. 31 오전 7:50:53',
                'sCompanyName': '서울9호',
                'sPhone': '01031389821',
                'sConMoney': '1,500',
                'sArea': '대구 신천자이아파트',
                'scores': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                'sS11': ''
            },
            {
                'sTimeStamp': '2025. 2. 2 오후 2:22:27',
                'sCompanyName': '서울10',
                'sPhone': '01066554267',
                'sConMoney': '13,800,000',
                'sArea': '인천 e편한세상',
                'scores': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                'sS11': '너무 친절히 긍정적으로 응대해 주셔서 감사드립니다 다음 인테리어도 인천 6호와 진행하고 싶습니다'
            }
        ]

        # 트랜잭션으로 묶어서 처리
        with transaction.atomic():
            success_count = 0
            error_count = 0

            for idx, data in enumerate(test_data, 1):
                try:
                    # Company 찾기 (sName2 또는 sName3으로)
                    company_no = 0  # 기본값
                    try:
                        # 업체명에서 숫자 제거 (예: '서울1호' -> '서울', '서울1' -> '서울')
                        clean_name = re.sub(r'\d+호?$', '', data['sCompanyName'])

                        # sName2 또는 sName3으로 검색
                        company = Company.objects.filter(
                            sName2=data['sCompanyName']
                        ).first() or Company.objects.filter(
                            sName3=data['sCompanyName']
                        ).first() or Company.objects.filter(
                            sName2=clean_name
                        ).first()

                        if company:
                            company_no = company.no
                        else:
                            self.stdout.write(self.style.WARNING(
                                f"업체명 '{data['sCompanyName']}'을(를) 찾을 수 없습니다. 기본값 0 사용"
                            ))
                    except Exception as e:
                        self.stdout.write(self.style.WARNING(
                            f"업체 검색 중 오류: {str(e)}"
                        ))

                    # 타임스탬프 파싱
                    timestamp = None
                    try:
                        # "2025. 1. 1 오후 3:17:48" 형식 파싱
                        timestamp_str = data['sTimeStamp']
                        # 오전/오후 처리
                        timestamp_str = timestamp_str.replace('오후', 'PM').replace('오전', 'AM')
                        # 파싱
                        timestamp = datetime.strptime(timestamp_str, '%Y. %m. %d %p %I:%M:%S')
                    except Exception as e:
                        self.stdout.write(self.style.WARNING(
                            f"타임스탬프 파싱 실패 '{data['sTimeStamp']}': {str(e)}"
                        ))

                    # Satisfy 객체 생성
                    satisfy = Satisfy(
                        sTimeStamp=data['sTimeStamp'],
                        sCompanyName=data['sCompanyName'],
                        sPhone=data['sPhone'],
                        sConMoney=data['sConMoney'],
                        sArea=data['sArea'],
                        nS1=data['scores'][0],
                        nS2=data['scores'][1],
                        nS3=data['scores'][2],
                        nS4=data['scores'][3],
                        nS5=data['scores'][4],
                        nS6=data['scores'][5],
                        nS7=data['scores'][6],
                        nS8=data['scores'][7],
                        nS9=data['scores'][8],
                        nS10=data['scores'][9],
                        sS11=data['sS11'],
                        noCompany=company_no,
                        timeStamp=timestamp
                    )

                    # save 메소드가 자동으로 fSatisfySum을 계산함
                    satisfy.save()

                    success_count += 1
                    self.stdout.write(self.style.SUCCESS(
                        f"✓ 입력 완료: {data['sCompanyName']} (만족도 합계: {satisfy.fSatisfySum}점)"
                    ))

                except Exception as e:
                    self.stdout.write(self.style.ERROR(
                        f"✗ 오류 발생 ({data['sCompanyName']}): {str(e)}"
                    ))
                    error_count += 1

        # 결과 출력
        self.stdout.write(self.style.SUCCESS(f'\n===== 작업 완료 ====='))
        self.stdout.write(self.style.SUCCESS(f'✓ 성공: {success_count}건'))
        if error_count > 0:
            self.stdout.write(self.style.ERROR(f'✗ 실패: {error_count}건'))

        # 최종 확인
        final_count = Satisfy.objects.count()
        self.stdout.write(self.style.SUCCESS(f'\n최종 Satisfy 데이터 수: {final_count}건'))

        # 통계 정보
        if final_count > 0:
            from django.db.models import Avg, Max, Min
            stats = Satisfy.objects.aggregate(
                avg_score=Avg('fSatisfySum'),
                max_score=Max('fSatisfySum'),
                min_score=Min('fSatisfySum')
            )
            self.stdout.write(self.style.SUCCESS(f'평균 만족도: {stats["avg_score"]:.1f}점'))
            self.stdout.write(self.style.SUCCESS(f'최고 만족도: {stats["max_score"]}점'))
            self.stdout.write(self.style.SUCCESS(f'최저 만족도: {stats["min_score"]}점'))