from django.urls import path
from .views import policy_list ,  policy_detail

urlpatterns = [
    path('', policy_list, name='policy_list'),

    path('<int:policy_id>/', policy_detail, name='policy_detail'),  # عرض تفاصيل السياسة

]