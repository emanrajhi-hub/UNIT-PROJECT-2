from django.urls import path
from .views import profile, send_test_email, edit_profile , change_password

urlpatterns = [
    path('profile/', profile, name='profile'),
    path('profile/edit/', edit_profile, name='edit_profile'),
    path('send-test-email/', send_test_email, name='send_test_email'),
    path('change-password/', change_password, name='change_password'),  # ✅ رابط تغيير كلمة المرور

]
