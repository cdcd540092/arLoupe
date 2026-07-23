from rest_framework import viewsets
from .models import Video, UserProfile
from .serializers import VideoSerializer
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login  # 💡 用來自動更新最後登入時間
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated  # 💡 引入權限檢查工具
from .serializers import UserManagementSerializer
from .utils import log_action
from .models import AuditLog
from .serializers import AuditLogSerializer
from rest_framework.permissions import BasePermission
from rest_framework.views import APIView
from django.db.models import Sum

# 💡 引入 JWT 必要的套件
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer

# ==========================================
# 1. 影片管理 API (原本的，保持不變)
# ==========================================
class VideoViewSet(viewsets.ModelViewSet):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    # 這裡應該有你原本設定的 permission_classes，請保留它
    # permission_classes = [IsAuthenticated] 

    # 💡 1. 攔截「上傳影片」動作 (POST /api/videos/)
    def perform_create(self, serializer):
        # 獲取上傳的檔案
        file_obj = self.request.FILES.get('file')
        file_size = file_obj.size if file_obj else 0
        
        # 儲存影片，並自動把檔案大小 (Bytes) 寫入資料庫
        video = serializer.save(file_size=file_size)
        
        # 🎯 寫入稽核日誌
        log_action(
            user=self.request.user,
            action="UPLOAD_VIDEO",
            request=self.request,
            details=f"上傳了新影片: {video.title} (大小: {round(file_size / (1024 * 1024), 2)} MB)"
        )

    # 💡 2. 攔截「觀看單一影片」動作 (GET /api/videos/<id>/)
    def retrieve(self, request, *args, **kwargs):
        # 先執行原本的獲取影片邏輯
        response = super().retrieve(request, *args, **kwargs)
        video_instance = self.get_object()
        
        # 🎯 寫入稽核日誌：誰點開了這部影片
        log_action(
            user=request.user,
            action="VIEW_VIDEO",
            request=request,
            details=f"觀看了影片: {video_instance.title} (影片 ID: {video_instance.id})"
        )
        
        return response


# ==========================================
# 2. 客製化 JWT 登入 View (這就是你報錯找不到的元件！)
# ==========================================
class CustomLoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        
        try:
            # 自動驗證：1.帳號存在 2.密碼正確 3.帳號未停用(is_active=True)
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            # 驗證失敗統一回傳錯誤訊息
            return Response({'error': '帳號或密碼錯誤，或該帳號已被停用'}, status=status.HTTP_400_BAD_REQUEST)

        # 驗證成功後，獲取使用者物件並「更新最後登入時間」
        user = serializer.user
        update_last_login(None, user)

        # 💡 新增：登入成功，記錄到稽核日誌 (AuditLog)
        log_action(
            user=user,
            action="LOGIN",
            request=request,
            details=f"使用者 {user.username} (角色: {user.profile.role}) 登入系統"
        )

        # 回傳你指定的完整 JSON 格式 (包含 access, refresh, user 物件)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)

