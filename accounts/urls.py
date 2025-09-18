"""
accounts 앱 URL 설정
"""

from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # 로그인 관련
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),

    # 네이버 소셜 로그인
    path('naver/', views.NaverLoginView.as_view(), name='naver_login'),
    path('naver/callback/', views.NaverCallbackView.as_view(), name='naver_callback'),

    # 스텝 네이버 소셜 로그인
    path('staff/naver/', views.StaffNaverLoginView.as_view(), name='staff_naver_login'),

    # 인증번호 관련
    path('verify/', views.VerifyCodeView.as_view(), name='verify_code'),
    path('resend-code/', views.resend_auth_code, name='resend_auth_code'),
]