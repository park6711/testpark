from django.urls import path
from . import views

app_name = 'template'

urlpatterns = [
    path('', views.TemplateListView.as_view(), name='template_list'),
    path('create/', views.TemplateCreateView.as_view(), name='template_create'),
    path('<int:pk>/', views.TemplateDetailView.as_view(), name='template_detail'),
    path('<int:pk>/update/', views.TemplateUpdateView.as_view(), name='template_update'),
    path('<int:pk>/delete/', views.template_delete, name='template_delete'),
]