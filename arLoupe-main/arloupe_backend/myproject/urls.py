from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    # 💡 讓所有開頭為 api/ 的請求，全部進入子路由做進一步分流
    path('api/', include('video_api.urls')), 
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)