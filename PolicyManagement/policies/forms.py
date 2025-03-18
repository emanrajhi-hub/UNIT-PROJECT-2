from django import forms
from .models import Policy

class PolicyForm(forms.ModelForm):
    class Meta:
        model = Policy
        fields = ['title', 'description', 'category', 'file', 'image']  # ✅ إضافة حقل الصورة مع الحقول الأخرى

    # ✅ حقل رفع ملف السياسة
    file = forms.FileField(
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )

    # ✅ حقل رفع الصورة الخاصة بالسياسة
    image = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )
