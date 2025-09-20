"""
impossibleterm 앱 URL 설정
"""

from django.urls import path
from . import views
from .release_view import ImpoReleaseView
from .delete_view import ImpoDeleteView

app_name = 'impossibleterm'

urlpatterns = [
    # impo 관련 URL들
    path('', views.ImpoListView.as_view(), name='impo_list'),
    path('add/', views.ImpoCreateView.as_view(), name='impo_add'),
    path('edit/<int:impo_id>/', views.ImpoEditView.as_view(), name='impo_edit'),
    path('release/<int:impo_id>/', ImpoReleaseView.as_view(), name='impo_release'),
    path('delete/<int:impo_id>/', ImpoDeleteView.as_view(), name='impo_delete'),
    path('index/', views.ImpoIndexView.as_view(), name='index'),
]