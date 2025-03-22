from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.core.paginator import Paginator
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model
import os
from django.conf import settings


from .models import Policy, Bookmark, Comment, Rating
from .forms import PolicyForm, CommentForm, RatingForm
from notifications.models import Notification

User = get_user_model()

# الصفحة الرئيسية
# def home(request):
#     policies = Policy.objects.order_by('-created_at')
#     paginator = Paginator(policies, 6)
#     page_number = request.GET.get('page')
#     page_obj = paginator.get_page(page_number)
#     return render(request, 'home.html', {'page_obj': page_obj})

def home(request):
    policies = Policy.objects.order_by('-created_at')

    # حساب متوسط التقييم لكل سياسة
    for policy in policies:
        ratings = policy.ratings.all()
        if ratings.exists():
            avg = sum([r.stars for r in ratings]) / ratings.count()
            policy.average_rating = round(avg, 1)
        else:
            policy.average_rating = 0

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
        policies = policies.filter(title__icontains=query) | policies.filter(description__icontains=query)
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

# صفحة تفاصيل السياسة مع التعليقات والتقييم
def policy_detail(request, policy_id):
    policy = get_object_or_404(Policy, id=policy_id)
    comments = policy.comments.order_by('-created_at')

    # هل تم حفظه بالمفضلة؟
    is_bookmarked = False
    if request.user.is_authenticated:
        is_bookmarked = policy.bookmarked_by.filter(id=request.user.pk).exists()

    # إعداد نماذج التعليق والتقييم
    comment_form = CommentForm()
    rating_form = RatingForm()

    if request.method == 'POST' and request.user.is_authenticated:
        if 'comment' in request.POST:
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.policy = policy
                comment.user = request.user
                comment.save()
                messages.success(request, "✅ Your comment has been added.")
                return redirect('policy_detail', policy_id=policy.id)

        elif 'rate' in request.POST:
            rating_form = RatingForm(request.POST)
            if rating_form.is_valid():
                # تحديث أو إنشاء تقييم جديد لنفس المستخدم والسياسة
                Rating.objects.update_or_create(
                    user=request.user,
                    policy=policy,
                    defaults={'stars': rating_form.cleaned_data['stars']}
                )
                messages.success(request, "⭐ Your rating has been submitted.")
                return redirect('policy_detail', policy_id=policy.id)

    return render(request, 'policies/policy_detail.html', {
        'policy': policy,
        'is_bookmarked': is_bookmarked,
        'comments': comments,
        'comment_form': comment_form,
        'rating_form': rating_form
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
        form = PolicyForm(request.POST, request.FILES, instance=policy)

        if form.is_valid():
            # حذف الصورة إذا طلب المستخدم أو رفع صورة جديدة
            if form.cleaned_data.get('delete_image') or request.FILES.get('image'):
                if policy.image and os.path.isfile(policy.image.path):
                    policy.image.close()  # ✅ إغلاق الملف قبل الحذف
                    os.remove(policy.image.path)
                policy.image = None

            # حذف الملف إذا طلب المستخدم أو رفع ملف جديد
            if form.cleaned_data.get('delete_file') or request.FILES.get('file'):
                if policy.file and os.path.isfile(policy.file.path):
                    policy.file.close()  # ✅ إغلاق الملف قبل الحذف
                    os.remove(policy.file.path)
                policy.file = None

            # تحديث باقي الحقول
            policy.title = form.cleaned_data['title']
            policy.description = form.cleaned_data['description']
            policy.category = form.cleaned_data['category']

            # إعادة إضافة الصورة أو الملف الجديد إن وُجد
            if request.FILES.get('image'):
                policy.image = request.FILES.get('image')
            if request.FILES.get('file'):
                policy.file = request.FILES.get('file')

            policy.save()
            messages.success(request, "✅ Policy updated successfully!")
            return redirect('policy_list')
        else:
            messages.error(request, "⚠️ There was an error updating the policy.")
    else:
        form = PolicyForm(instance=policy)

    return render(request, 'policies/edit_policy.html', {'form': form, 'policy': policy})




# حذف سياسة
@login_required
def delete_policy(request, policy_id):
    policy = get_object_or_404(Policy, id=policy_id)

    # السماح بحذف السياسة إذا كان المستخدم هو صاحبها أو مشرف
    if request.user == policy.author or request.user.is_superuser:
        if request.method == 'POST':
            Notification.objects.create(
                recipient=policy.author,
                message=f"Your policy '{policy.title}' has been deleted."
            )
            policy.delete()
            messages.success(request, "✅ Policy deleted successfully.")
            return redirect('policy_list')
    else:
        messages.error(request, "❌ You do not have permission to delete this policy.")
        return redirect('policy_list')

    return render(request, 'policies/confirm_delete.html', {'policy': policy})


# إضافة أو إزالة Bookmark
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

# عرض Bookmarks في البروفايل
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


@login_required
def dashboard(request):
    total_policies = Policy.objects.count()
    approved_policies = Policy.objects.filter(status='Approved').count()
    pending_policies = Policy.objects.filter(status='Pending').count()
    rejected_policies = Policy.objects.filter(status='Rejected').count()
    total_users = User.objects.count()

    return render(request, 'policies/dashboard.html', {
        'total_policies': total_policies,
        'approved_policies': approved_policies,
        'pending_policies': pending_policies,
        'rejected_policies': rejected_policies,
        'total_users': total_users,
    })
