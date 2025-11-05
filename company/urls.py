from django.urls import path
from . import views

app_name = 'company'

urlpatterns = [
    # Traditional views
    path('', views.company_list, name='company_list'),
    path('create/', views.company_create, name='company_create'),
    path('update/<int:pk>/', views.company_update, name='company_update'),
    path('delete/<int:pk>/', views.company_delete, name='company_delete'),
    path('view/<int:pk>/', views.company_view, name='company_view'),

    # React-based views
    path('react/', views.company_list_react, name='company_list_react'),

    # API endpoints
    path('api/companies/', views.api_company_list, name='api_company_list'),
    path('api/companies/<int:pk>/delete/', views.api_company_delete, name='api_company_delete'),
    path('api/companies/bulk-delete/', views.api_company_bulk_delete, name='api_company_bulk_delete'),
]