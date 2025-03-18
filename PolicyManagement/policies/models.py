from django.db import models

# Create your models here.

from users.models import CustomUser

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
        ('Engineernig' , 'Engineering'),
        ('Private', 'Private Sectors'),  # ✅ إضافة فئة القطاعات الخاصة
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    file = models.FileField(upload_to='policies/')

    image = models.ImageField(upload_to='policies/images/', blank=True, null=True)  # ✅ هذا هو الحقل الجديد


    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')  # ✅ إضافة حالة الموافقة

    def __str__(self):
        return self.title
