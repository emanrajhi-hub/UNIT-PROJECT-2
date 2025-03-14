from django.shortcuts import render ,  get_object_or_404

# Create your views here.
from django.http import HttpResponse
from .models import Policy  # تأكد من استيراد الموديل



def home(request):
    return render(request, 'home.html')



def policy_list(request):
    query = request.GET.get('q', '')  # البحث بالكلمة المفتاحية
    category_filter = request.GET.get('category', '')  # الحصول على الفئة المختارة

    policies = Policy.objects.all()

    if query:
        policies = policies.filter(title__icontains=query)  # البحث في العنوان
    
    if category_filter:
        policies = policies.filter(category=category_filter)  # تصفية حسب الفئة

    return render(request, 'policies/policy_list.html', {'policies': policies, 'query': query, 'category_filter': category_filter})



def policy_detail(request, policy_id):
    policy = get_object_or_404(Policy, id=policy_id)  # جلب السياسة المطلوبة أو عرض 404 إذا لم تكن موجودة
    return render(request, 'policies/policy_detail.html', {'policy': policy})