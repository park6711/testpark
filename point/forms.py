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
                'placeholder': '사용 포인트를 입력하세요',
                'min': 0,
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

        # 업체 목록 필터링 (살아있는 업체만)
        self.fields['noCompany'].queryset = Company.objects.filter(
            bAlive=True
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
        """사용 포인트 검증"""
        nUsePoint = self.cleaned_data.get('nUsePoint')
        if nUsePoint is None:
            nUsePoint = 0
        if nUsePoint < 0:
            raise forms.ValidationError("사용 포인트는 0 이상이어야 합니다.")
        return nUsePoint

    def clean(self):
        """전체 검증"""
        cleaned_data = super().clean()
        noCompany = cleaned_data.get('noCompany')
        nUsePoint = cleaned_data.get('nUsePoint', 0)

        if self.instance.pk:  # 수정인 경우
            # 현재 포인트 잔액 확인
            current_remain = self.instance.nPrePoint
            new_remain = current_remain - nUsePoint

            if new_remain < 0:
                raise forms.ValidationError(
                    f"잔액이 마이너스가 될 수 없습니다. "
                    f"현재 이전 포인트: {current_remain:,}, "
                    f"사용 포인트: {nUsePoint:,}, "
                    f"예상 잔액: {new_remain:,}"
                )
        else:  # 신규 추가인 경우
            if noCompany:
                # 현재 포인트 잔액 확인
                last_point = Point.objects.filter(
                    noCompany=noCompany
                ).order_by('-time', '-no').first()

                if last_point:
                    current_remain = last_point.nRemainPoint
                else:
                    current_remain = 0

                new_remain = current_remain - nUsePoint

                if new_remain < 0:
                    raise forms.ValidationError(
                        f"잔액이 마이너스가 될 수 없습니다. "
                        f"현재 포인트: {current_remain:,}, "
                        f"사용 포인트: {nUsePoint:,}, "
                        f"예상 잔액: {new_remain:,}"
                    )

        return cleaned_data