from django.urls import path
from . import views

urlpatterns = [
    path('', views.policy_list, name='policy_list'),
    path('<int:policy_id>/', views.policy_detail, name='policy_detail'),
    path('add/', views.add_policy, name='add_policy'),
    path('edit/<int:policy_id>/', views.edit_policy, name='edit_policy'),
    path('delete/<int:policy_id>/', views.delete_policy, name='delete_policy'),

    # ✅ مسار toggle للـ bookmark (إضافة / إزالة)
    path('bookmark/toggle/<int:policy_id>/', views.toggle_bookmark, name='toggle_bookmark'),

    # ✅ صفحة عرض جميع bookmarks داخل صفحة البروفايل
    path('bookmarks/', views.profile_bookmarks, name='profile_bookmarks'),
]
