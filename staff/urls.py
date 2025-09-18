from django.urls import path
from . import views

app_name = 'staff'

urlpatterns = [
    path('', views.staff_list, name='staff_list'),
    path('create/', views.staff_create, name='staff_create'),
    path('update/<int:pk>/', views.staff_update, name='staff_update'),
    path('delete/<int:pk>/', views.staff_delete, name='staff_delete'),
    path('view/<int:pk>/', views.staff_view, name='staff_view'),
]