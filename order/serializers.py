from rest_framework import serializers
from .models import Order, Assign, Estimate, AssignMemo
from company.models import Company
from area.models import Area

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
            'no', 'time', 'designation', 'designation_type', 'sNick', 'sNaverID',
            'sName', 'sPhone', 'post_link', 'sArea', 'dateSchedule',
            'sConstruction', 'assigned_company', 'recent_status', 're_request_count',
            'bPrivacy1', 'bPrivacy2', 'created_at', 'updated_at'
        ]
        read_only_fields = ['no', 'time', 'created_at', 'updated_at']

class AssignSerializer(serializers.ModelSerializer):
    construction_type_display = serializers.CharField(source='get_nConstructionType_display', read_only=True)
    assign_type_display = serializers.CharField(source='get_nAssignType_display', read_only=True)
    appoint_type_display = serializers.CharField(source='get_nAppoint_display', read_only=True)
    company_name = serializers.CharField(source='get_company_name', read_only=True)
    area_name = serializers.CharField(source='get_area_name', read_only=True)
    status_color = serializers.CharField(source='get_status_color', read_only=True)
    order_detail = serializers.SerializerMethodField()

    class Meta:
        model = Assign
        fields = [
            'no', 'noOrder', 'time', 'noCompany', 'nConstructionType',
            'nAssignType', 'sCompanyPhone', 'sCompanySMS', 'sClientPhone',
            'sClientSMS', 'sWorker', 'noCompanyReport', 'nAppoint',
            'noGonggu', 'noArea', 'construction_type_display',
            'assign_type_display', 'appoint_type_display', 'company_name',
            'area_name', 'status_color', 'order_detail', 'created_at', 'updated_at'
        ]
        read_only_fields = ['no', 'time', 'created_at', 'updated_at']

    def get_order_detail(self, obj):
        order = obj.get_order()
        if order:
            return {
                'no': order.no,
                'sName': order.sName,
                'sPhone': order.sPhone,
                'sArea': order.sArea,
                'dateSchedule': order.dateSchedule
            }
        return None

class EstimateSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='get_company_name', read_only=True)
    client_name = serializers.CharField(source='get_client_name', read_only=True)
    construction_type = serializers.CharField(source='get_construction_type', read_only=True)
    summary = serializers.CharField(source='get_summary', read_only=True)
    is_recent = serializers.BooleanField(read_only=True)

    class Meta:
        model = Estimate
        fields = [
            'no', 'noOrder', 'noAssign', 'time', 'sPost',
            'company_name', 'client_name', 'construction_type',
            'summary', 'is_recent', 'created_at', 'updated_at'
        ]
        read_only_fields = ['no', 'time', 'created_at', 'updated_at']

class AssignMemoSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='get_company_name', read_only=True)
    client_name = serializers.CharField(source='get_client_name', read_only=True)
    memo_preview = serializers.CharField(source='get_memo_preview', read_only=True)
    assign_status = serializers.CharField(source='get_assign_status', read_only=True)
    summary = serializers.CharField(source='get_summary', read_only=True)
    is_recent = serializers.BooleanField(read_only=True)
    is_important = serializers.BooleanField(read_only=True)

    class Meta:
        model = AssignMemo
        fields = [
            'no', 'noOrder', 'noAssign', 'time', 'sWorker', 'sMemo',
            'company_name', 'client_name', 'memo_preview', 'assign_status',
            'summary', 'is_recent', 'is_important', 'created_at', 'updated_at'
        ]
        read_only_fields = ['no', 'time', 'created_at', 'updated_at']

class OrderDetailSerializer(serializers.ModelSerializer):
    assigns = serializers.SerializerMethodField()
    estimates = serializers.SerializerMethodField()
    memos = serializers.SerializerMethodField()
    privacy_status = serializers.CharField(source='get_privacy_status', read_only=True)
    schedule_status = serializers.CharField(source='get_schedule_status', read_only=True)
    is_urgent = serializers.BooleanField(read_only=True)

    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = ['no', 'time', 'created_at', 'updated_at']

    def get_assigns(self, obj):
        assigns = Assign.objects.filter(noOrder=obj.no).order_by('-no')
        return AssignSerializer(assigns, many=True).data

    def get_estimates(self, obj):
        estimates = Estimate.objects.filter(noOrder=obj.no).order_by('-no')
        return EstimateSerializer(estimates, many=True).data

    def get_memos(self, obj):
        memos = AssignMemo.objects.filter(noOrder=obj.no).order_by('-no')
        return AssignMemoSerializer(memos, many=True).data

class OrderCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
            'sAppoint', 'sNick', 'sNaverID', 'sName', 'sPhone',
            'sPost', 'sArea', 'dateSchedule', 'sConstruction',
            'bPrivacy1', 'bPrivacy2'
        ]

    def validate(self, data):
        if not data.get('sName'):
            raise serializers.ValidationError("고객명은 필수 입력 항목입니다.")
        if not data.get('sPhone'):
            raise serializers.ValidationError("연락처는 필수 입력 항목입니다.")
        if not data.get('bPrivacy1'):
            raise serializers.ValidationError("개인정보 동의는 필수입니다.")
        return data

class AssignCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assign
        fields = [
            'noOrder', 'noCompany', 'nConstructionType', 'nAssignType',
            'sCompanyPhone', 'sCompanySMS', 'sClientPhone', 'sClientSMS',
            'sWorker', 'noCompanyReport', 'nAppoint', 'noGonggu', 'noArea'
        ]

    def validate(self, data):
        if not data.get('noOrder'):
            raise serializers.ValidationError("의뢰 ID는 필수입니다.")
        if not data.get('noCompany'):
            raise serializers.ValidationError("업체 ID는 필수입니다.")

        try:
            Order.objects.get(no=data.get('noOrder'))
        except Order.DoesNotExist:
            raise serializers.ValidationError("유효하지 않은 의뢰 ID입니다.")

        return data

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['no', 'sCompanyName', 'sRepPhone', 'sArea', 'bStatus']

class AreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area
        fields = ['no', 'sArea', 'sType']

class BulkUpdateSerializer(serializers.Serializer):
    order_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=True,
        min_length=1
    )
    assign_type = serializers.IntegerField(required=False)
    company_id = serializers.IntegerField(required=False)
    worker = serializers.CharField(required=False, allow_blank=True)

    def validate(self, data):
        if not data.get('assign_type') and not data.get('company_id'):
            raise serializers.ValidationError("할당 상태나 업체 ID 중 하나는 필수입니다.")
        return data

class MessageTemplateSerializer(serializers.Serializer):
    template_id = serializers.CharField(required=True)
    recipient_type = serializers.CharField(required=True)
    order_id = serializers.IntegerField(required=True)
    custom_message = serializers.CharField(required=False, allow_blank=True)

    def validate_recipient_type(self, value):
        valid_types = ['company', 'client', 'both']
        if value not in valid_types:
            raise serializers.ValidationError(f"수신자 유형은 {valid_types} 중 하나여야 합니다.")
        return value