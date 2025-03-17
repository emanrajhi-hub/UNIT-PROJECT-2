from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponseForbidden
from django.core.paginator import Paginator
from .models import Policy
from .forms import PolicyForm
from django.contrib import messages
from notifications.models import Notification
from django.core.mail import send_mail
from django.conf import settings



def home(request):
    policies = Policy.objects.order_by('-created_at')
    paginator = Paginator(policies, 6)  # عرض 6 سياسات في كل صفحة
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'home.html', {'page_obj': page_obj})


# def policy_list(request):
#     query = request.GET.get('q', '')
#     category_filter = request.GET.get('category', '')

#     policies = Policy.objects.all()

#     if query:
#         policies = policies.filter(title__icontains=query)
    
#     if category_filter:
#         policies = policies.filter(category=category_filter)

#     return render(request, 'policies/policy_list.html', {'policies': policies, 'query': query, 'category_filter': category_filter})

def policy_list(request):
    query = request.GET.get('q', '')
    category_filter = request.GET.get('category', '')

    policies = Policy.objects.all()

    if query:
        policies = policies.filter(
            title__icontains=query
        ) | policies.filter(
            description__icontains=query
        )  # ✅ البحث في العنوان أو الوصف

    if category_filter:
        policies = policies.filter(category=category_filter)

    paginator = Paginator(policies.order_by('-created_at'), 6)  # ✅ pagination مع 6 عناصر لكل صفحة
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'policies/policy_list.html', {
        'policies': page_obj,  # نرسل page_obj الآن بدلًا من policies
        'query': query,
        'category_filter': category_filter
    })



def policy_detail(request, policy_id):
    policy = get_object_or_404(Policy, id=policy_id)
    return render(request, 'policies/policy_detail.html', {'policy': policy})


@login_required
def edit_policy(request, policy_id):
    policy = get_object_or_404(Policy, id=policy_id)

    if request.user != policy.author and not request.user.is_superuser:
        messages.error(request, "❌ You do not have permission to edit this policy.")
        return redirect('policy_list')

    if request.method == 'POST':
        form = PolicyForm(request.POST, instance=policy)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Policy updated successfully!")
            return redirect('policy_list')
        else:
            messages.error(request, "⚠️ There was an error updating the policy.")
    else:
        form = PolicyForm(instance=policy)

    return render(request, 'policies/edit_policy.html', {'form': form, 'policy': policy})


@login_required
def add_policy(request):
    if request.method == 'POST':
        form = PolicyForm(request.POST, request.FILES)
        if form.is_valid():
            policy = form.save(commit=False)
            policy.author = request.user
            policy.save()

            Notification.objects.create(
                recipient=policy.author,
                message=f"Your policy '{policy.title}' has been submitted for approval."
            )

            messages.success(request, "✅ Policy added successfully and sent for approval.")
            return redirect('policy_list')
    else:
        form = PolicyForm()

    return render(request, 'policies/add_policy.html', {'form': form})


@login_required
def delete_policy(request, policy_id):
    policy = get_object_or_404(Policy, id=policy_id)

    if not request.user.is_superuser:
        messages.error(request, "❌ You do not have permission to delete this policy.")
        return redirect('policy_list')

    Notification.objects.create(
        recipient=policy.author,
        message=f"Your policy '{policy.title}' has been deleted by an admin."
    )

    policy.delete()
    messages.success(request, "✅ Policy deleted successfully.")
    
    return redirect('policy_list')


def about_us(request):
    return render(request, 'about_us.html')

def contact_us(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message_content = request.POST.get('message')

        if name and email and message_content:
            subject = f"New Contact Message from {name}"
            message = f"Sender Name: {name}\nSender Email: {email}\n\nMessage:\n{message_content}"
            from_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = [settings.DEFAULT_FROM_EMAIL]  # الإيميل الذي تريد أن تصلك عليه الرسائل

            send_mail(subject, message, from_email, recipient_list, fail_silently=False)
            messages.success(request, "✅ Your message has been sent successfully!")

            return redirect('contact_us')
        else:
            messages.error(request, "⚠️ Please fill all fields.")

    return render(request, 'contact_us.html')