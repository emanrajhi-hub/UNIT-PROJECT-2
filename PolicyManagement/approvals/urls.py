from django.urls import path
from .views import approvals_list , approve_policy, reject_policy  , approved_rejected_policies  # تأكد من استيراد الفيو

urlpatterns = [
    path('', approvals_list, name='approvals_list'),  # المسار الرئيسي للموافقات

    path('approve/<int:policy_id>/', approve_policy, name='approve_policy'),
    path('reject/<int:policy_id>/', reject_policy, name='reject_policy'),

    path('approved-rejected/', approved_rejected_policies, name='approved_rejected_policies'),  # ✅ إضافة هذا السطر

]
