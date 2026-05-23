from django.contrib import admin
from django.urls import path, re_path, include
from django.conf import settings
from django.http import Http404
import os
import mimetypes

try:
    from ranged_response import RangedFileResponse
except ImportError:
    RangedFileResponse = None

def serve_media_with_range(request, path, document_root=None):
    filepath = os.path.normpath(os.path.join(document_root, path))
    if not os.path.exists(filepath):
        raise Http404("File not found")
        
    content_type, _ = mimetypes.guess_type(filepath)
    content_type = content_type or 'application/octet-stream'
    
    if RangedFileResponse:
        response = RangedFileResponse(request, open(filepath, 'rb'), content_type=content_type)
        return response
    else:
        # Fallback 預設處理
        from django.http import FileResponse
        return FileResponse(open(filepath, 'rb'), content_type=content_type)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('video_api.urls')),
    re_path(r'^media/(?P<path>.*)$', serve_media_with_range, {'document_root': settings.MEDIA_ROOT}),
]