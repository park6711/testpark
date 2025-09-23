from django.urls import path
from . import views

app_name = 'point'

urlpatterns = [
    # 리스트 뷰
    path('', views.point_list, name='point_list'),

    # CRUD 기능
    path('<int:pk>/', views.point_detail, name='point_detail'),
    path('create/', views.point_create, name='point_create'),
    path('<int:pk>/update/', views.point_update, name='point_update'),
    path('<int:pk>/delete/', views.point_delete, name='point_delete'),

    # 업체별 최종 포인트
    path('company-points/', views.company_points, name='company_points'),
]