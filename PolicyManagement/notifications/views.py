from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Notification

@login_required
def notifications_list(request):
    if request.user.is_superuser:  # ✅ المشرف يرى جميع الإشعارات
        notifications = Notification.objects.all().order_by('-created_at')
    else:  # ✅ المستخدم العادي يرى إشعاراته فقط
        notifications = Notification.objects.filter(recipient=request.user).order_by('-created_at')

    # ✅ طباعة الإشعارات في سطر الأوامر للتأكد من جلب البيانات بشكل صحيح
    print(f"🔹 Notifications for {request.user.username}: {notifications}")

    return render(request, 'notifications/notifications_list.html', {'notifications': notifications})



@login_required
def mark_as_read(request, notification_id):
    # ✅ إذا كان المستخدم مشرفًا، يمكنه قراءة أي إشعار
    if request.user.is_superuser:
        notification = get_object_or_404(Notification, id=notification_id)
    else:
        # ✅ المستخدم العادي لا يستطيع قراءة إلا إشعاراته الخاصة
        notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)

    notification.is_read = True
    notification.save()

    return redirect('notifications_list')  # إعادة توجيه المستخدم إلى قائمة الإشعارات بعد التحديث