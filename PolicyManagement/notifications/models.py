from django.db import models
from users.models import CustomUser  # ✅ التأكد من استيراد المستخدم المخصص
from policies.models import Policy  # ✅ استيراد نموذج السياسات

# class Notification(models.Model):
#     recipient = models.ForeignKey(CustomUser, on_delete=models.CASCADE)  # لمن سيتم إرسال الإشعار؟
#     policy = models.ForeignKey(Policy, on_delete=models.CASCADE, null=True, blank=True)  # السياسة المرتبطة بالإشعار
#     message = models.TextField()  # محتوى الإشعار
#     is_read = models.BooleanField(default=False)  # هل تمت قراءة الإشعار؟
#     created_at = models.DateTimeField(auto_now_add=True)  # وقت إنشاء الإشعار

#     def __str__(self):
#         return f"Notification for {self.recipient.username} - {'Read' if self.is_read else 'Unread'}"

class Notification(models.Model):
    recipient = models.ForeignKey(CustomUser, on_delete=models.CASCADE)  # لمن سيتم إرسال الإشعار؟
    policy = models.ForeignKey(Policy, on_delete=models.CASCADE, null=True, blank=True)  # السياسة المرتبطة بالإشعار
    message = models.TextField()  # محتوى الإشعار
    is_read = models.BooleanField(default=False)  # هل تمت قراءة الإشعار؟
    created_at = models.DateTimeField(auto_now_add=True)  # وقت إنشاء الإشعار

    # ✅ الرابط الاختياري للإشعار (مثلاً لصفحة الرسائل)
    link = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"Notification for {self.recipient.username} - {'Read' if self.is_read else 'Unread'}"