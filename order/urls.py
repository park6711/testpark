from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views, api_views, dashboard_views

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

    # 구글 시트 동기화 API
    path('api/sync-google-sheets/', api_views.sync_google_sheets, name='sync_google_sheets'),

    # 동기화 대시보드 API
    path('api/dashboard/', include([
        path('', dashboard_views.sync_dashboard, name='sync_dashboard'),
        path('history/', dashboard_views.sync_history, name='sync_history'),
        path('manual-sync/', dashboard_views.manual_sync, name='manual_sync'),
        path('pending-orders/', dashboard_views.pending_orders, name='pending_orders'),
    ])),
]