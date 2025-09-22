from django.urls import path
from . import views

app_name = 'point'

urlpatterns = [
    path('', views.point_list, name='point_list'),
]