from rest_framework import serializers
from .models import Video
from django.contrib.auth.models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import UserProfile
from .models import AuditLog

class AuditLogSerializer(serializers.ModelSerializer):
    # 💡 顯示易讀的用戶姓名或帳號，而不是只顯示 user_id
    operator_name = serializers.CharField(source='user.first_name', read_only=True)
    operator_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = AuditLog
        fields = ['id', 'operator_username', 'operator_name', 'action', 'ip_address', 'details', 'created_at']

# 影片的序列化器 (原本的)
class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = '__all__'

# 💡 新增：客製化 JWT 登入回傳格式的序列化器
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user
        user_role = user.profile.role if hasattr(user, 'profile') else 'DOCTOR'

        # 打包成你指定的 user 格式
        data['user'] = {
            'id': user.id,
            'name': user.first_name,  
            'email': user.email,
            'role': user_role
        }
        return data

class UserManagementSerializer(serializers.ModelSerializer):
    # 💡 透過 source 撈出關聯的 UserProfile 欄位
    role = serializers.CharField(source='profile.role', required=False)
    name = serializers.CharField(source='first_name', required=False, allow_blank=True)
    
    class Meta:
        model = User
        # 7. 查詢所有人員要求的欄位
        fields = ['id', 'username', 'password', 'name', 'email', 'role', 'last_login', 'is_active']
        extra_kwargs = {
            'password': {'write_only': True, 'required': False}, # 密碼唯寫，查詢時不回傳
            'last_login': {'read_only': True}                    # 最後登入時間由系統產生
        }

    # 8. 新增人員（處理密碼加密與角色綁定）
    def create(self, validated_data):
        # 拆解出 profile 的資料與姓名
        profile_data = validated_data.pop('profile', {})
        role = profile_data.get('role', 'DOCTOR')
        first_name = validated_data.pop('first_name', '')

        # 建立 User 實例（此處 create_user 會自動幫密碼進行雜湊加密）
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            email=validated_data.get('email', ''),
            first_name=first_name
        )

        # 調整自動生成的 profile 角色
        profile = user.profile
        profile.role = role
        profile.save()

        return user

    # 9. 修改人員資料
    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', {})
        role = profile_data.get('role')
        first_name = validated_data.pop('first_name', None)

        # 更新 User 基本欄位
        instance.email = validated_data.get('email', instance.email)
        if first_name is not None:
            instance.first_name = first_name
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.save()

        # 更新角色
        if role:
            profile = instance.profile
            profile.role = role
            profile.save()

        return instance