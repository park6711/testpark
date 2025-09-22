from django.urls import path
from . import views

app_name = 'companycondition'

urlpatterns = [
    path('', views.company_condition_list, name='company_condition_list'),
    path('search/', views.search_companies, name='search_companies'),
    path('detail/<int:company_id>/', views.get_company_detail, name='get_company_detail'),
    path('update/<int:company_id>/', views.update_apply_grade, name='update_apply_grade'),
]