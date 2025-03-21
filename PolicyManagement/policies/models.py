from django.db import models
from django.conf import settings
from users.models import CustomUser
import os

class Policy(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]

    CATEGORY_CHOICES = [
        ('HR', 'Human Resources'),
        ('IT', 'Information Technology'),
        ('Finance', 'Finance'),
        ('Engineernig', 'Engineering'),
        ('Private', 'Private Sectors'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    file = models.FileField(upload_to='policies/files/', blank=True, null=True)
    image = models.ImageField(upload_to='policies/images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')

    def __str__(self):
        return self.title

    # ✅ حذف الملف القديم قبل رفع جديد
    def save(self, *args, **kwargs):
        try:
            # لو فيه تعديل للملف
            if self.pk:
                old_policy = Policy.objects.get(pk=self.pk)
                if old_policy.file and old_policy.file != self.file:
                    if os.path.isfile(old_policy.file.path):
                        os.remove(old_policy.file.path)
                if old_policy.image and old_policy.image != self.image:
                    if os.path.isfile(old_policy.image.path):
                        os.remove(old_policy.image.path)
        except Policy.DoesNotExist:
            pass  # حالة الإضافة الجديدة

        super().save(*args, **kwargs)


class Bookmark(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookmarks')
    policy = models.ForeignKey('Policy', on_delete=models.CASCADE, related_name='bookmarked_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'policy')

    def __str__(self):
        return f"{self.user.username} bookmarked {self.policy.title}"


class Comment(models.Model):
    policy = models.ForeignKey(Policy, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.policy.title}"


class Rating(models.Model):
    policy = models.ForeignKey(Policy, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    stars = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'policy')

    def __str__(self):
        return f"{self.stars} stars by {self.user.username} for {self.policy.title}"
