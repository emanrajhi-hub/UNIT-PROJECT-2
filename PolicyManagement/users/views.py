from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomUserUpdateForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm

from policies.models import Bookmark  # ✅ استيراد Bookmark

from policies.models import Message


@login_required
def profile(request):
    # ✅ جلب كل البوك ماركس للمستخدم مع السياسات المرتبطة بها
    bookmarks = Bookmark.objects.filter(user=request.user).select_related('policy')
    return render(request, 'users/profile.html', {'bookmarks': bookmarks})


# @login_required
# def send_test_email(request):
#     if request.method == "POST":
#         send_mail(
#             'Test Email from Django',
#             'This is a test email sent from Django project using Gmail SMTP.',
#             settings.DEFAULT_FROM_EMAIL,
#             [request.user.email],
#             fail_silently=False,
#         )
#         messages.success(request, "✅ Test email has been sent to your email address.")
#     return redirect('profile')




@login_required
def send_test_email(request):
    if request.method == "POST":

        # 📨 عنوان الإيميل (السطر اللي يظهر في العنوان)
        subject = 'Test Email from Django'

        # ✉️ الرسالة النصية العادية (في حال الإيميل ما يدعم HTML)
        message = 'This is a test email sent from Django project using Gmail SMTP.'

        # 🌟 هذا هو محتوى الإيميل بتنسيق HTML، ويحتوي على الشعار والنص داخل تصميم مرتب
        html_message = """
            <div style="text-align: center; font-family: Arial, sans-serif; padding: 20px;">
                <img src="https://i.postimg.cc/MGyX4zLh/logo.png" alt="Policy Logo" width="200" style="margin-bottom: 20px;" />
                <h2 style="color: #333;">Test Email from Policy Management System</h2>
                <p style="font-size: 16px; color: #555;">
                    This is a test email sent from your Django project using Gmail SMTP.
                </p>
            </div>
        """

        # 🛠️ تنفيذ الإرسال باستخدام send_mail
        send_mail(
            subject,                    # عنوان الإيميل
            message,                    # الرسالة النصية العادية
            settings.DEFAULT_FROM_EMAIL,  # بريد المرسل (من settings.py)
            [request.user.email],       # المرسل إليه هو المستخدم الحالي
            fail_silently=False,        # إظهار الخطأ لو حصل شيء
            html_message=html_message   # 💡 هذا هو الجزء الجديد: محتوى الإيميل بتنسيق HTML
        )

        # ✅ رسالة نجاح تظهر في الموقع
        messages.success(request, "✅ Test email has been sent to your email address.")

    # 🔁 بعد الإرسال نرجع المستخدم إلى صفحة البروفايل
    return redirect('profile')



@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = CustomUserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Your profile has been updated successfully.")
            return redirect('profile')
    else:
        form = CustomUserUpdateForm(instance=request.user)

    return render(request, 'users/edit_profile.html', {'form': form})


@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "✅ Your password was successfully updated.")
            return redirect('profile')
    else:
        form = PasswordChangeForm(user=request.user)
    return render(request, 'users/change_password.html', {'form': form})


@login_required
def user_messages(request):
    messages_list = request.user.message_set.all().order_by('-created_at')
    return render(request, 'users/user_messages.html', {'messages': messages_list})
