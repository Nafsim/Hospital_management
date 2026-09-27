from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import User

class LoginForm(AuthenticationForm):
    role = forms.ChoiceField(
        choices=User.ROLE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select form-select-lg',
            'id': 'id_role'
        })
    )
    username = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Enter your email'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Enter your password'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('username')
        role = cleaned_data.get('role')
        password = cleaned_data.get('password')

        if email and password and role:
            try:
                user = User.objects.get(email=email)
                if user.role != role:
                    raise forms.ValidationError("Selected role does not match this account.")
            except User.DoesNotExist:
                pass   # let AuthenticationForm handle invalid credentials
        return cleaned_data