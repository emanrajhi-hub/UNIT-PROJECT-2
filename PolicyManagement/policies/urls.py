from django.urls import path
from .views import policy_list ,  policy_detail, add_policy ,  edit_policy

urlpatterns = [
    path('', policy_list, name='policy_list'),

    path('<int:policy_id>/', policy_detail, name='policy_detail'),  # عرض تفاصيل السياسة

    path('add/', add_policy, name='add_policy'),  # ✅ إضافة مسار إضافة السياسة


    path('edit/<int:policy_id>/', edit_policy, name='edit_policy'),


]