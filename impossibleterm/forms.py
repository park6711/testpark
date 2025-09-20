from django import forms
from .models import ImpossibleTerm
from company.models import Company


class ImpoForm(forms.ModelForm):
    """공사 불가능 기간 생성/수정 폼"""

    class Meta:
        model = ImpossibleTerm
        fields = ['noCompany', 'dateStart', 'dateEnd', 'sWorker']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 필드 위젯 및 속성 설정
        self.fields['noCompany'].widget = forms.Select(
            choices=self.get_company_choices(),
            attrs={
                'class': 'form-control company-select',
                'required': True,
                'data-live-search': 'true'
            }
        )
        self.fields['noCompany'].label = '열린업체'

        # 시작일 기본값을 오늘로 설정 (한국 시간 기준)
        from django.utils import timezone
        today = timezone.localtime().date()

        self.fields['dateStart'].widget = forms.DateInput(
            attrs={
                'type': 'date',
                'class': 'form-control',
                'required': True
            }
        )
        self.fields['dateStart'].label = '시작일'
        self.fields['dateStart'].initial = today
        self.fields['dateStart'].help_text = f'오늘은 {today.strftime("%Y년 %m월 %d일")}입니다.'

        self.fields['dateEnd'].widget = forms.DateInput(
            attrs={
                'type': 'date',
                'class': 'form-control',
                'required': False
            }
        )
        self.fields['dateEnd'].label = '종료일'
        self.fields['dateEnd'].help_text = '입력하지 않으면 2099년까지 자동 설정됩니다.'

        # 설정자 필드
        self.fields['sWorker'].widget = forms.TextInput(
            attrs={
                'class': 'form-control',
                'readonly': True,
                'style': 'background-color: #f8f9fa; border-color: #dee2e6;'
            }
        )
        self.fields['sWorker'].label = '설정자'
        self.fields['sWorker'].help_text = '현재 로그인한 스텝이 자동으로 설정됩니다.'

    def get_company_choices(self):
        """업체 선택 옵션 반환"""
        companies = Company.objects.all().order_by('no')
        choices = [('', '--- 업체를 선택하세요 ---')]

        for company in companies:
            # sName2가 있으면 우선 사용, 없으면 sName1 사용
            company_name = company.sName2 or company.sName1 or f"업체{company.no}"
            choices.append((company.no, company_name))

        return choices

    def save(self, commit=True):
        """저장 시 종료일이 없으면 2099-12-31로 설정"""
        instance = super().save(commit=False)

        if not instance.dateEnd:
            from datetime import date
            instance.dateEnd = date(2099, 12, 31)

        if commit:
            instance.save()
        return instance