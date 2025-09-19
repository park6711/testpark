"""
stop 앱 URL 설정
"""

from django.urls import path
from . import views
from .release_view import StopReleaseView
from .delete_view import StopDeleteView

app_name = 'stop'

urlpatterns = [
    # stop 관련 URL들을 여기에 추가
    path('', views.StopListView.as_view(), name='stop_list'),
    path('add/', views.StopCreateView.as_view(), name='stop_add'),
    path('edit/<int:stop_id>/', views.StopEditView.as_view(), name='stop_edit'),
    path('release/<int:stop_id>/', StopReleaseView.as_view(), name='stop_release'),
    path('delete/<int:stop_id>/', StopDeleteView.as_view(), name='stop_delete'),
    path('index/', views.StopIndexView.as_view(), name='index'),
]