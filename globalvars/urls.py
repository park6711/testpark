from django.urls import path
from . import views

app_name = 'globalvars'

urlpatterns = [
    path('', views.globalvar_list, name='globalvar_list'),
    path('update/', views.globalvar_update, name='globalvar_update'),
]