# ==========================================
# 3. 使用者註冊 API (配合你原本的 Signal 架構)
# ==========================================
@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    """ 帳號註冊 API """
    username = request.data.get('username')
    password = request.data.get('password')
    first_name = request.data.get('first_name', '')  # 接收姓名
    email = request.data.get('email', '')            # 接收 Email
    role = request.data.get('role', 'STAFF')         # 預設為大寫 STAFF

    if not username or not password:
        return Response({'error': '請提供帳號與密碼'}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(username=username).exists():
        return Response({'error': '此帳號已被註冊'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # 1. 建立 Django 使用者
        user = User.objects.create_user(
            username=username, 
            password=password,
            first_name=first_name,
            email=email
        )
        
        # 2. 綁定角色 (因為 Signal 已經建好 profile，抓出來修改並儲存)
        profile = user.profile
        profile.role = role
        profile.save()
        
        return Response({
            'username': user.username,
            'name': user.first_name,
            'email': user.email,
            'role': role
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class UserManagementViewSet(viewsets.ModelViewSet):
    # 💡 排序讓最新的使用者排在前面，且列出所有帳號（含被停用的）
    queryset = User.objects.all().order_by('-id')
    serializer_class = UserManagementSerializer
    permission_classes = [IsAuthenticated] # 必須登入才能管理人員

    # 💡 8. 攔截「建立人員」動作，並自動寫入稽核日誌
    def perform_create(self, serializer):
        user = serializer.save()
        log_action(
            user=self.request.user,  # 操作者：當前登入的 ADMIN
            action="CREATE_USER",
            request=self.request,
            details=f"建立了新帳號: {user.username} (姓名: {user.first_name}, 角色: {user.profile.role})"
        )

    # 💡 9. 攔截「修改人員」動作，並自動寫入稽核日誌
    def perform_update(self, serializer):
        user = serializer.save()
        log_action(
            user=self.request.user,  # 操作者：當前登入的 ADMIN
            action="UPDATE_USER",
            request=self.request,
            details=f"修改了帳號: {user.username} 的資料 (角色: {user.profile.role}, 狀態: {'啟用' if user.is_active else '停用'})"
        )

    # 💡 10. 覆寫刪除動作，改為 Soft Delete (軟刪除)，並寫入稽核日誌
    def destroy(self, request, *args, **kwargs):
        user_instance = self.get_object()
        
        # 避免最高管理員不小心把自己停用
        if user_instance == request.user:
            return Response({'error': '你不能停用你自己！'}, status=status.HTTP_400_BAD_REQUEST)
            
        user_instance.is_active = False # 🎯 修改狀態為不啟用，不刪除資料
        user_instance.save()
        
        # 💡 新增：成功停用後，記錄到稽核日誌
        log_action(
            user=request.user,  # 操作者：當前登入的 ADMIN
            action="DISABLE_USER",
            request=request,
            details=f"停用（軟刪除）了帳號: {user_instance.username}"
        )
        
        return Response({'message': '人員帳號已成功停用(軟刪除)'}, status=status.HTTP_200_OK)
    
# 💡 自訂一個「限 ADMIN 進入」的權限門檻
class IsAdminUserOnly(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.profile.role == 'ADMIN'

class AuditLogViewSet(viewsets.ReadOnlyModelViewSet): # 唯讀，不允許前端手動新增/修改日誌
    queryset = AuditLog.objects.all()  # 預設已經在 Model 用 -created_at 排序好了
    serializer_class = AuditLogSerializer
    permission_classes = [IsAdminUserOnly] # 🎯 嚴格限管 ADMIN 存取

class DashboardStatsView(APIView):
    permission_classes = [IsAdminUserOnly] # 🎯 一樣只限 ADMIN 讀取

    def get(self, request):
        # 1. 統計總影片數
        total_videos = Video.objects.count()
        
        # 2. 統計總帳號數
        total_users = User.objects.count()
        
        # 3. 計算總儲存空間 (假設你的 Video model 裡有 file_size 欄位，單位是 bytes)
        # 註：如果你的 Video model 沒有 file_size 欄位，可以直接先寫死一個模擬數字，或加總容量
        total_bytes = Video.objects.aggregate(Sum('file_size'))['file_size__sum'] or 0
        
        # 💡 將 Bytes 換算成 GB：Bytes / 1024^3
        storage_used_gb = round(total_bytes / (1024 * 1024 * 1024), 2)
        
        # 4. 抓取最新 5 筆稽核日誌
        recent_logs = AuditLog.objects.all()[:5]
        recent_activity = []
        for log in recent_logs:
            # 格式化時間成前端好讀的 "10:30 AM" 或是 "2026-07-01 10:30"
            formatted_time = log.created_at.strftime("%I:%M %p")
            operator = log.user.first_name if (log.user and log.user.first_name) else (log.user.username if log.user else "系統")
            
            recent_activity.append({
                "time": formatted_time,
                "user": operator,
                "action": log.details
            })

        # 回傳統整後的 JSON
        return Response({
            "total_videos": total_videos,
            "total_users": total_users,
            "storage_used_gb": storage_used_gb,
            "recent_activity": recent_activity
        }, status=status.HTTP_200_OK)