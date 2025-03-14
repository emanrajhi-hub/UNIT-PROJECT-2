from django.db import models

# Create your models here.

from policies.models import Policy
from users.models import CustomUser

class Approval(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    policy = models.ForeignKey(Policy, on_delete=models.CASCADE)
    reviewer = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    comment = models.TextField(blank=True, null=True)
    reviewed_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.policy.title} - {self.status}"
