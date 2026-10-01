from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import User
from hospitals.models import Hospital

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


class HospitalCreationForm(forms.ModelForm):
    admin_first_name = forms.CharField(max_length=150, label="Admin First Name")
    admin_last_name = forms.CharField(max_length=150, label="Admin Last Name")
    admin_email = forms.EmailField(label="Admin Email")
    admin_password = forms.CharField(widget=forms.PasswordInput, label="Admin Password")
    admin_phone = forms.CharField(max_length=15, required=False, label="Admin Phone")

    class Meta:
        model = Hospital
        fields = ['name', 'code', 'address', 'city', 'facility_type', 'phone', 'email']   # ← added city & facility_type
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'facility_type': forms.Select(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }
    def clean_code(self):
        code = self.cleaned_data.get('code')
        if Hospital.objects.filter(code=code).exists():
            raise forms.ValidationError("A hospital with this code already exists.")
        return code

    def clean_admin_email(self):
        email = self.cleaned_data.get('admin_email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email