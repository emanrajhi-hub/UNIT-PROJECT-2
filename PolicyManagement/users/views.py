from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomUserUpdateForm
from django.contrib.auth import update_session_auth_hash


from django.contrib.auth.forms import PasswordChangeForm


@login_required
def profile(request):
    return render(request, 'users/profile.html')


@login_required
def send_test_email(request):
    if request.method == "POST":
        send_mail(
            'Test Email from Django',  # عنوان البريد
            'This is a test email sent from Django project using Gmail SMTP.',  # نص الرسالة
            settings.DEFAULT_FROM_EMAIL,  # البريد المرسل
            [request.user.email],  # البريد المستقبل
            fail_silently=False,
        )
        messages.success(request, "✅ Test email has been sent to your email address.")
    return redirect('profile')  # إعادة التوجيه إلى صفحة البروفايل بعد الإرسال


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
            update_session_auth_hash(request, user)  # حتى لا يقوم بتسجيل خروج المستخدم بعد تغيير كلمة المرور
            messages.success(request, "✅ Your password was successfully updated.")
            return redirect('profile')
    else:
        form = PasswordChangeForm(user=request.user)
    return render(request, 'users/change_password.html', {'form': form})
