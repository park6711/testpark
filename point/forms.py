from django import forms
from .models import Point
from company.models import Company
from contract.models import CompanyReport


class PointForm(forms.ModelForm):
    """포인트 폼"""

    # Company 선택을 위한 커스텀 필드 추가
    company = forms.ModelChoiceField(
        queryset=Company.objects.none(),
        label='업체',
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-select company-select',
            'id': 'company-select',
        })
    )

    class Meta:
        model = Point
        fields = [
            'nType', 'noCompanyReport',
            'nUsePoint', 'sMemo', 'sWorker'
        ]
        widgets = {
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
        self.fields['company'].queryset = Company.objects.filter(
            dateWithdraw__isnull=True
        ).order_by('sName2')

        # 업체 선택 시 label 변경 (sName2를 메인으로 표시)
        self.fields['company'].label_from_instance = lambda obj: f"{obj.sName2}"

        # 빈 선택지 추가
        self.fields['company'].empty_label = "--- 업체를 선택하세요 ---"

        # 계약보고 필드를 ChoiceField로 변경
        self.fields['noCompanyReport'] = forms.ChoiceField(
            choices=[('', '--- 업체를 먼저 선택하세요 ---')],
            label='계약보고',
            required=False,
            widget=forms.Select(attrs={
                'class': 'form-select',
                'id': 'companyreport-select',
            })
        )

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

    def save(self, commit=True):
        """저장 시 company 필드 값을 noCompany에 매핑"""
        point = super().save(commit=False)
        if self.cleaned_data.get('company'):
            point.noCompany = self.cleaned_data['company'].no
        if commit:
            point.save()
        return point