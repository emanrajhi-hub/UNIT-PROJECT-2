from django import forms
from .models import Policy

class PolicyForm(forms.ModelForm):
    class Meta:
        model = Policy
        fields = ['title', 'description', 'category', 'file']  # ✅ إضافة حقل الملف هنا

    file = forms.FileField(
        required=False, 
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )
