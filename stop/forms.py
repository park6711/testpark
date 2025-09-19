from django import forms
from .models import Stop
from company.models import Company


class StopForm(forms.ModelForm):
    """일시정지 생성/수정 폼"""

    class Meta:
        model = Stop
        fields = ['noCompany', 'dateStart', 'dateEnd', 'sStop', 'bShow', 'sWorker']

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

        self.fields['sStop'].widget = forms.Textarea(
            attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': '일시정지 사유를 자세히 입력해주세요...',
                'required': True
            }
        )
        self.fields['sStop'].label = '일시정지 사유'

        self.fields['bShow'].widget = forms.RadioSelect(
            choices=[
                (True, '업체에 공개'),
                (False, '업체에 비공개')
            ],
            attrs={
                'class': 'form-radio'
            }
        )
        self.fields['bShow'].label = '공개 여부'
        self.fields['bShow'].help_text = ''  # 설명 삭제
        self.fields['bShow'].initial = True  # 기본값을 공개로 설정

        self.fields['sWorker'].widget = forms.TextInput(
            attrs={
                'class': 'form-control',
                'readonly': True,
                'style': 'background-color: #f8f9fa; cursor: not-allowed;'
            }
        )
        self.fields['sWorker'].label = '설정자'
        self.fields['sWorker'].help_text = '현재 로그인한 스텝이 자동으로 설정됩니다'

    def get_company_choices(self):
        """업체 선택 옵션 생성 (Company.sName2 사용)"""
        choices = [('', '-- 열린업체를 선택하세요 --')]

        try:
            companies = Company.objects.all().order_by('no')

            for company in companies:
                # sName2를 우선 사용, 없으면 sName1, 그것도 없으면 업체번호
                sname2 = getattr(company, 'sName2', None)
                sname1 = getattr(company, 'sName1', None)

                if sname2 and sname2.strip():
                    company_name = sname2
                elif sname1 and sname1.strip():
                    company_name = sname1
                else:
                    company_name = f'업체번호 {company.no}'

                choice_text = company_name
                choices.append((company.no, choice_text))

        except Exception as e:
            print(f"Company 테이블 조회 오류: {e}")
            # License에서 업체 정보 가져오기 (대안)
            try:
                from license.models import License
                licenses = License.objects.all().order_by('noCompany')
                for license_obj in licenses:
                    choices.append((license_obj.noCompany, f"{license_obj.noCompany}. {license_obj.sCompanyName}"))
            except Exception as e2:
                print(f"License에서 업체 목록 조회 오류: {e2}")

        return choices

    def clean(self):
        """폼 유효성 검증"""
        cleaned_data = super().clean()
        date_start = cleaned_data.get('dateStart')
        date_end = cleaned_data.get('dateEnd')

        if date_start and date_end:
            if date_start > date_end:
                raise forms.ValidationError('시작일은 종료일보다 빨라야 합니다.')

        return cleaned_data