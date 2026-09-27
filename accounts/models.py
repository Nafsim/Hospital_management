from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
class User(AbstractUser):
    ROLE_CHOICES = (
        ('moh', 'Ministry of Health (MOH)'),
        ('hospital_admin', 'Hospital Admin'),
        ('doctor', 'Doctor'),
        ('nurse', 'Nurse'),
        ('patient', 'Patient'),
        ('lab', 'Laboratory / Diagnostic'),
        ('counter', 'Counter / Reception'),
        ('bloodbank', 'Blood Bank Staff'),
        ('accountant', 'Accountant'),
    )

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    hospital = models.ForeignKey(
        'hospitals.Hospital',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='staff'
    )
    phone = models.CharField(max_length=15, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'role']

    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"