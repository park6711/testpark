from django.urls import path
from . import views

app_name = 'accounts_api'

urlpatterns = [
    # API 상태 확인
    path('status/', views.api_status, name='api_status'),

    # 사용자 관련 API
    path('users/', views.UserListAPIView.as_view(), name='user_list'),
    path('profile/', views.api_user_profile, name='user_profile'),
]