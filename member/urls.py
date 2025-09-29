from django.urls import path
from . import views

app_name = 'member'

urlpatterns = [
    path('', views.member_list, name='member_list'),
    path('dashboard/', views.member_dashboard, name='member_dashboard'),  # 업체 대시보드
    path('create/', views.member_create, name='member_create'),
    path('update/<int:pk>/', views.member_update, name='member_update'),
    path('delete/<int:pk>/', views.member_delete, name='member_delete'),
    path('view/<int:pk>/', views.member_view, name='member_view'),
]