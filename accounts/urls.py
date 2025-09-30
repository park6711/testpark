"""
accounts 앱 URL 설정
"""

from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # 로그인 페이지
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),

    # 통합 네이버 로그인 (Staff/Member 자동 구분)
    path('naver/login/', views.UnifiedNaverLoginView.as_view(), name='unified_naver_login'),
    path('naver/callback/', views.UnifiedNaverCallbackView.as_view(), name='unified_naver_callback'),

    # 네이버 앱에 등록된 콜백 URL (통합 콜백으로 처리)
    path('company/naver/callback/', views.UnifiedNaverCallbackView.as_view(), name='company_naver_callback'),

    # 인증번호 관련
    path('verify/', views.VerifyCodeView.as_view(), name='verify_code'),
    path('resend-code/', views.resend_auth_code, name='resend_auth_code'),


    # 계정 전환
    path('switch-account/', views.SwitchAccountView.as_view(), name='switch_account'),
]