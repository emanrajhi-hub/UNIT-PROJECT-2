from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.core.paginator import Paginator
from .models import Policy ,Bookmark
from .forms import PolicyForm
from django.contrib import messages
from notifications.models import Notification
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()

# الصفحة الرئيسية
def home(request):
    policies = Policy.objects.order_by('-created_at')
    paginator = Paginator(policies, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'home.html', {'page_obj': page_obj})

# قائمة السياسات مع البحث والتصنيف
def policy_list(request):
    query = request.GET.get('q', '')
    category_filter = request.GET.get('category', '')

    policies = Policy.objects.all()

    if query:
        policies = policies.filter(
            title__icontains=query
        ) | policies.filter(
            description__icontains=query
        )

    if category_filter:
        policies = policies.filter(category=category_filter)

    paginator = Paginator(policies.order_by('-created_at'), 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'policies/policy_list.html', {
        'policies': page_obj,
        'query': query,
        'category_filter': category_filter
    })

# صفحة تفاصيل السياسة
def policy_detail(request, policy_id):
    policy = get_object_or_404(Policy, id=policy_id)
    is_bookmarked = False
    if request.user.is_authenticated:
        is_bookmarked = policy.bookmarked_by.filter(id=request.user.pk).exists()
    return render(request, 'policies/policy_detail.html', {
        'policy': policy,
        'is_bookmarked': is_bookmarked
    })

# إضافة سياسة
@login_required
def add_policy(request):
    if request.method == 'POST':
        form = PolicyForm(request.POST, request.FILES)
        if form.is_valid():
            policy = form.save(commit=False)
            policy.author = request.user
            policy.save()

            Notification.objects.create(
                recipient=policy.author,
                message=f"Your policy '{policy.title}' has been submitted for approval."
            )

            messages.success(request, "✅ Policy added successfully and sent for approval.")
            return redirect('policy_list')
    else:
        form = PolicyForm()

    return render(request, 'policies/add_policy.html', {'form': form})

@login_required
def edit_policy(request, policy_id):
    policy = get_object_or_404(Policy, id=policy_id)

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
            messages.error(request, "⚠️ There was an error updating the policy.")
    else:
        form = PolicyForm(instance=policy)

    return render(request, 'policies/edit_policy.html', {'form': form, 'policy': policy})

@login_required
def delete_policy(request, policy_id):
    policy = get_object_or_404(Policy, id=policy_id)

    if not request.user.is_superuser:
        messages.error(request, "❌ You do not have permission to delete this policy.")
        return redirect('policy_list')

    Notification.objects.create(
        recipient=policy.author,
        message=f"Your policy '{policy.title}' has been deleted by an admin."
    )

    policy.delete()
    messages.success(request, "✅ Policy deleted successfully.")
    
    return redirect('policy_list')

# ✅ toggle bookmark - تم التعديل هنا

@login_required
def toggle_bookmark(request, policy_id):
    policy = get_object_or_404(Policy, id=policy_id)
    
    bookmark, created = Bookmark.objects.get_or_create(user=request.user, policy=policy)
    
    if not created:
        bookmark.delete()
        messages.info(request, "🔖 Removed from bookmarks.")
    else:
        messages.success(request, "✅ Added to bookmarks.")
    
    return redirect('policy_detail', policy_id=policy.id)

# ✅ عرض bookmarks في البروفايل
@login_required
def profile_bookmarks(request):
    bookmarks = request.user.bookmarked_policies.all()
    paginator = Paginator(bookmarks, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'users/profile_bookmarks.html', {'page_obj': page_obj})

# صفحة من نحن
def about_us(request):
    return render(request, 'about_us.html')

# صفحة تواصل معنا
def contact_us(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message_content = request.POST.get('message')

        if name and email and message_content:
            subject = f"New Contact Message from {name}"
            message = f"Sender Name: {name}\nSender Email: {email}\n\nMessage:\n{message_content}"
            from_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = [settings.DEFAULT_FROM_EMAIL]

            send_mail(subject, message, from_email, recipient_list, fail_silently=False)
            messages.success(request, "✅ Your message has been sent successfully!")
            return redirect('contact_us')
        else:
            messages.error(request, "⚠️ Please fill all fields.")

    return render(request, 'contact_us.html')
