from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import VideoViewSet, init_upload, upload_file, complete_upload

router = DefaultRouter()
router.register(r'videos', VideoViewSet)

urlpatterns = [
    path('', include(router.urls)),
    
    # arLoupe Edge 設備自動上傳 API
    path('recordings/uploads/init', init_upload, name='init_upload'),
    path('upload/<str:recording_date>/<str:session_id>/<str:filename>', upload_file, name='upload_file'),
    path('recordings/uploads/complete', complete_upload, name='complete_upload'),
]