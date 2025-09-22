from django.urls import path
from . import views

app_name = 'license'

urlpatterns = [
    path('', views.license_list, name='license_list'),
    path('create/', views.license_create, name='license_create'),
    path('update/<int:pk>/', views.license_update, name='license_update'),
    path('delete/<int:pk>/', views.license_delete, name='license_delete'),
    path('view/<int:pk>/', views.license_view, name='license_view'),
]