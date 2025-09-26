from django.core.management.base import BaseCommand
from django.db import transaction
from datetime import datetime
import json
from evaluation.models import Complain
from company.models import Company


class Command(BaseCommand):
    help = 'Complain 데이터를 백업하고 새로운 데이터로 재구성합니다.'

    def handle(self, *args, **kwargs):
        # 새로운 Complain 데이터
        new_complain_data = [
            {
                'sTimeStamp': '2025. 8. 6 오후 6:52:09',
                'sCompanyName': '경기9',
                'sPass': '문자',
                'sComplain': '8월 4일 A/S 접수 당일 견적서 주신다고 했지만 이틀이 지났는데도 무응답',
                'sComplainPost': '',
                'sPost': 'https://cafe.naver.com/pcarpenter/838364',
                'sSMSBool': '발송',
                'sSMSMent': '상기 내용으로 고객불만건이 접수되었음을 알려드리며, 앞으로는 이러한 고객불만이 발생하지 않도록 노력해 주시길 부탁드립니다.',
                'sFile': 'https://drive.google.com/open?id=1iJB37ac3zwOhctmWIrs_aPtCwp1xNX5f',
                'sCheck': '확인 불필요',
                'sWorker': '비비안',
                'fComplain': 0.2
            },
            {
                'sTimeStamp': '2025. 8. 8 오전 7:13:27',
                'sCompanyName': '경기22',
                'sPass': 'A/S 접수 게시글',
                'sComplain': '연락없음, 견적서 지체',
                'sComplainPost': 'https://cafe.naver.com/pcarpenter/840057',
                'sPost': 'https://cafe.naver.com/pcarpenter/839478',
                'sSMSBool': '발송',
                'sSMSMent': '상기 내용으로 고객불만건이 접수되었음을 알려드리며, 빠른 해명 댓글과 빠른 조치 요청드립니다.',
                'sFile': '',
                'sCheck': '확인 불필요',
                'sWorker': '댄',
                'fComplain': 0.2
            },
            {
                'sTimeStamp': '2025. 8. 8 오전 8:13:03',
                'sCompanyName': '서울27',
                'sPass': 'A/S 접수 게시글',
                'sComplain': '더이상 누수문제가 발생하지 않도록 문제 해결 원함',
                'sComplainPost': 'https://cafe.naver.com/pcarpenter/840060',
                'sPost': 'https://cafe.naver.com/pcarpenter/837608',
                'sSMSBool': '발송',
                'sSMSMent': '상기 내용으로 고객불만건이 접수되었음을 알려드리며, 빠른 해명 댓글과 빠른 조치 요청드립니다.',
                'sFile': '',
                'sCheck': '계약 확인',
                'sWorker': '댄',
                'fComplain': 0
            },
            {
                'sTimeStamp': '2025. 8. 8 오후 3:16:43',
                'sCompanyName': '시스템에어컨5',
                'sPass': '문자',
                'sComplain': '안녕하세요, 시스템에어컨5호님이 연락이 닿지 않아, 혹 다른 업체와의 연결을 부탁드려도 될지요?',
                'sComplainPost': '',
                'sPost': 'https://cafe.naver.com/pcarpenter/837026',
                'sSMSBool': '발송',
                'sSMSMent': '상기 내용으로 고객불만건이 접수되었음을 알려드리며, 앞으로는 이러한 고객불만이 발생하지 않도록 노력해 주시길 부탁드립니다.',
                'sFile': 'https://drive.google.com/open?id=1D975Ot8qLljKcPfYfN1sPompZoeYCeB5',
                'sCheck': '확인 불필요',
                'sWorker': '제니',
                'fComplain': 0.2
            },
            {
                'sTimeStamp': '2025. 8. 11 오후 12:24:30',
                'sCompanyName': '서울54',
                'sPass': '일반 게시글',
                'sComplain': '계약시 견적서와 최종 상세견적서의 인건항목이 다름(협의되지 않은 내역이 포함, 카페 글 확인 요)',
                'sComplainPost': 'https://cafe.naver.com/pcarpenter/840435',
                'sPost': 'https://cafe.naver.com/pcarpenter/829967',
                'sSMSBool': '발송',
                'sSMSMent': '상기 내용으로 고객불만건이 접수되었음을 알려드리며, 빠른 해명 댓글과 빠른 조치 요청드립니다.',
                'sFile': 'https://drive.google.com/open?id=1hi2dkfBjygoCHcZS2mldeKr-rR6l3iMV',
                'sCheck': '계약 확인',
                'sWorker': '아네스',
                'fComplain': 0.2
            },
            {
                'sTimeStamp': '2025. 8. 15 오후 4:47:50',
                'sCompanyName': '욕실1',
                'sPass': 'A/S 접수 게시글',
                'sComplain': '천정 환풍기 수리',
                'sComplainPost': 'https://cafe.naver.com/pcarpenter/841012',
                'sPost': 'https://cafe.naver.com/pcarpenter/616530',
                'sSMSBool': '발송',
                'sSMSMent': '상기 내용으로 A/S 건이 접수되었음을 알려드립니다. 빠른 해명 댓글과 빠른 조치 요청드립니다.',
                'sFile': '',
                'sCheck': '계약 확인',
                'sWorker': '댄',
                'fComplain': 0
            },
            {
                'sTimeStamp': '2025. 8. 15 오후 11:08:44',
                'sCompanyName': '서울54',
                'sPass': 'A/S 접수 게시글',
                'sComplain': '장판 찍힘 1차, 2차 A/S 진행했지만 추가 A/S는 하지않고 다른 업체에 의뢰 요청',
                'sComplainPost': 'https://cafe.naver.com/pcarpenter/841046',
                'sPost': 'https://cafe.naver.com/pcarpenter/829967',
                'sSMSBool': '발송',
                'sSMSMent': '상기 내용으로 고객불만건이 접수되었음을 알려드리며, 빠른 해명 댓글과 빠른 조치 요청드립니다.',
                'sFile': '',
                'sCheck': '계약 확인',
                'sWorker': '비비안',
                'fComplain': 0.2
            },
            {
                'sTimeStamp': '2025. 8. 20 오전 11:50:59',
                'sCompanyName': '서울46',
                'sPass': '댓글',
                'sComplain': '연락 없음',
                'sComplainPost': 'https://cafe.naver.com/pcarpenter/840647',
                'sPost': 'https://cafe.naver.com/pcarpenter/840647',
                'sSMSBool': '발송',
                'sSMSMent': '상기 내용으로 고객불만건이 접수되었음을 알려드리며, 빠른 해명 댓글과 빠른 조치 요청드립니다.',
                'sFile': '',
                'sCheck': '확인 불필요',
                'sWorker': '댄',
                'fComplain': 0.2
            },
            {
                'sTimeStamp': '2025. 8. 22 오후 2:57:05',
                'sCompanyName': '이사1',
                'sPass': '일반 게시글',
                'sComplain': '이사1호에서 안내주신다 하였는데 문자, 전화 다 안받으시네요.\n다른 업체로 연결 부탁드립니다.',
                'sComplainPost': 'https://cafe.naver.com/pcarpenter/841974',
                'sPost': 'https://cafe.naver.com/pcarpenter/841501',
                'sSMSBool': '발송',
                'sSMSMent': '상기 내용으로 고객불만건이 접수되었음을 알려드리며, 앞으로는 이러한 고객불만이 발생하지 않도록 노력해 주시길 부탁드립니다.',
                'sFile': '',
                'sCheck': '확인 불필요',
                'sWorker': '제니',
                'fComplain': 0.2
            },
            {
                'sTimeStamp': '2025. 8. 24 오전 9:09:03',
                'sCompanyName': '대구13',
                'sPass': 'A/S 접수 게시글',
                'sComplain': '문틀 필름지 시공 하자 문의',
                'sComplainPost': 'https://cafe.naver.com/pcarpenter/842156',
                'sPost': 'https://cafe.naver.com/pcarpenter/830339',
                'sSMSBool': '발송',
                'sSMSMent': '상기 내용으로 A/S 건이 접수되었음을 알려드립니다. 빠른 해명 댓글과 빠른 조치 요청드립니다.',
                'sFile': 'https://drive.google.com/open?id=1RUis4fHMJK7Hej4SnzaYxmMl77GBrH__',
                'sCheck': '계약 확인',
                'sWorker': '제니',
                'fComplain': 0.2
            },
            {
                'sTimeStamp': '2025. 8. 26 오전 11:32:25',
                'sCompanyName': '서울64',
                'sPass': '일반 게시글',
                'sComplain': '견적의뢰후 6일이 지났지만 연락이 아직 안와서 혹시 업체를 바꿔도 될지 문의 드립니다.',
                'sComplainPost': 'https://cafe.naver.com/pcarpenter/842427',
                'sPost': 'https://cafe.naver.com/pcarpenter/841599',
                'sSMSBool': '발송',
                'sSMSMent': '상기 내용으로 고객불만건이 접수되었음을 알려드리며, 빠른 해명 댓글과 빠른 조치 요청드립니다.',
                'sFile': '',
                'sCheck': '확인 불필요',
                'sWorker': '아네스',
                'fComplain': 0.2
            },
            {
                'sTimeStamp': '2025. 8. 26 오전 11:47:18',
                'sCompanyName': '인천3',
                'sPass': 'A/S 접수 게시글',
                'sComplain': '12일에 잔금까지 다 치르고 나서 집기 들어오니까 문제가 발생합니다. (카페게시글 확인 요 )',
                'sComplainPost': 'https://cafe.naver.com/pcarpenter/842432',
                'sPost': 'https://cafe.naver.com/pcarpenter/832218',
                'sSMSBool': '발송',
                'sSMSMent': '상기 내용으로 A/S 건이 접수되었음을 알려드립니다. 빠른 해명 댓글과 빠른 조치 요청드립니다.',
                'sFile': 'https://drive.google.com/open?id=1-t5mBva8L8k7ByV-UO-f-2WqgL-Rku-1',
                'sCheck': '계약 확인',
                'sWorker': '아네스',
                'fComplain': 0
            },
            {
                'sTimeStamp': '2025. 8. 30 오후 8:18:27',
                'sCompanyName': '경기51',
                'sPass': '문자',
                'sComplain': '견적 의뢰 4일만에 문자로 통화가 되어야 견적 가능하고 고객님께 취소 접수 요청',
                'sComplainPost': '',
                'sPost': 'https://cafe.naver.com/pcarpenter/842483',
                'sSMSBool': '발송',
                'sSMSMent': '상기 내용으로 고객 불만 건이 접수되었음을 알려드립니다. 앞으로는 고객님을 통한 취소가 아니라 사장님께서 카페 본부로 반려하시기를 요청드립니다.',
                'sFile': 'https://drive.google.com/open?id=1kb88S9lWLM57Zbwd3Fl5rSODpAxk5sRb',
                'sCheck': '확인 불필요',
                'sWorker': '비비안',
                'fComplain': 0.2
            },
            {
                'sTimeStamp': '2025. 9. 1 오전 11:50:15',
                'sCompanyName': '시스템에어컨2',
                'sPass': '문자',
                'sComplain': '상담지체',
                'sComplainPost': '',
                'sPost': 'https://cafe.naver.com/pcarpenter/841673',
                'sSMSBool': '발송',
                'sSMSMent': '상기 내용으로 고객불만건이 접수되었음을 알려드리며, 앞으로는 이러한 고객불만이 발생하지 않도록 노력해 주시길 부탁드립니다.',
                'sFile': 'https://drive.google.com/open?id=1pnk3e9ElFhrrPSDB40WuP46FitZMQItC',
                'sCheck': '확인 불필요',
                'sWorker': '스텔라',
                'fComplain': 0.2
            },
            {
                'sTimeStamp': '2025. 9. 3 오후 3:03:36',
                'sCompanyName': '경기9',
                'sPass': '문자',
                'sComplain': '경기9호 1달째 지속적으로 연락은 되지만 견적서 준다 오늘 내일이면 된다 하고 지금 1달째 입니다. \n이제 견적서를 준다고 해도 신뢰가 깨져서 맡기기도 싫습니다',
                'sComplainPost': '',
                'sPost': 'https://cafe.naver.com/pcarpenter/839286',
                'sSMSBool': '발송',
                'sSMSMent': '상기 내용으로 고객불만건이 접수되었음을 알려드리며, 앞으로는 이러한 고객불만이 발생하지 않도록 노력해 주시길 부탁드립니다.',
                'sFile': '',
                'sCheck': '확인 불필요',
                'sWorker': '안나',
                'fComplain': 0.2
            },
            {
                'sTimeStamp': '2025. 9. 4 오후 12:18:35',
                'sCompanyName': '경기29',
                'sPass': 'A/S 접수 게시글',
                'sComplain': '견적서 지체',
                'sComplainPost': 'https://cafe.naver.com/pcarpenter/843731',
                'sPost': 'https://cafe.naver.com/pcarpenter/842909',
                'sSMSBool': '발송',
                'sSMSMent': '상기 내용으로 고객불만건이 접수되었음을 알려드리며, 빠른 해명 댓글과 빠른 조치 요청드립니다.',
                'sFile': '',
                'sCheck': '확인 불필요',
                'sWorker': '댄',
                'fComplain': 0.2
            },
            {
                'sTimeStamp': '2025. 9. 4 오후 4:53:30',
                'sCompanyName': '서울27',
                'sPass': 'A/S 접수 게시글',
                'sComplain': '상담 지체 - 소비자 요청으로 9/3, 1차 빠른 상담 요청 드림',
                'sComplainPost': 'https://cafe.naver.com/pcarpenter/843787',
                'sPost': 'https://cafe.naver.com/pcarpenter/843094',
                'sSMSBool': '발송',
                'sSMSMent': '상기 내용으로 고객불만건이 접수되었음을 알려드리며, 빠른 해명 댓글과 빠른 조치 요청드립니다.',
                'sFile': 'https://drive.google.com/open?id=1MoA8180GFn-HjaD5RsWAyVgXoX6RigOB',
                'sCheck': '확인 불필요',
                'sWorker': '제니',
                'fComplain': 0.2
            },
            {
                'sTimeStamp': '2025. 9. 4 오후 5:00:10',
                'sCompanyName': '광주3',
                'sPass': '동참문의/기타상담',
                'sComplain': '10평 상가공사, 공기는 마무리되었으나 진행하면서 부터 꾸준히 하자가 발생. a/s 진행은 하고 있으나 애초에 업체의 공사 역량이 부족하다고 판단됨. (계약 1850만원 추가금 5~600정도(정산 필요), 총입금한 금액 1700만원, 나머지 잔금.)',
                'sComplainPost': '',
                'sPost': 'https://cafe.naver.com/pcarpenter/838365',
                'sSMSBool': '미발송',
                'sSMSMent': '광주3호 실장님과 통화함. 최대한 고객에 요청에 맞춰서 마감 잘 해주시길 요청하였으며, 잘 마무리하식로 함(고객에게도 광주3호의 a/s 의지를 안내함)',
                'sFile': '',
                'sCheck': '계약 확인',
                'sWorker': '아네스',
                'fComplain': 0.2
            },
            {
                'sTimeStamp': '2025. 9. 5 오후 3:59:25',
                'sCompanyName': '서울54',
                'sPass': '댓글',
                'sComplain': '견적서 지체',
                'sComplainPost': '',
                'sPost': 'https://cafe.naver.com/pcarpenter/842446',
                'sSMSBool': '발송',
                'sSMSMent': '상기 내용으로 고객불만건이 접수되었음을 알려드리며, 빠른 해명 댓글과 빠른 조치 요청드립니다.',
                'sFile': 'https://drive.google.com/open?id=1TyW1uNHHvoBLx51KX5ahbOGS4zzGk8DG',
                'sCheck': '확인 불필요',
                'sWorker': '스텔라',
                'fComplain': 0.2
            },
            {
                'sTimeStamp': '2025. 9. 9 오후 9:12:45',
                'sCompanyName': '부산9',
                'sPass': '문자',
                'sComplain': '견적서 지체',
                'sComplainPost': '',
                'sPost': 'https://cafe.naver.com/pcarpenter/835129',
                'sSMSBool': '발송',
                'sSMSMent': '상기 내용으로 고객불만건이 접수되었음을 알려드리며, 빠른 해명 댓글과 빠른 조치 요청드립니다.',
                'sFile': 'https://drive.google.com/open?id=12xOTHLfbNd_nmUdJQNRz08Xuye8wrubh',
                'sCheck': '확인 불필요',
                'sWorker': '비비안',
                'fComplain': 0
            },
            {
                'sTimeStamp': '2025. 9. 10 오전 9:10:05',
                'sCompanyName': '서울72',
                'sPass': '고객만족도조사 참여',
                'sComplain': '박목수에서 10%의 이윤을 가져가시는 줄 몰랐어요. 그리고 인건비항목과 자재비가 나중에 추가되고 늘어나는 부분을 조율했습니다만, 그럼에도 50만원 정도 추가금을 물게 된 것과 시공 마무리까지는 유쾌한 과정은 아니었습니다. 낱낱히 따져보려다 잘 마무리하고 무사히 끝난 것에 의의를 두려합니다.',
                'sComplainPost': '',
                'sPost': 'https://cafe.naver.com/pcarpenter/821267',
                'sSMSBool': '미발송',
                'sSMSMent': '카페에서 기업이윤(수수료) 10%를 가져간다고 오해하게 하여 고객불만 및 카페브랜드 손실 감안하여 내부적으로 불만적용함',
                'sFile': '',
                'sCheck': '계약 확인',
                'sWorker': '아네스',
                'fComplain': 0.2
            },
            {
                'sTimeStamp': '2025. 9. 10 오후 6:51:17',
                'sCompanyName': '서울52',
                'sPass': 'A/S 접수 게시글',
                'sComplain': '고객과 상의없이 스프링쿨러를 가리고 중 시공',
                'sComplainPost': 'https://cafe.naver.com/pcarpenter/844679',
                'sPost': 'https://cafe.naver.com/pcarpenter/841457',
                'sSMSBool': '발송',
                'sSMSMent': '상기 내용으로 A/S 건이 접수되었음을 알려드립니다. 빠른 해명 댓글과 빠른 조치 요청드립니다.',
                'sFile': '',
                'sCheck': '계약 확인',
                'sWorker': '비비안',
                'fComplain': 0.2
            },
            {
                'sTimeStamp': '2025. 9. 16 오후 12:16:59',
                'sCompanyName': '부산5',
                'sPass': '일반 게시글',
                'sComplain': '상담 및 견적지체',
                'sComplainPost': 'https://cafe.naver.com/pcarpenter/845461',
                'sPost': 'https://cafe.naver.com/pcarpenter/843862',
                'sSMSBool': '발송',
                'sSMSMent': '상기 내용으로 고객불만건이 접수되었음을 알려드리며, 빠른 해명 댓글과 빠른 조치 요청드립니다.',
                'sFile': 'https://drive.google.com/open?id=11JE_flRIIIaHuC5eXmyuOtQcMY8NSYO9',
                'sCheck': '확인 불필요',
                'sWorker': '스텔라',
                'fComplain': 0.2
            },
            {
                'sTimeStamp': '2025. 9. 18 오전 7:25:52',
                'sCompanyName': '서울26',
                'sPass': 'A/S 접수 게시글',
                'sComplain': '소통 어려움',
                'sComplainPost': 'https://cafe.naver.com/pcarpenter/845786',
                'sPost': 'https://cafe.naver.com/pcarpenter/809685',
                'sSMSBool': '발송',
                'sSMSMent': '상기 내용으로 A/S 건이 접수되었음을 알려드립니다. 빠른 해명 댓글과 빠른 조치 요청드립니다.',
                'sFile': '',
                'sCheck': '해당 아이디, 별명 등 제대로 검색 조회x 다시 확인 요청 필요',
                'sWorker': '댄',
                'fComplain': 0.2
            },
            {
                'sTimeStamp': '2025. 9. 19 오후 4:57:11',
                'sCompanyName': '이사1',
                'sPass': '문자',
                'sComplain': '불만 사항\n1. 외국 노동자들과 같이 온팀이였는데 우리식구들이 같이 있는데도 계속 거친말로 함부로 대하고 외국노동자들도 계속 딴데를 왔다갔다하면서 엄청 심란함\n2. 전체 인테리어 한 집이라고 주의 해달라고 했으나 \n- 바닥 장판 밀림\n- 벽도배지 찢김 (모르는 일처럼 우리에게 확인해달라고 함_인테리어 업체가 전날찍은 사진에는 찢김없음)\n3. 침대 사이즈때문에 사다리차를 중간에 옮겨야한다며 견적서에 없는 15만원 추가 됨',
                'sComplainPost': '',
                'sPost': 'https://cafe.naver.com/pcarpenter/833003',
                'sSMSBool': '미발송',
                'sSMSMent': '박창국 대표(01040359030)에게 별도 문자 발송함. [박목수의열린견적서] 안녕하세요 ~ 금일 이사1호를 이용한 고객의 고객불만이 접수되어 안내드립니다. 불만 사항: 1. 외국 노동자들과 같이 온팀이였는데 우리식구들이 같이 있는데도 계속 거친말로 함부로 대하고 외국 노동자들도 계속 딴데를 왔다갔다하면서 엄청 심란함 2. 전체 인테리어 한 집이라고 주의 해달라고 했으나 - 바닥 장판 밀림 - 벽도배지 찢김 (모르는 일처럼 우리에게 확인해달라고 함_인테리어 업체가 전날찍은 사진에는 찢김없음) 3. 침대 사이즈때문에 사다리차를 중간에 옮겨야한다며 견적서에 없는 15만원 추가 됨 고객이 불안하여 이사업체에 알림은 원치 않아 고객정보 없이 안내드립니다.',
                'sFile': '',
                'sCheck': '확인 불필요',
                'sWorker': '아네스',
                'fComplain': 0.2
            },
            {
                'sTimeStamp': '2025. 9. 19 오후 7:30:14',
                'sCompanyName': '부산9',
                'sPass': 'A/S 접수 게시글',
                'sComplain': '거실화장실 라디에이터 철거하면서 설비가 제대로 안되어 아랫집에 누수 발생',
                'sComplainPost': 'https://cafe.naver.com/pcarpenter/846092',
                'sPost': 'https://cafe.naver.com/pcarpenter/825708',
                'sSMSBool': '발송',
                'sSMSMent': '상기 내용으로 A/S 건이 접수되었음을 알려드립니다. 빠른 해명 댓글과 빠른 조치 요청드립니다.',
                'sFile': '',
                'sCheck': '계약 확인',
                'sWorker': '비비안',
                'fComplain': 0.2
            },
            {
                'sTimeStamp': '2025. 9. 20 오후 6:41:10',
                'sCompanyName': '입주청소5',
                'sPass': 'A/S 접수 게시글',
                'sComplain': '입주청소 깨끗이 안하시네요.',
                'sComplainPost': 'https://cafe.naver.com/pcarpenter/846212',
                'sPost': 'https://cafe.naver.com/pcarpenter/840488',
                'sSMSBool': '발송',
                'sSMSMent': '상기 내용으로 A/S 건이 접수되었음을 알려드립니다. 빠른 해명 댓글과 빠른 조치 요청드립니다.',
                'sFile': '',
                'sCheck': '확인 불필요',
                'sWorker': '비비안',
                'fComplain': 0.2
            },
            {
                'sTimeStamp': '2025. 9. 22 오후 10:57:16',
                'sCompanyName': '경기27',
                'sPass': '문자',
                'sComplain': '상담 지체 - 아직까지 연락 없는걸로봐서는 접수가 안된걸까요?',
                'sComplainPost': '',
                'sPost': 'https://cafe.naver.com/pcarpenter/845608',
                'sSMSBool': '',
                'sSMSMent': '상기 내용으로 고객불만건이 접수되었음을 알려드리며, 빠른 상담 요청드립니다.',
                'sFile': '',
                'sCheck': '확인 불필요',
                'sWorker': '제니',
                'fComplain': 0.2
            },
            {
                'sTimeStamp': '2025. 9. 23 오전 7:16:46',
                'sCompanyName': '서울27',
                'sPass': 'A/S 접수 게시글',
                'sComplain': '두번이나 AS 받았으나 여전히 엉망',
                'sComplainPost': 'https://cafe.naver.com/pcarpenter/846521',
                'sPost': 'https://cafe.naver.com/pcarpenter/825780',
                'sSMSBool': '발송',
                'sSMSMent': '상기 내용으로 고객불만건이 접수되었음을 알려드리며, 빠른 해명 댓글과 빠른 조치 요청드립니다.',
                'sFile': '',
                'sCheck': '계약 확인',
                'sWorker': '댄',
                'fComplain': 0.2
            },
            {
                'sTimeStamp': '2025. 9. 23 오전 9:41:56',
                'sCompanyName': '서울31',
                'sPass': 'A/S 접수 게시글',
                'sComplain': '창고 공간에 선반을 만들면서 박은 못에 벽 속의 우수관이 손상됐다고 합니다. 그 틈으로 물이 흘러서 벽이 이렇게 된거 같다는 결론이고요, 인테리어 업체에서도 한번 와서 보셔야 될 것 같아요.',
                'sComplainPost': 'https://cafe.naver.com/pcarpenter/846533',
                'sPost': 'https://cafe.naver.com/pcarpenter/774382',
                'sSMSBool': '발송',
                'sSMSMent': '상기 내용으로 A/S 건이 접수되었음을 알려드립니다. 빠른 해명 댓글과 빠른 조치 요청드립니다.',
                'sFile': '',
                'sCheck': '계약 확인',
                'sWorker': '아네스',
                'fComplain': 0.2
            }
        ]

        # 기존 Complain 데이터 백업
        existing_complains = list(Complain.objects.all().values())
        self.stdout.write(self.style.WARNING(f'\n기존 Complain 데이터 {len(existing_complains)}건을 백업합니다...'))

        # 백업 파일로 저장
        with open('complain_backup.json', 'w', encoding='utf-8') as f:
            json.dump(existing_complains, f, ensure_ascii=False, indent=2, default=str)
        self.stdout.write(self.style.SUCCESS('✓ 백업 완료: complain_backup.json'))

        # 트랜잭션 시작
        with transaction.atomic():
            # 기존 데이터 삭제
            Complain.objects.all().delete()
            self.stdout.write(self.style.WARNING('✓ 기존 Complain 데이터 삭제 완료'))

            # 새 데이터 입력
            success_count = 0
            error_count = 0
            company_not_found = []

            for data in new_complain_data:
                try:
                    # timeStamp 변환 (한국어 날짜 형식 파싱)
                    timestamp_str = data['sTimeStamp']
                    # "2025. 8. 6 오후 6:52:09" 형식 파싱
                    timestamp_str = timestamp_str.replace('오전', 'AM').replace('오후', 'PM')
                    timestamp = datetime.strptime(timestamp_str, '%Y. %m. %d %p %I:%M:%S')

                    # Company 매칭 (sName2로 검색)
                    company_name = data['sCompanyName']

                    # TODO(human): Company 매칭 로직 구현
                    # "경기9" → "경기9호", "시스템에어컨5" → "시스템에어컨5호" 변환
                    # 특수 케이스도 고려 필요
                    no_company = 0
                    company_not_found.append(company_name)

                    # Complain 객체 생성
                    complain = Complain(
                        sTimeStamp=data['sTimeStamp'],
                        timeStamp=timestamp,
                        sCompanyName=data['sCompanyName'],
                        noCompany=no_company,
                        sPass=data['sPass'],
                        sComplain=data['sComplain'],
                        sComplainPost=data['sComplainPost'],
                        sPost=data['sPost'],
                        sSMSBool=data['sSMSBool'],
                        sSMSMent=data['sSMSMent'],
                        sFile=data['sFile'],
                        sCheck=data['sCheck'],
                        sWorker=data['sWorker'],
                        fComplain=data['fComplain']
                    )
                    complain.save()
                    success_count += 1

                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'오류 발생 ({data["sTimeStamp"]}): {str(e)}'))
                    error_count += 1

        # 결과 출력
        self.stdout.write(self.style.SUCCESS(f'\n===== 작업 완료 ====='))
        self.stdout.write(self.style.SUCCESS(f'✓ 성공: {success_count}건'))
        if error_count > 0:
            self.stdout.write(self.style.ERROR(f'✗ 실패: {error_count}건'))

        if company_not_found:
            self.stdout.write(self.style.WARNING(f'\n매칭되지 않은 업체명 (noCompany=0으로 설정):'))
            for name in set(company_not_found):
                self.stdout.write(self.style.WARNING(f'  - {name}'))

        # 최종 데이터 확인
        final_count = Complain.objects.count()
        self.stdout.write(self.style.SUCCESS(f'\n최종 Complain 데이터 수: {final_count}건'))