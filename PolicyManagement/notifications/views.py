from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Notification
from django.contrib import messages  # ✅ استيراد messages لتجنب الأخطاء


def get_unread_notifications_count(request):
    """ دالة لإضافة عدد الإشعارات غير المقروءة إلى جميع الصفحات """
    if request.user.is_authenticated:
        return {'unread_count': Notification.objects.filter(recipient=request.user, is_read=False).count()}
    return {'unread_count': 0}

@login_required
def notifications_list(request):
    if request.user.is_superuser:
        notifications = Notification.objects.all().order_by('-created_at')
    else:
        notifications = Notification.objects.filter(recipient=request.user).order_by('-created_at')

    # ✅ حساب عدد الإشعارات غير المقروءة
    unread_count = notifications.filter(is_read=False).count()

    return render(request, 'notifications/notifications_list.html', {
        'notifications': notifications,
        'unread_count': unread_count  # ✅ تمرير العدد إلى الـ template
    })


@login_required
def mark_as_read(request, notification_id):
    """ ✅ تمييز إشعار معين كمقروء """
    if request.user.is_superuser:
        notification = get_object_or_404(Notification, id=notification_id)
    else:
        notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)

    notification.is_read = True
    notification.save()

    return redirect('notifications_list')


@login_required
def mark_all_as_read(request):
    """ ✅ تمييز جميع الإشعارات كمقروءة """
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    messages.success(request, "✅ All notifications marked as read.")
    return redirect('notifications_list')
