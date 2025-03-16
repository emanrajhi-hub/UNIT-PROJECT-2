from django.shortcuts import render, redirect, get_object_or_404
from policies.models import Policy
from django.contrib.auth.decorators import login_required, permission_required
from notifications.models import Notification
from django.contrib import messages
from django.http import HttpResponseForbidden  # ✅ لمنع الوصول غير المصرح به

@login_required
def approvals_list(request):
    """ 🔹 المشرف يرى جميع السياسات المعلقة، بينما يرى المستخدم العادي السياسات التي أضافها فقط """
    if request.user.is_superuser:
        policies = Policy.objects.filter(status='Pending').order_by('-created_at')
    else:
        policies = Policy.objects.filter(author=request.user).order_by('-created_at')

    return render(request, 'approvals/approvals_list.html', {'policies': policies})

@login_required
@permission_required('policies.change_policy', raise_exception=True)
def approve_policy(request, policy_id):
    """ ✅ الموافقة على السياسة """
    policy = get_object_or_404(Policy, id=policy_id)
    
    # 🔹 السماح فقط للمشرف بالقبول
    if not request.user.is_superuser:
        return HttpResponseForbidden("❌ You do not have permission to approve policies.")

    policy.status = 'Approved'
    policy.save()

    if policy.author:
        Notification.objects.create(
            recipient=policy.author,
            message=f"✅ Your policy '{policy.title}' has been approved."
        )

    messages.success(request, f"✅ The policy '{policy.title}' has been approved.")
    return redirect('approvals_list')

@login_required
@permission_required('policies.change_policy', raise_exception=True)
def reject_policy(request, policy_id):
    """ ❌ رفض السياسة """
    policy = get_object_or_404(Policy, id=policy_id)
    
    # 🔹 السماح فقط للمشرف بالرفض
    if not request.user.is_superuser:
        return HttpResponseForbidden("❌ You do not have permission to reject policies.")

    policy.status = 'Rejected'
    policy.save()

    if policy.author:
        Notification.objects.create(
            recipient=policy.author,
            message=f"❌ Your policy '{policy.title}' has been rejected."
        )

    messages.warning(request, f"❌ The policy '{policy.title}' has been rejected.")
    return redirect('approvals_list')

@login_required
@permission_required('policies.delete_policy', raise_exception=True)
def delete_policy(request, policy_id):
    """ 🗑️ حذف السياسات المرفوضة فقط """
    policy = get_object_or_404(Policy, id=policy_id)

    if not request.user.is_superuser:
        return HttpResponseForbidden("❌ You do not have permission to delete policies.")

    if policy.status != 'Rejected':
        messages.error(request, "❌ You can only delete rejected policies.")
        return redirect('approvals_list')

    policy_title = policy.title
    policy.delete()

    if policy.author:
        Notification.objects.create(
            recipient=policy.author,
            message=f"⚠️ Your rejected policy '{policy_title}' has been deleted by an admin."
        )

    messages.success(request, f"🗑️ The rejected policy '{policy_title}' has been deleted.")
    return redirect('approvals_list')

@login_required
def approved_rejected_policies(request):
    """ 🔹 عرض السياسات الموافق عليها والمرفوضة لكل المستخدمين """
    approved_policies = Policy.objects.filter(status='Approved').order_by('-created_at')
    rejected_policies = Policy.objects.filter(status='Rejected').order_by('-created_at')

    return render(request, 'approvals/approved_rejected_policies.html', {
        'approved_policies': approved_policies,
        'rejected_policies': rejected_policies
    })
