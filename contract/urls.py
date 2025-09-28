from django.urls import path
from . import views
from . import webhook_views

app_name = 'contract'

urlpatterns = [
    path('', views.contract_list, name='contract_list'),
    path('clientreport/', views.clientreport_list, name='clientreport_list'),
    path('clientreport/<int:pk>/', views.clientreport_detail, name='clientreport_detail'),
    path('clientreport/<int:pk>/edit/', views.clientreport_edit, name='clientreport_edit'),
    path('clientreport/<int:pk>/delete/', views.clientreport_delete, name='clientreport_delete'),

    # Webhook URLs
    path('webhook/clientreport/', webhook_views.clientreport_webhook, name='clientreport_webhook'),
    path('webhook/test/', webhook_views.test_clientreport_webhook, name='test_clientreport_webhook'),
]