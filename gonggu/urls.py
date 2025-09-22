from django.urls import path
from . import views

app_name = 'gonggu'

urlpatterns = [
    path('', views.gonggu_list, name='gonggu_list'),
    path('create/', views.gonggu_create, name='gonggu_create'),
    path('<int:pk>/', views.gonggu_detail, name='gonggu_detail'),
    path('<int:pk>/delete/', views.gonggu_delete, name='gonggu_delete'),
    path('<int:pk>/add-company/', views.add_gonggu_company, name='add_gonggu_company'),
    path('company/<int:gonggu_company_id>/remove/', views.remove_gonggu_company, name='remove_gonggu_company'),
    path('company/<int:gonggu_company_id>/area-manage/', views.area_manage, name='area_manage'),
]