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

    # 통합 네이버 로그인 (업체/스텝 선택 가능)
    path('naver/login/', views.CompanyNaverLoginView.as_view(), name='unified_naver_login'),

    # 업체(일반) 네이버 소셜 로그인
    path('company/naver/login/', views.CompanyNaverLoginView.as_view(), name='company_naver_login'),

    # 스텝 네이버 소셜 로그인
    path('staff/naver/login/', views.StaffNaverLoginView.as_view(), name='staff_naver_login'),

    # 네이버 계정 변경 모드 설정
    path('set-switch-mode/', views.SetSwitchModeView.as_view(), name='set_switch_mode'),

    # 통합 네이버 콜백 (신규 - /auth/naver/callback/)
    path('naver/callback/', views.NaverCallbackView.as_view(), name='naver_callback'),

    # 기존 업체 콜백 URL을 통합 콜백으로 사용 (업체/스텝 구분은 state로 처리)
    path('company/naver/callback/', views.NaverCallbackView.as_view(), name='company_naver_callback'),

    # 임시 테스트 로그인 (개발용)
    path('test/staff/login/', views.TestStaffLoginView.as_view(), name='test_staff_login'),
    path('test/company/login/', views.TestCompanyLoginView.as_view(), name='test_company_login'),

    # 인증번호 관련
    path('verify/', views.VerifyCodeView.as_view(), name='verify_code'),
    path('resend-code/', views.resend_auth_code, name='resend_auth_code'),
]