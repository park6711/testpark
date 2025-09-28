from django.urls import path
from . import views
from . import views_webhook
from . import webhook_views

app_name = 'evaluation'

urlpatterns = [
    path('', views.evaluation_list, name='evaluation_list'),

    # 업체평가 회차 관리
    path('evaluation-no/', views.evaluation_no_list, name='evaluation_no_list'),
    path('evaluation-no/<int:pk>/', views.evaluation_no_detail, name='evaluation_no_detail'),
    path('evaluation-no/<int:pk>/edit/', views.evaluation_no_edit, name='evaluation_no_edit'),
    path('evaluation-no/update-field/', views.evaluation_no_update_field, name='evaluation_no_update_field'),

    # 고객불만 이력 관리
    path('complain/', views.complain_list, name='complain_list'),
    # complain_detail 제거 - 수정 기능 제거
    path('complain/<int:pk>/delete/', views.complain_delete, name='complain_delete'),
    path('complain/update-score/', views.complain_update_score, name='complain_update_score'),
    path('complain/update-check/', views.complain_update_check, name='complain_update_check'),

    # Google Sheets Webhook
    path('webhook/google-sheets/', views_webhook.google_sheets_webhook, name='google_sheets_webhook'),
    path('webhook/google-sheets-complain/', views_webhook.google_sheets_webhook_complain, name='google_sheets_webhook_complain'),
    path('webhook/test/', views_webhook.test_webhook, name='test_webhook'),

    # 고객만족도 이력 관리
    path('satisfy/', views.satisfy_list, name='satisfy_list'),
    path('satisfy/update-company/', views.satisfy_update_company, name='satisfy_update_company'),
    path('satisfy/<int:pk>/delete/', views.satisfy_delete, name='satisfy_delete'),

    # Satisfy Webhook
    path('webhook/satisfy/', webhook_views.satisfy_webhook, name='satisfy_webhook'),
    path('webhook/test-satisfy/', webhook_views.test_satisfy_webhook, name='test_satisfy_webhook'),

    # Complain Webhook (새로운 버전)
    path('webhook/complain/', webhook_views.complain_webhook, name='complain_webhook'),
    path('webhook/test-complain/', webhook_views.test_complain_webhook, name='test_complain_webhook'),
]