from .models import AuditLog

def get_client_ip(request):
    """ 💡 偵測前端請求的真實 IP """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def log_action(user, action, request, details=""):
    """ 💡 快速寫入稽核日誌的輔助函式 """
    try:
        ip = get_client_ip(request) if request else None
        AuditLog.objects.create(
            user=user,
            action=action,
            ip_address=ip,
            details=details
        )
    except Exception as e:
        print(f"寫入稽核日誌失敗: {str(e)}") # 避免日誌寫入失敗導致主業務中斷