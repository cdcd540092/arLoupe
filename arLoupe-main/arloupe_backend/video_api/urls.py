from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    VideoViewSet, register_user, CustomLoginView, 
    UserManagementViewSet, AuditLogViewSet, DashboardStatsView # 💡 引入新 View
)
from rest_framework_simplejwt.views import TokenRefreshView, TokenBlacklistView

# 建立 DRF 的 Router 來處理影片
router = DefaultRouter()
router.register(r'videos', VideoViewSet)
router.register(r'users', UserManagementViewSet, basename='user-management')
router.register(r'audit-logs', AuditLogViewSet, basename='audit-logs')

urlpatterns = [
    # 1. 影片的 API 路由 (會變成 /api/videos/)
    path('', include(router.urls)),
    
    # 2. 💡 完全符合你指定的 JWT 登入規範網址！
    # 因為總路由有一層 'api/'，這裡加上 'auth/login/'，拼起來就是 /api/auth/login/
    path('auth/login/', CustomLoginView.as_view(), name='auth_login'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('auth/logout/', TokenBlacklistView.as_view(), name='token_blacklist'),
    
    # 3. 註冊 API 路由 (拼起來就是 /api/register/)
    path('register/', register_user, name='api_register'),
    path('dashboard/stats/', DashboardStatsView.as_view(), name='dashboard_stats'),
]