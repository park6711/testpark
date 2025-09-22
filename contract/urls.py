from django.urls import path
from . import views

app_name = 'contract'

urlpatterns = [
    path('', views.contract_list, name='contract_list'),
]