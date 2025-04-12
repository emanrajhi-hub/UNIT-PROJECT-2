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

from .models import Message

from django.urls import reverse  



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


# def contact_us(request):
#     if request.method == 'POST':
#         name = request.POST.get('name')
#         email = request.POST.get('email')
#         message_content = request.POST.get('message')

#         if name and email and message_content:
#             subject = f"New Contact Message from {name}"
#             message = f"Sender Name: {name}\nSender Email: {email}\n\nMessage:\n{message_content}"
#             from_email = settings.DEFAULT_FROM_EMAIL
#             recipient_list = [settings.DEFAULT_FROM_EMAIL]

#             # 🟢 إرسال الإيميل
#             send_mail(subject, message, from_email, recipient_list, fail_silently=False)

#             # 🟢 تخزين الرسالة في قاعدة البيانات
#             Message.objects.create(
#                 user=request.user if request.user.is_authenticated else None,
#                 name=name,
#                 email=email,
#                 content=message_content
#             )

#             messages.success(request, "✅ Your message has been sent and saved successfully!")
#             return redirect('contact_us')
#         else:
#             messages.error(request, "⚠️ Please fill all fields.")

#     return render(request, 'contact_us.html')



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

            # 🟢 إرسال الإيميل
            send_mail(subject, message, from_email, recipient_list, fail_silently=False)

            # 🟢 تخزين الرسالة في قاعدة البيانات
            new_msg = Message.objects.create(
                user=request.user if request.user.is_authenticated else None,
                name=name,
                email=email,
                content=message_content
            )

            # ✅ إرسال إشعار للإدمنين داخل الموقع
            admin_users = User.objects.filter(is_staff=True)
            for admin in admin_users:
                Notification.objects.create(
                    recipient=admin,
                    message=f"📩 New contact message received from {name}.",
                    link= reverse('message_list')  # عدّل الرابط لو عندك مسار ثاني لعرض الرسائل
                )

            messages.success(request, "✅ Your message has been sent and saved successfully!")
            return redirect('contact_us')
        else:
            messages.error(request, "⚠️ Please fill all fields.")

    return render(request, 'contact_us.html')


# @login_required
# def dashboard(request):
#     total_policies = Policy.objects.count()
#     approved_policies = Policy.objects.filter(status='Approved').count()
#     pending_policies = Policy.objects.filter(status='Pending').count()
#     rejected_policies = Policy.objects.filter(status='Rejected').count()
#     total_users = User.objects.count()

#     # ✅ AI Suggestions (English)
#     ai_suggestions = []
#     if pending_policies > 5:
#         ai_suggestions.append("🔔 More than 5 policies are pending review. Please check them soon.")
    
#     if rejected_policies > 0:
#         ai_suggestions.append(f"❌ There are {rejected_policies} rejected policies. Consider reviewing and updating them.")
    
#     if approved_policies > total_policies / 2 and total_policies > 0:
#         ai_suggestions.append("✅ Over half of the policies have been approved. Keep up the good work!")
    
#     if total_users > 10:
#         ai_suggestions.append("👥 Your platform is growing! Monitor user activities and notifications closely.")

#     # ✅ Latest Activities based on notifications
#     #latest_notifications = Notification.objects.order_by('-created_at')[:5]

#     if request.user.is_superuser:
#        latest_notifications = Notification.objects.order_by('-created_at')[:5]
#     else:
#        latest_notifications = Notification.objects.filter(recipient=request.user).order_by('-created_at')[:5]


#     latest_activities = []
#     for notif in latest_notifications:
#         if notif.link:
#           activity = f'<a href="{notif.link}">{notif.message}</a>'
#         else:
#           activity = notif.message
#         latest_activities.append(activity)



#     return render(request, 'policies/dashboard.html', {
#         'total_policies': total_policies,
#         'approved_policies': approved_policies,
#         'pending_policies': pending_policies,
#         'rejected_policies': rejected_policies,
#         'total_users': total_users,
#         'ai_suggestions': ai_suggestions,
#         'latest_activities': latest_activities,
#     })



