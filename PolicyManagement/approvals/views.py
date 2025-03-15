from django.shortcuts import render, redirect, get_object_or_404
from policies.models import Policy
from django.contrib.auth.decorators import login_required, permission_required
from notifications.models import Notification

@login_required
def approvals_list(request):
    policies = Policy.objects.filter(status='Pending').order_by('-created_at')
    return render(request, 'approvals/approvals_list.html', {'policies': policies})

@login_required
@permission_required('policies.change_policy', raise_exception=True)
def approve_policy(request, policy_id):
    policy = get_object_or_404(Policy, id=policy_id)
    policy.status = 'Approved'
    policy.save()

    # 🔹 تأكد أن policy.author ليس None قبل إنشاء الإشعار
    if policy.author:
        notification = Notification.objects.create(
            recipient=policy.author,
            message=f"Your policy '{policy.title}' has been approved."
        )
        print(f"✅ Notification created: {notification}")

    return redirect('approvals_list')

@login_required
@permission_required('policies.change_policy', raise_exception=True)
def reject_policy(request, policy_id):
    policy = get_object_or_404(Policy, id=policy_id)
    policy.status = 'Rejected'
    policy.save()

    # 🔹 تأكد أن policy.author ليس None قبل إنشاء الإشعار
    if policy.author:
        notification = Notification.objects.create(
            recipient=policy.author,
            message=f"Your policy '{policy.title}' has been rejected."
        )
        print(f"❌ Notification created: {notification}")

    return redirect('approvals_list')

@login_required
def approved_rejected_policies(request):
    # 🔹 تقسيم السياسات إلى قسمين متطابقين مع القالب
    approved_policies = Policy.objects.filter(status='Approved').order_by('-created_at')
    rejected_policies = Policy.objects.filter(status='Rejected').order_by('-created_at')

    return render(request, 'approvals/approved_rejected_policies.html', {
        'approved_policies': approved_policies,
        'rejected_policies': rejected_policies
    })
