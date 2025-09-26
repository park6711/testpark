from django.urls import path
from . import views

app_name = 'evaluation'

urlpatterns = [
    path('', views.evaluation_list, name='evaluation_list'),

    # 업체평가 회차 관리
    path('evaluation-no/', views.evaluation_no_list, name='evaluation_no_list'),
    path('evaluation-no/<int:pk>/', views.evaluation_no_detail, name='evaluation_no_detail'),
    path('evaluation-no/<int:pk>/edit/', views.evaluation_no_edit, name='evaluation_no_edit'),
    path('evaluation-no/update-field/', views.evaluation_no_update_field, name='evaluation_no_update_field'),
]