import os
from rest_framework import viewsets
from rest_framework.decorators import api_view, parser_classes
from rest_framework.response import Response
from rest_framework.parsers import BaseParser
from django.conf import settings
from .models import Video
from .serializers import VideoSerializer

class VideoViewSet(viewsets.ModelViewSet):
    queryset = Video.objects.all().order_by('-created_at')
    serializer_class = VideoSerializer

# =========================================================
# arLoupe Edge 設備自動上傳 API 整合 (相容 mock_upload_server)
# =========================================================

@api_view(['POST'])
def init_upload(request):
    """
    模擬 S3 Presigned URL 機制，告訴樹莓派要往哪裡 PUT 檔案。
    """
    data = request.data
    session_id = data.get('session_id', 'default_session')
    recording_date = data.get('recording_date', '1970-01-01')
    segment_index = data.get('segment_index', 0)
    
    mp4_name = os.path.basename(data.get('mp4_filename', 'video.mp4'))
    json_name = os.path.basename(data.get('json_filename', 'meta.json'))
    recording_id = f"{session_id}_seg{int(segment_index):05d}"

    # 回傳的 URL 加入 /api 前綴，以符合 Django 的路由配置
    return Response({
        "recording_id": recording_id,
        "mp4_upload_url": f"/api/upload/{recording_date}/{session_id}/{mp4_name}",
        "json_upload_url": f"/api/upload/{recording_date}/{session_id}/{json_name}",
        "expires_in": 900
    })


class BinaryParser(BaseParser):
    """ 解析原生的二進位串流 (用於 PUT 上傳) """
    media_type = '*/*'
    def parse(self, stream, media_type=None, parser_context=None):
        return stream.read()


@api_view(['PUT'])
@parser_classes([BinaryParser])
def upload_file(request, recording_date, session_id, filename):
    """
    接收樹莓派的二進位檔案，直接存入 Django 的 media/videos 資料夾。
    若是 MP4 檔，則自動註冊進 Video 資料庫！
    """
    safe_filename = os.path.basename(filename)
    save_dir = os.path.join(settings.MEDIA_ROOT, 'videos')
    os.makedirs(save_dir, exist_ok=True)
    
    save_path = os.path.join(save_dir, safe_filename)
    
    with open(save_path, "wb") as f:
        f.write(request.data)
        
    # 自動化：如果是影片檔，立刻建立資料庫紀錄，前端臨床檢視器就會馬上顯示！
    if safe_filename.endswith('.mp4'):
        # 產生專業的患者標題，或使用預設
        title = f"arLoupe_{session_id}_{safe_filename.split('.')[0]}"
        file_relative_path = f"videos/{safe_filename}"
        Video.objects.create(title=title, file=file_relative_path)
        
    return Response({
        "status": "ok",
        "filename": safe_filename,
        "saved_to": save_path,
        "size_bytes": os.path.getsize(save_path)
    })


@api_view(['POST'])
def complete_upload(request):
    """ 接收上傳完成的通知 """
    return Response({
        "status": "completed",
        "received": request.data
    })