from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views, api_views

app_name = 'order'

# API Router 설정
router = DefaultRouter()
router.register(r'api/orders', api_views.OrderViewSet)
router.register(r'api/assigns', api_views.AssignViewSet)
router.register(r'api/group-purchases', api_views.GroupPurchaseViewSet)
router.register(r'api/message-templates', api_views.MessageTemplateViewSet)
router.register(r'api/companies', api_views.CompanyViewSet)
router.register(r'api/areas', api_views.AreaViewSet)

urlpatterns = [
    # 기존 뷰
    path('', views.order_list, name='order_list'),

    # React 앱을 위한 HTML 페이지
    path('pplist/', views.pplist_view, name='pplist'),

    # API 엔드포인트
    path('', include(router.urls)),
]