@login_required
def dashboard(request):
    if request.user.is_superuser:
        policies = Policy.objects.all()
    else:
        policies = Policy.objects.filter(author=request.user)

    total_policies = policies.count()
    approved_policies = policies.filter(status='Approved').count()
    pending_policies = policies.filter(status='Pending').count()
    rejected_policies = policies.filter(status='Rejected').count()
    
    total_users = User.objects.count()

    # ✅ AI Suggestions (English)
    ai_suggestions = []
    if pending_policies > 5:
        ai_suggestions.append("🔔 More than 5 policies are pending review. Please check them soon.")
    
    if rejected_policies > 0:
        ai_suggestions.append(f"❌ There are {rejected_policies} rejected policies. Consider reviewing and updating them.")
    
    if approved_policies > total_policies / 2 and total_policies > 0:
        ai_suggestions.append("✅ Over half of the policies have been approved. Keep up the good work!")
    
    if total_users > 10:
        ai_suggestions.append("👥 Your platform is growing! Monitor user activities and notifications closely.")

    # ✅ Latest Activities based on notifications
   # latest_notifications = Notification.objects.order_by('-created_at')[:5]

    if request.user.is_superuser:
     latest_notifications = Notification.objects.order_by('-created_at')[:5]
    else:
     latest_notifications = Notification.objects.filter(recipient=request.user).order_by('-created_at')[:5]

    latest_activities = []
    for notif in latest_notifications:
        if notif.link:
            activity = f'<a href="{notif.link}">{notif.message}</a>'
        else:
            activity = notif.message
        latest_activities.append(activity)

    return render(request, 'policies/dashboard.html', {
        'total_policies': total_policies,
        'approved_policies': approved_policies,
        'pending_policies': pending_policies,
        'rejected_policies': rejected_policies,
        'total_users': total_users,
        'ai_suggestions': ai_suggestions,
        'latest_activities': latest_activities,
    })



#from .models import Message
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.timezone import now

@staff_member_required  # فقط للمشرفين
def message_list(request):

    if request.GET.get('replied') == '1':
       messages.success(request, "✅ Reply sent successfully and saved.")



    messages_list = Message.objects.order_by('-created_at')
    return render(request, 'message_list.html', {
        'messages': messages_list
    })


from django.core.mail import send_mail
#from django.utils.timezone import now
#from .models import Message

#from django.contrib.admin.views.decorators import staff_member_required


# @staff_member_required
# def reply_message(request, message_id):
#     msg = get_object_or_404(Message, id=message_id)

#     if request.method == 'POST':
#         reply_text = request.POST.get('reply')
#         if reply_text:
#             # حفظ الرد في قاعدة البيانات
#             msg.reply = reply_text
#             msg.is_replied = True
#             msg.replied_at = now()
#             msg.save()

#             # إرسال الرد عبر الإيميل
#             subject = f"Reply to your message - Policy Management"
#             email_body = f"Dear {msg.name},\n\nYour message:\n{msg.content}\n\nAdmin reply:\n{reply_text}\n\nThank you."
#             send_mail(subject, email_body, settings.DEFAULT_FROM_EMAIL, [msg.email], fail_silently=False)

#             messages.success(request, "✅ Reply sent successfully and saved.")
#             return redirect('message_list')
#         else:
#             messages.error(request, "⚠️ Reply cannot be empty.")

#     return render(request, 'reply_message.html', {'message': msg})



from notifications.models import Notification  # تأكد أنه مستورد

from django.urls import reverse

@staff_member_required
def reply_message(request, message_id):
    msg = get_object_or_404(Message, id=message_id)

    if request.method == 'POST':
        reply_text = request.POST.get('reply')
        if reply_text:
            # حفظ الرد في قاعدة البيانات
            msg.reply = reply_text
            msg.is_replied = True
            msg.replied_at = now()
            msg.save()

            # إرسال الرد عبر الإيميل
            subject = f"Reply to your message - Policy Management"
            email_body = f"Dear {msg.name},\n\nYour message:\n{msg.content}\n\nAdmin reply:\n{reply_text}\n\nThank you."
            send_mail(subject, email_body, settings.DEFAULT_FROM_EMAIL, [msg.email], fail_silently=False)

            # ✅ إشعار للمستخدم في النظام (إذا كان مسجّل دخول)
            if msg.user:
                Notification.objects.create(
                    recipient=msg.user,
                    message=f"📬 You have a new reply to your contact message. Click to view.",
                    link="/users/my-messages/"  # عدل المسار إذا كان مختلف
                )

            messages.success(request, "✅ Reply sent successfully and saved.")
           # return redirect('message_list') + '?replied=1'
          #  return redirect(reverse('message_list') + '?replied=1')
            return redirect(reverse('message_list') + '?replied=1&once=1')


        else:
            messages.error(request, "⚠️ Reply cannot be empty.")

    return render(request, 'reply_message.html', {'message': msg})

