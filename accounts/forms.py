from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import User
from hospitals.models import Hospital
from patients.models import Patient

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

    def clean_username(self):
        email = self.cleaned_data['username'].strip()
        user = User.objects.filter(email__iexact=email).first()
        return user.email if user else email

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('username')
        role = cleaned_data.get('role')
        password = cleaned_data.get('password')

        if email and password and role:
            try:
                user = User.objects.get(email__iexact=email)
                if user.role != role:
                    raise forms.ValidationError("Selected role does not match this account.")
            except User.DoesNotExist:
                pass   
        return cleaned_data


class HospitalCreationForm(forms.ModelForm):
    admin_first_name = forms.CharField(max_length=150, label="Admin First Name")
    admin_last_name = forms.CharField(max_length=150, label="Admin Last Name")
    admin_email = forms.EmailField(label="Admin Email")
    admin_password = forms.CharField(widget=forms.PasswordInput, label="Admin Password")
    admin_phone = forms.CharField(max_length=15, required=False, label="Admin Phone")

    class Meta:
        model = Hospital
        fields = ['name', 'code', 'address', 'city', 'facility_type', 'phone', 'email']   
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


class RegistrationTypeForm(forms.Form):
    registration_type = forms.ChoiceField(
        choices=(('', 'Select Registration Type'), ('patient', 'Patient'), ('hospital', 'Hospital')),
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'registration-type'}),
    )


class PatientRegistrationForm(forms.Form):
    first_name = forms.CharField(max_length=150, label='First Name')
    last_name = forms.CharField(max_length=150, label='Last Name')
    email = forms.EmailField(label='Email Address')
    phone = forms.CharField(max_length=15, label='Phone Number')
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
    )
    confirm_password = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
    )
    date_of_birth = forms.DateField(
        required=False,
        label='Date of Birth',
        widget=forms.DateInput(attrs={'type': 'date'}),
    )
    gender = forms.ChoiceField(
        required=False,
        choices=(('', 'Select Gender'),) + Patient.GENDER_CHOICES,
    )
    blood_group = forms.ChoiceField(
        required=False,
        choices=(('', 'Select Blood Group'),) + Patient.BLOOD_GROUP_CHOICES,
    )
    nid = forms.CharField(max_length=30, required=False, label='National ID')
    address = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 2}),
    )
    city = forms.CharField(max_length=100, required=False)
    emergency_name = forms.CharField(max_length=150, required=False, label='Emergency Contact Name')
    emergency_phone = forms.CharField(max_length=20, required=False, label='Emergency Contact Phone')

    def clean_email(self):
        email = self.cleaned_data['email'].strip()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('An account with this email already exists.')
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', 'Passwords do not match.')
        return cleaned_data


class HospitalRegistrationForm(forms.Form):
    name = forms.CharField(max_length=255, label='Hospital / Facility Name')
    code = forms.CharField(max_length=20, label='Registration Code')
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': 2}))
    city = forms.CharField(max_length=100)
    state = forms.CharField(max_length=100, required=False)
    facility_type = forms.ChoiceField(
        choices=Hospital.FACILITY_TYPE,
        label='Facility Type',
    )
    phone = forms.CharField(max_length=20, label='Facility Phone')
    email = forms.EmailField(required=False, label='Facility Email')
    admin_first_name = forms.CharField(max_length=150, label='Account Holder First Name')
    admin_last_name = forms.CharField(max_length=150, label='Account Holder Last Name')
    admin_email = forms.EmailField(label='Account Email')
    admin_phone = forms.CharField(max_length=15, label='Account Phone')
    admin_password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
    )
    confirm_password = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
    )

    def clean_code(self):
        code = self.cleaned_data['code'].strip()
        if Hospital.objects.filter(code__iexact=code).exists():
            raise forms.ValidationError('A facility with this registration code already exists.')
        return code

    def clean_admin_email(self):
        email = self.cleaned_data['admin_email'].strip()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('An account with this email already exists.')
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('admin_password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', 'Passwords do not match.')
        return cleaned_data