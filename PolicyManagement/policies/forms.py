from django import forms
from .models import Policy, Comment, Rating

class PolicyForm(forms.ModelForm):
    class Meta:
        model = Policy
        fields = ['title', 'description', 'category', 'file', 'image']

    file = forms.FileField(
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )

    image = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )

# ✅ نموذج إضافة تعليق
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Write your comment here...'
            })
        }

# ✅ نموذج تقييم النجوم
class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['stars']
        widgets = {
            'stars': forms.Select(attrs={
                'class': 'form-select'
            })
        }
        labels = {
            'stars': 'Rate this policy'
        }
