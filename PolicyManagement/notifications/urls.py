from django.urls import path
from .views import notifications_list, mark_as_read , mark_all_as_read

urlpatterns = [
    path('', notifications_list, name='notifications_list'),
    path('mark-as-read/<int:notification_id>/', mark_as_read, name='mark_as_read'),  # ✅ رابط وضع علامة كمقروء
    path('mark-all-as-read/', mark_all_as_read, name='mark_all_as_read'),  # ✅ إضافة المسار الجديد

]
