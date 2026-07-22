from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Video, UserProfile

admin.site.register(Video)

# 定義內嵌的角色介面
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = '權限角色設定 (Profile)'

# 重新定義使用者管理介面
class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    
    # 後台列表直接顯示你要的欄位變動
    list_display = ('username', 'email', 'first_name', 'get_role', 'is_active', 'last_login')

    def get_role(self, obj):
        if hasattr(obj, 'profile'):
            return obj.profile.role
        return "無角色"
    get_role.short_description = '身分角色'

admin.site.unregister(User)
admin.site.register(User, UserAdmin)