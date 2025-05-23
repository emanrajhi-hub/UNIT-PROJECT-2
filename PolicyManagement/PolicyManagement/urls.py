"""
URL configuration for PolicyManagement project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path , include
from policies.views import home  # استيراد الصفحة الرئيسية
from django.conf import settings  # تأكد من استيراده
from django.conf.urls.static import static  # تأكد من استيراده
from policies.views import home, about_us, contact_us , message_list , reply_message





urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),  # الصفحة الرئيسية

    path('about/', about_us, name='about_us'),  # ✅ رابط About Us هنا

    path('contact/', contact_us, name='contact_us'),  # ✅ رابط Contact Us هنا



    path('accounts/', include('allauth.urls')),

    path('users/', include('users.urls')),

    path('policies/', include('policies.urls')),

    path('approvals/', include('approvals.urls')),  # ✅ إضافة مسار approvals

    path('notifications/', include('notifications.urls')),  # ✅ إضافة مسار notifications

    path('messages/', message_list, name='message_list'),

    path('messages/<int:message_id>/reply/', reply_message, name='reply_message'),


]


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)