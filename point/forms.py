from django import forms
from .models import Point
from company.models import Company
from contract.models import CompanyReport


class PointForm(forms.ModelForm):
    """포인트 폼"""

    class Meta:
        model = Point
        fields = [
            'noCompany', 'nType', 'noCompanyReport',
            'nUsePoint', 'sMemo', 'sWorker'
        ]
        widgets = {
            'noCompany': forms.Select(attrs={
                'class': 'form-select',
                'required': True,
            }),
            'nType': forms.Select(attrs={
                'class': 'form-select',
            }),
            'noCompanyReport': forms.Select(attrs={
                'class': 'form-select',
            }),
            'nUsePoint': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '적용 포인트를 입력하세요',
            }),
            'sWorker': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '작업자명',
            }),
            'sMemo': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': '메모를 입력하세요',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 업체 목록 필터링 (활성 업체만)
        self.fields['noCompany'].queryset = Company.objects.filter(
            dateWithdraw__isnull=True
        ).order_by('sName2')

        # 업체 선택 시 label 변경
        self.fields['noCompany'].label_from_instance = lambda obj: f"{obj.sName2} ({obj.sName1})"

        # 계약보고 필터링
        self.fields['noCompanyReport'].queryset = CompanyReport.objects.all().order_by('-no')
        self.fields['noCompanyReport'].required = False
        self.fields['noCompanyReport'].empty_label = "--- 선택하지 않음 ---"

        # 계약보고 label 변경
        self.fields['noCompanyReport'].label_from_instance = lambda obj: f"#{obj.no} - {obj.get_nType_display()}"

    def clean_nUsePoint(self):
        """적용 포인트 검증"""
        nUsePoint = self.cleaned_data.get('nUsePoint')
        if nUsePoint is None or nUsePoint == 0:
            raise forms.ValidationError("적용 포인트는 0이 될 수 없습니다.")
        # 음수값도 허용 (포인트 적립)
        return nUsePoint

    def clean(self):
        """전체 검증"""
        cleaned_data = super().clean()
        # 잔액이 마이너스가 되는 것도 허용 (실제 비즈니스 요구사항에 따름)
        return cleaned_data