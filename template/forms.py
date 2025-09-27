from django import forms
from .models import Template


class TemplateForm(forms.ModelForm):
    """템플리트 폼"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 새로 추가하는 경우에만 초기값 설정
        if not self.instance.pk:
            self.fields['nReceiver'].initial = 2  # 고객
            self.fields['nType'].initial = 0  # 문자

    class Meta:
        model = Template
        fields = ['nReceiver', 'nType', 'sTitle', 'sContent']
        widgets = {
            'nReceiver': forms.Select(attrs={
                'class': 'form-control',
                'style': 'width: 200px;'
            }),
            'nType': forms.Select(attrs={
                'class': 'form-control',
                'style': 'width: 200px;'
            }),
            'sTitle': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '제목을 입력하세요'
            }),
            'sContent': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 10,
                'placeholder': '내용을 입력하세요'
            }),
        }
        labels = {
            'nReceiver': '수신대상',
            'nType': '구분',
            'sTitle': '제목',
            'sContent': '내용',
        }