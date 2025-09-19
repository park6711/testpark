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

    # 업체(일반) 네이버 소셜 로그인
    path('company/naver/login/', views.CompanyNaverLoginView.as_view(), name='company_naver_login'),
    path('company/naver/callback/', views.CompanyNaverCallbackView.as_view(), name='company_naver_callback'),

    # 스텝 네이버 소셜 로그인
    path('staff/naver/login/', views.StaffNaverLoginView.as_view(), name='staff_naver_login'),
    path('staff/naver/callback/', views.StaffNaverCallbackView.as_view(), name='staff_naver_callback'),

    # 인증번호 관련
    path('verify/', views.VerifyCodeView.as_view(), name='verify_code'),
    path('resend-code/', views.resend_auth_code, name='resend_auth_code'),
]