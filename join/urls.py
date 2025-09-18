from django.urls import path
from . import views

app_name = 'join'

urlpatterns = [
    path('company-registration/', views.company_registration, name='company_registration'),
    path('btoc-registration/', views.btoc_registration, name='btoc_registration'),
    path('btob-registration/', views.btob_registration, name='btob_registration'),
    path('success/', views.registration_success, name='registration_success'),
]