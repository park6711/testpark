from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Q, Count, Prefetch
from django.db import transaction
from datetime import datetime
import json

# Google Sheets Sync는 조건부 import
try:
    from .google_sheets_sync import GoogleSheetsSync
    GOOGLE_SHEETS_ENABLED = True
except ImportError:
    GOOGLE_SHEETS_ENABLED = False

from .models import (
    Order, Assign, Estimate, AssignMemo,
    ChangeHistory, StatusHistory, QuoteLink, QuoteDraft,
    Memo, GroupPurchase, MessageTemplate
)
from .serializers import (
    OrderSerializer, OrderDetailSerializer, OrderCreateUpdateSerializer,
    AssignSerializer, AssignCreateUpdateSerializer,
    EstimateSerializer, AssignMemoSerializer,
    CompanySerializer, AreaSerializer,
    BulkUpdateSerializer, MessageTemplateSerializer
)
from company.models import Company
from area.models import Area


class OrderViewSet(viewsets.ModelViewSet):
    """의뢰(Order) ViewSet"""
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [AllowAny]  # 개발 중에는 AllowAny, 프로덕션에서는 IsAuthenticated

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return OrderDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return OrderCreateUpdateSerializer
        return OrderSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        # Get query parameters (handle both DRF and Django request objects)
        params = getattr(self.request, 'query_params', self.request.GET)

        # 검색 필터
        search = params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(sName__icontains=search) |
                Q(sPhone__icontains=search) |
                Q(sNaverID__icontains=search) |
                Q(sNick__icontains=search) |
                Q(sArea__icontains=search) |
                Q(sConstruction__icontains=search)
            )

        # 상태 필터
        status_filter = params.get('status', None)
        if status_filter:
            queryset = queryset.filter(recent_status=status_filter)

        # 날짜 필터
        date_from = params.get('date_from', None)
        date_to = params.get('date_to', None)
        if date_from:
            queryset = queryset.filter(created_at__date__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__date__lte=date_to)

        # 관련 데이터 미리 로드 (N+1 쿼리 방지)
        queryset = queryset.prefetch_related(
            'change_histories',
            'status_histories',
            'quote_links__drafts',
            'memos'
        )

        return queryset.order_by('-created_at')

    @action(detail=True, methods=['post'])
    def update_field(self, request, pk=None):
        """필드 개별 수정 및 이력 기록"""
        order = self.get_object()
        field_name = request.data.get('field_name')
        field_label = request.data.get('field_label')
        new_value = request.data.get('new_value')
        author = request.data.get('author', '관리자')

        # 이전 값 저장
        old_value = getattr(order, field_name, '')

        # 필드 업데이트
        setattr(order, field_name, new_value)
        order.save()

        # 변경 이력 저장
        if str(old_value) != str(new_value):
            ChangeHistory.objects.create(
                order=order,
                field_name=field_name,
                field_label=field_label,
                old_value=str(old_value),
                new_value=str(new_value),
                author=author
            )

        return Response({'status': 'success', 'message': '필드가 수정되었습니다.'})

    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """상태 변경 및 이력 기록"""
        order = self.get_object()
        new_status = request.data.get('status')
        message_sent = request.data.get('message_sent', False)
        message_content = request.data.get('message_content', '')
        recipient_type = request.data.get('recipient', '업체+고객')
        author = request.data.get('author', '관리자')

        # 상태 전환 규칙 확인
        STATUS_TRANSITIONS = {
            '대기중': ['할당', '업체미비', '중복접수', '연락처오류', '가능문의', '고객문의'],
            '할당': ['반려', '취소', '제외', '연락처오류', '계약'],
            '연락처오류': ['대기중', '할당'],
            '가능문의': ['할당', '불가능답변(X)'],
            '반려': ['대기중', '할당', '계약'],
            '고객문의': ['대기중', '할당'],
            '취소': ['계약'],
            '제외': [],
            '업체미비': ['대기중'],
            '중복접수': [],
            '불가능답변(X)': ['대기중'],
            '계약': []
        }

        current_status = order.recent_status
        allowed_transitions = STATUS_TRANSITIONS.get(current_status, [])

        if new_status not in allowed_transitions and new_status != current_status:
            return Response({
                'status': 'error',
                'message': f'{current_status}에서 {new_status}(으)로 변경할 수 없습니다.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # 상태 변경 이력 저장
        if current_status != new_status:
            StatusHistory.objects.create(
                order=order,
                old_status=current_status,
                new_status=new_status,
                message_sent=message_sent,
                message_content=message_content,
                author=author
            )

            # 상태 업데이트
            order.recent_status = new_status
            order.save()

            # TODO: 실제 문자 발송 로직 구현
            if message_sent:
                self._send_message(order, message_content, recipient_type)

        return Response({'status': 'success', 'message': '상태가 변경되었습니다.'})

    @action(detail=True, methods=['post'])
    def add_memo(self, request, pk=None):
        """메모 추가"""
        order = self.get_object()
        content = request.data.get('content')
        author = request.data.get('author', '관리자')

        memo = Memo.objects.create(
            order=order,
            content=content,
            author=author
        )

        return Response({
            'status': 'success',
            'memo': {
                'id': memo.no,
                'content': memo.content,
                'author': memo.author,
                'datetime': memo.datetime.strftime('%Y-%m-%d %H:%M')
            }
        })

    @action(detail=True, methods=['post'])
    def add_quote_link(self, request, pk=None):
        """견적서 링크 추가"""
        order = self.get_object()
        draft_type = request.data.get('draft_type', '초안')
        link = request.data.get('link')

        # QuoteLink 찾기 또는 생성
        quote_link, created = QuoteLink.objects.get_or_create(order=order)

        # Draft 추가
        draft = QuoteDraft.objects.create(
            quote_link=quote_link,
            draft_type=draft_type,
            link=link
        )

        return Response({
            'status': 'success',
            'draft': {
                'id': draft.no,
                'type': draft.draft_type,
                'link': draft.link,
                'datetime': draft.datetime.strftime('%Y-%m-%d %H:%M')
            }
        })

    @action(detail=True, methods=['get'])
    def quote_count(self, request, pk=None):
        """견적서 개수 조회"""
        order = self.get_object()
        try:
            quote_link = order.quote_links.first()
            if quote_link:
                count = quote_link.drafts.count()
            else:
                count = 0
        except:
            count = 0

        return Response({'count': count})

    @action(detail=True, methods=['get'])
    def memo_count(self, request, pk=None):
        """메모 개수 조회"""
        order = self.get_object()
        count = order.memos.count()
        return Response({'count': count})

    @action(detail=False, methods=['post'])
    def bulk_delete(self, request):
        """선택 항목 일괄 삭제"""
        order_ids = request.data.get('order_ids', [])

        if not order_ids:
            return Response({
                'status': 'error',
                'message': '삭제할 항목을 선택하세요.'
            }, status=status.HTTP_400_BAD_REQUEST)

        deleted_count = Order.objects.filter(no__in=order_ids).delete()[0]

        return Response({
            'status': 'success',
            'message': f'{deleted_count}개 항목이 삭제되었습니다.'
        })

    @action(detail=True, methods=['post'])
    def copy(self, request, pk=None):
        """의뢰 복사"""
        order = self.get_object()

        # 새 의뢰 생성
        new_order = Order.objects.create(
            designation=order.designation,
            designation_type=order.designation_type,
            sNick=order.sNick,
            sNaverID=order.sNaverID,
            sName=order.sName,
            sPhone=order.sPhone,
            sArea=order.sArea,
            dateSchedule=order.dateSchedule,
            sConstruction=order.sConstruction,
            recent_status='대기중',
            re_request_count=0,
            bPrivacy1=order.bPrivacy1,
            bPrivacy2=order.bPrivacy2
        )

        serializer = self.get_serializer(new_order)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def assign_companies(self, request):
        """업체 할당 - 11.tsx 로직과 동일하게 구현"""
        order_no = request.data.get('order_no')
        company_ids = request.data.get('company_ids', [])
        designation_type = request.data.get('designation_type', '지정없음')
        group_purchase_id = request.data.get('group_purchase_id')

        if not order_no:
            return Response({
                'success': False,
                'message': '의뢰 번호가 필요합니다.'
            }, status=status.HTTP_400_BAD_REQUEST)

        if not company_ids:
            return Response({
                'success': False,
                'message': '할당할 업체를 선택해주세요.'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            order = Order.objects.get(no=order_no)
        except Order.DoesNotExist:
            return Response({
                'success': False,
                'message': '의뢰를 찾을 수 없습니다.'
            }, status=status.HTTP_404_NOT_FOUND)

        # 같은 게시글(post_link)의 이미 할당된 업체들 확인
        existing_assignments = set()
        if order.post_link:
            existing_assignments = set(
                Order.objects.filter(post_link=order.post_link)
                .exclude(assigned_company='')
                .values_list('assigned_company', flat=True)
            )

        assigned_orders = []
        first_item_assigned = False

        # 선택된 업체들 처리
        with transaction.atomic():
            for company_id in company_ids:
                try:
                    company = Company.objects.get(no=company_id)
                    company_name = f"{company.sCompanyName} {company.sAddress}" if company.sAddress else company.sCompanyName

                    # 이미 할당된 업체는 스킵
                    if company_name in existing_assignments:
                        continue

                    # 첫 번째 업체이고 현재 행에 할당된 업체가 없으면 현재 행 업데이트
                    if not first_item_assigned and not order.assigned_company:
                        order.assigned_company = company_name
                        order.recent_status = '대기중'
                        order.designation_type = designation_type
                        order.save()

                        assigned_orders.append(order)
                        first_item_assigned = True
                        existing_assignments.add(company_name)
                    else:
                        # 추가 업체는 새 행 생성 (의뢰 복사)
                        new_order = Order.objects.create(
                            designation=order.designation,
                            designation_type=designation_type,
                            sNick=order.sNick,
                            sNaverID=order.sNaverID,
                            sName=order.sName,
                            sPhone=order.sPhone,
                            sPost=order.sPost,
                            post_link=order.post_link,
                            sArea=order.sArea,
                            dateSchedule=order.dateSchedule,
                            sConstruction=order.sConstruction,
                            assigned_company=company_name,
                            recent_status='대기중',
                            re_request_count=order.re_request_count,
                            bPrivacy1=order.bPrivacy1,
                            bPrivacy2=order.bPrivacy2,
                            google_sheet_uuid=None  # 복사본은 UUID 없음
                        )
                        assigned_orders.append(new_order)
                        existing_assignments.add(company_name)

                except Company.DoesNotExist:
                    continue

        return Response({
            'success': True,
            'assigned_count': len(assigned_orders),
            'message': f'{len(assigned_orders)}개 업체가 할당되었습니다.',
            'assigned_order_ids': [o.no for o in assigned_orders]
        }, status=status.HTTP_200_OK)

    def _send_message(self, order, message_content, recipient_type):
        """실제 문자 발송 로직 (구현 필요)"""
        # TODO: SMS API 연동
        pass


class AssignViewSet(viewsets.ModelViewSet):
    """할당(Assign) ViewSet"""
    queryset = Assign.objects.all()
    serializer_class = AssignSerializer
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return AssignCreateUpdateSerializer
        return AssignSerializer


class GroupPurchaseViewSet(viewsets.ModelViewSet):
    """공동구매 ViewSet"""
    queryset = GroupPurchase.objects.filter(is_active=True)
    permission_classes = [AllowAny]

    def list(self, request):
        """공동구매 목록 조회"""
        purchases = self.get_queryset()
        data = []

        for purchase in purchases:
            data.append({
                'id': purchase.no,
                'round': purchase.round,
                'company': purchase.company_name,
                'unavailable_dates': purchase.unavailable_dates,
                'available_areas': purchase.available_areas,
                'name': purchase.name,
                'link': purchase.link
            })

        return Response(data)

    @action(detail=True, methods=['post'])
    def check_availability(self, request, pk=None):
        """공동구매 가능 여부 확인"""
        purchase = self.get_object()
        scheduled_date = request.data.get('scheduled_date')
        area = request.data.get('area')

        if scheduled_date:
            scheduled_date = datetime.strptime(scheduled_date, '%Y-%m-%d').date()

        result = purchase.check_availability(scheduled_date, area)
        return Response(result)


class MessageTemplateViewSet(viewsets.ModelViewSet):
    """메시지 템플릿 ViewSet"""
    queryset = MessageTemplate.objects.filter(is_active=True)
    permission_classes = [AllowAny]

    def list(self, request):
        """템플릿 목록 조회"""
        templates = self.get_queryset()
        data = {}

        for template in templates:
            data[template.name] = template.content

        return Response(data)

    @action(detail=True, methods=['post'])
    def render(self, request, pk=None):
        """템플릿 렌더링"""
        template = self.get_object()
        context = request.data.get('context', {})
        rendered = template.render(context)

        return Response({'rendered': rendered})


class CompanyViewSet(viewsets.ReadOnlyModelViewSet):
    """업체 ViewSet"""
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [AllowAny]

    def list(self, request):
        """업체 목록 조회"""
        companies = self.get_queryset()
        data = []

        for company in companies:
            data.append({
                'no': company.no,
                'sCompanyName': company.sCompanyName,
                'sAddress': company.sAddress or '',
                'grade': company.nGrade or 4,
                'license': company.sBuildLicense or '-',
                'specialty': company.sStrength or '-',
                'assignCount': 0  # TODO: 할당 횟수 계산
            })

        return Response(data)


class AreaViewSet(viewsets.ReadOnlyModelViewSet):
    """지역 ViewSet"""
    queryset = Area.objects.all()
    serializer_class = AreaSerializer
    permission_classes = [AllowAny]

    def list(self, request):
        """지역 목록 조회"""
        areas = self.get_queryset()
        regions = [area.sArea for area in areas]
        return Response(regions)


@api_view(['POST'])
@permission_classes([AllowAny])  # 인증 없이 접근 가능
def sync_google_sheets(request):
    """구글 스프레드시트 데이터 동기화 API"""
    if not GOOGLE_SHEETS_ENABLED:
        return Response({
            'success': False,
            'message': '구글 스프레드시트 동기화가 비활성화되어 있습니다. gspread 패키지를 설치하세요.'
        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    try:
        sync = GoogleSheetsSync()
        result = sync.sync_data()

        return Response({
            'success': True,
            'message': '동기화 완료',
            'result': result
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            'success': False,
            'message': f'동기화 실패: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)