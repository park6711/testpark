from django.urls import path
from . import views
from . import webhook_views

app_name = 'contract'

urlpatterns = [
    path('', views.contract_list, name='contract_list'),
    path('companyreport/', views.companyreport_list, name='companyreport_list'),
    path('clientreport/', views.clientreport_list, name='clientreport_list'),
    path('clientreport/<int:pk>/', views.clientreport_detail, name='clientreport_detail'),
    path('clientreport/<int:pk>/edit/', views.clientreport_edit, name='clientreport_edit'),
    path('clientreport/<int:pk>/delete/', views.clientreport_delete, name='clientreport_delete'),

    # CompanyReport 상세/수정/액션 URLs
    path('companyreport/<int:pk>/detail/', views.companyreport_detail, name='companyreport_detail'),
    path('companyreport/<int:pk>/edit/', views.companyreport_edit, name='companyreport_edit'),
    path('companyreport/<int:pk>/delete/', views.companyreport_delete, name='companyreport_delete'),
    path('companyreport/<int:pk>/increase/', views.companyreport_increase, name='companyreport_increase'),
    path('companyreport/<int:pk>/decrease/', views.companyreport_decrease, name='companyreport_decrease'),
    path('companyreport/<int:pk>/cancel/', views.companyreport_cancel, name='companyreport_cancel'),
    path('companyreport/create/', views.companyreport_create, name='companyreport_create'),

    # API URLs
    path('assign-company/', views.assign_company, name='assign_company'),
    path('update-report-type/', views.update_report_type, name='update_report_type'),
    path('update-company-name/', views.update_company_name, name='update_company_name'),
    path('api/companyreport/<int:pk>/action/', views.companyreport_action_api, name='companyreport_action_api'),
    path('api/calculate-fee/', views.calculate_fee_api, name='calculate_fee_api'),
    path('api/point-process/', views.process_point_api, name='process_point_api'),
    path('api/order-search/', views.search_order_api, name='search_order_api'),
    path('api/assign-search/', views.search_assign_api, name='search_assign_api'),
    path('api/company-search/', views.search_company_api, name='search_company_api'),
    path('api/report-file/<int:file_id>/delete/', views.delete_report_file, name='delete_report_file'),
    path('api/create-refund-point/', views.create_refund_point, name='create_refund_point'),
    path('api/companyreport/<int:pk>/data/', views.get_companyreport_data, name='get_companyreport_data'),

    # Webhook URLs
    path('webhook/clientreport/', webhook_views.clientreport_webhook, name='clientreport_webhook'),
    path('webhook/test/', webhook_views.test_clientreport_webhook, name='test_clientreport_webhook'),
    path('webhook/companyreport/', webhook_views.companyreport_webhook, name='companyreport_webhook'),
    path('webhook/companyreport/test/', webhook_views.test_companyreport_webhook, name='test_companyreport_webhook'),
]