from django import forms
from django.contrib.auth import get_user_model
from allauth.account.forms import SignupForm

User = get_user_model()

# ✅ نموذج التسجيل المخصص (Allauth)
class CustomSignupForm(SignupForm):
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
    ]
    gender = forms.ChoiceField(choices=GENDER_CHOICES, widget=forms.RadioSelect, label="Gender")

    def save(self, request):
        user = super(CustomSignupForm, self).save(request)
        user.gender = self.cleaned_data['gender']
        user.save()
        return user

# ✅ نموذج تعديل الملف الشخصي
class CustomUserUpdateForm(forms.ModelForm):
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
    ]
    gender = forms.ChoiceField(choices=GENDER_CHOICES, widget=forms.RadioSelect, label="Gender")

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'gender']  # الحقول المتاحة للتعديل
