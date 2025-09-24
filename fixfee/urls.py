from django.urls import path
from . import views

app_name = 'fixfee'

urlpatterns = [
    path('', views.fixfee_list, name='fixfee_list'),
    path('status/', views.fixfee_status, name='fixfee_status'),
    path('add/', views.fixfee_add, name='fixfee_add'),
    path('<int:pk>/', views.fixfee_detail, name='fixfee_detail'),
    path('delete/<int:pk>/', views.fixfee_delete, name='fixfee_delete'),
    path('api/company-info/', views.get_company_info, name='get_company_info'),
    path('api/check-duplicate/', views.check_duplicate, name='check_duplicate'),
]