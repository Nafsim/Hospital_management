from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Staff(models.Model):
    DEPARTMENT_CHOICES = (
        ('general', 'General Medicine'),
        ('cardiology', 'Cardiology'),
        ('neurology', 'Neurology'),
        ('orthopedics', 'Orthopedics'),
        ('pediatrics', 'Pediatrics'),
        ('surgery', 'Surgery'),
        ('radiology', 'Radiology'),
        ('pathology', 'Pathology'),
        ('emergency', 'Emergency'),
        ('icu', 'ICU'),
        ('administration', 'Administration'),
        ('pharmacy', 'Pharmacy'),
        ('laboratory', 'Laboratory'),
        ('blood_bank', 'Blood Bank'),
        ('accounting', 'Accounting'),
        ('reception', 'Reception'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='staff_profile')
    hospital = models.ForeignKey(
        'hospitals.Hospital',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='staff_members'
    )
    employee_id = models.CharField(max_length=20, unique=True)
    department = models.CharField(max_length=50, choices=DEPARTMENT_CHOICES)
    designation = models.CharField(max_length=100)
    date_of_joining = models.DateField()
    salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    qualification = models.TextField(blank=True)
    specialization = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.employee_id} - {self.user.get_full_name()}"
