from django.shortcuts import render, redirect, get_object_or_404
from policies.models import Policy
from django.contrib.auth.decorators import login_required, permission_required
from notifications.models import Notification
from django.contrib import messages
from django.http import HttpResponseForbidden

# @login_required
# def approvals_list(request):
#     """ 🔹 المشرف يرى جميع السياسات المعلقة، بينما المستخدم العادي يرى فقط لو كان قد أضاف سياسات """
#     if request.user.is_superuser:
#         policies = Policy.objects.filter(status='Pending').order_by('-created_at')
#     else:
#         user_policies = Policy.objects.filter(author=request.user)
#         if not user_policies.exists():
#             messages.warning(request, "⚠️ You don't have any policies yet to track approvals.")
#             return redirect('policy_list')  # يعيده إلى صفحة السياسات أو أي صفحة تناسبك
#         policies = user_policies.order_by('-created_at')

#     return render(request, 'approvals/approvals_list.html', {'policies': policies})

@login_required
def approvals_list(request):
    """ 🔹 المشرف يرى جميع السياسات المعلقة، بينما المستخدم العادي يرى فقط سياساته المعلقة (Pending فقط) """
    if request.user.is_superuser:
        policies = Policy.objects.filter(status='Pending').order_by('-created_at')
    else:
        user_pending_policies = Policy.objects.filter(author=request.user, status='Pending')
        if not user_pending_policies.exists():
            messages.warning(request, "⚠️ You don't have any pending policies to track.")
            return redirect('policy_list')  # يعيده إلى صفحة السياسات أو أي صفحة تناسبك
        policies = user_pending_policies.order_by('-created_at')

    return render(request, 'approvals/approvals_list.html', {'policies': policies})



@login_required
@permission_required('policies.change_policy', raise_exception=True)
def approve_policy(request, policy_id):
    if not request.user.is_superuser:
        return HttpResponseForbidden("❌ You do not have permission to approve policies.")
    policy = get_object_or_404(Policy, id=policy_id)
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
    if not request.user.is_superuser:
        return HttpResponseForbidden("❌ You do not have permission to reject policies.")
    policy = get_object_or_404(Policy, id=policy_id)
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
    if not request.user.is_superuser:
        return HttpResponseForbidden("❌ You do not have permission to delete policies.")
    policy = get_object_or_404(Policy, id=policy_id)
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
    approved_policies = Policy.objects.filter(status='Approved').order_by('-created_at')
    rejected_policies = Policy.objects.filter(status='Rejected').order_by('-created_at')
    return render(request, 'approvals/approved_rejected_policies.html', {
        'approved_policies': approved_policies,
        'rejected_policies': rejected_policies
    })
