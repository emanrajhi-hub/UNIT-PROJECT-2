from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponseForbidden
from .models import Policy
from .forms import PolicyForm  # تأكد من أنك أضفت نموذج تعديل السياسة
from django.contrib import messages
from notifications.models import Notification


def home(request):
    policies = Policy.objects.all().order_by('-created_at')[:6]  # عرض أحدث 6 سياسات فقط كمثال
    return render(request, 'home.html', {'policies': policies})




def policy_list(request):
    query = request.GET.get('q', '')  # البحث بالكلمة المفتاحية
    category_filter = request.GET.get('category', '')  # الحصول على الفئة المختارة

    policies = Policy.objects.all()

    if query:
        policies = policies.filter(title__icontains=query)  # البحث في العنوان

    if category_filter:
        policies = policies.filter(category=category_filter)  # تصفية حسب الفئة

    return render(request, 'policies/policy_list.html', {'policies': policies, 'query': query, 'category_filter': category_filter})


def policy_detail(request, policy_id):
    policy = get_object_or_404(Policy, id=policy_id)  # جلب السياسة المطلوبة أو عرض 404 إذا لم تكن موجودة
    return render(request, 'policies/policy_detail.html', {'policy': policy})


@login_required
def edit_policy(request, policy_id):
    policy = get_object_or_404(Policy, id=policy_id)

    # ✅ السماح بالتعديل فقط لصاحب السياسة أو المشرف
    if request.user != policy.author and not request.user.is_superuser:
        messages.error(request, "❌ You do not have permission to edit this policy.")
        return redirect('policy_list')

    if request.method == 'POST':
        form = PolicyForm(request.POST, instance=policy)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Policy updated successfully!")
            return redirect('policy_list')
        else:
            messages.error(request, "⚠️ There was an error updating the policy. Please check the form.")
    else:
        form = PolicyForm(instance=policy)

    return render(request, 'policies/edit_policy.html', {'form': form, 'policy': policy})


@login_required
def add_policy(request):
    if request.method == 'POST':
        form = PolicyForm(request.POST, request.FILES)  # ✅ إضافة request.FILES لدعم تحميل الملفات
        if form.is_valid():
            policy = form.save(commit=False)
            policy.author = request.user  # تعيين المستخدم الحالي كصاحب السياسة
            policy.save()

            # ✅ إضافة إشعار عند إضافة سياسة جديدة
            from notifications.models import Notification  # استيراد الموديل داخل الفيو
            Notification.objects.create(
                recipient=policy.author,  # إرسال الإشعار للمستخدم الذي أضاف السياسة
                message=f"Your policy '{policy.title}' has been submitted for approval."
            )

            messages.success(request, "✅ Policy added successfully and sent for approval.")
            return redirect('policy_list')
    else:
        form = PolicyForm()

    return render(request, 'policies/add_policy.html', {'form': form})



@login_required
def delete_policy(request, policy_id):
    policy = get_object_or_404(Policy, id=policy_id)

    if not request.user.is_superuser:
        messages.error(request, "❌ You do not have permission to delete this policy.")
        return redirect('policy_list')

    # إرسال إشعار إلى صاحب السياسة قبل الحذف
    Notification.objects.create(
        recipient=policy.author,
        message=f"Your policy '{policy.title}' has been deleted by an admin."
    )

    policy.delete()
    messages.success(request, "✅ Policy deleted successfully.")
    
    return redirect('policy_list')