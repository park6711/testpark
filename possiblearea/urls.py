from django.urls import path
from . import views

app_name = 'possiblearea'

urlpatterns = [
    # 공사 가능 지역 관리 메인 페이지
    path('', views.PossiManageView.as_view(), name='possi_manage'),

    # 공사 가능 지역 데이터 API
    path('data/', views.PossiDataView.as_view(), name='possi_data'),
]