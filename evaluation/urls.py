from django.urls import path
from . import views
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
    path('webhook/google-sheets/', webhook_views.google_sheets_webhook, name='google_sheets_webhook'),
]