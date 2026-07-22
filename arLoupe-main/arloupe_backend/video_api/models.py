from django.db import models    
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# 🎯 修正後：Video 包含 file_size 欄位
class Video(models.Model):
    title = models.CharField(max_length=100)
    file = models.FileField(upload_to='videos/')
    file_size = models.BigIntegerField(default=0) # 💡 搬到這裡！用來記錄每部影片的 Bytes 大小
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('ADMIN', 'Admin'),
        ('DOCTOR', 'Doctor'),
        ('PATIENT', 'Patient')
    ]

    # 與 Django 內建的 User 進行一對一關聯
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='DOCTOR')
    # 💡 這裡的 file_size 已經刪除了！

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"
    
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

class AuditLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='audit_logs')
    action = models.CharField(max_length=100)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    details = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        username = self.user.username if self.user else "未知用戶"
        return f"[{self.created_at}] {username} - {self.action}"