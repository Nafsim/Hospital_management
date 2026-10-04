from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.utils import timezone


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


class Notice(models.Model):
    PRIORITY_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    )

    TYPE_CHOICES = (
        ('general', 'General'),
        ('announcement', 'Announcement'),
        ('alert', 'Alert'),
        ('maintenance', 'Maintenance'),
        ('policy', 'Policy Update'),
    )

    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    )

    title = models.CharField(max_length=255)
    content = models.TextField()
    notice_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='general')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='published')

    hospital = models.ForeignKey(
        'hospitals.Hospital',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notices'
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='notices_created'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    publish_date = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class SystemSettings(models.Model):
    company_name = models.CharField(max_length=255, default="NHIMS")
    company_email = models.EmailField(default="info@nhims.gov.bd")
    phone = models.CharField(max_length=30, blank=True, default="+880")
    address = models.TextField(blank=True, default="")

    TIMEZONE_CHOICES = (
        ('Asia/Dhaka', 'Asia/Dhaka (GMT+6)'),
        ('UTC', 'UTC'),
        ('Asia/Kolkata', 'Asia/Kolkata (GMT+5:30)'),
        ('Asia/Karachi', 'Asia/Karachi (GMT+5)'),
    )
    CURRENCY_CHOICES = (
        ('BDT', 'BDT (৳)'),
        ('USD', 'USD ($)'),
        ('EUR', 'EUR (€)'),
        ('INR', 'INR (₹)'),
    )
    DATE_FORMAT_CHOICES = (
        ('DD-MM-YYYY', 'DD-MM-YYYY'),
        ('MM-DD-YYYY', 'MM-DD-YYYY'),
        ('YYYY-MM-DD', 'YYYY-MM-DD'),
    )

    timezone = models.CharField(max_length=50, choices=TIMEZONE_CHOICES, default='Asia/Dhaka')
    currency = models.CharField(max_length=10, choices=CURRENCY_CHOICES, default='BDT')
    date_format = models.CharField(max_length=20, choices=DATE_FORMAT_CHOICES, default='DD-MM-YYYY')
    maintenance_mode = models.BooleanField(default=False)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "System Settings"
        verbose_name_plural = "System Settings"

    def __str__(self):
        return "System Settings"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj
class Department(models.Model):
    DEPARTMENT_CHOICES = (
        ('emergency', 'Emergency'),
        ('cardiology', 'Cardiology'),
        ('neurology', 'Neurology'),
        ('orthopedics', 'Orthopedics'),
        ('pediatrics', 'Pediatrics'),
        ('gynecology', 'Gynecology & Obstetrics'),
        ('medicine', 'Internal Medicine'),
        ('surgery', 'General Surgery'),
        ('dermatology', 'Dermatology'),
        ('ent', 'ENT'),
        ('ophthalmology', 'Ophthalmology'),
        ('psychiatry', 'Psychiatry'),
        ('oncology', 'Oncology'),
        ('urology', 'Urology'),
        ('nephrology', 'Nephrology'),
        ('gastroenterology', 'Gastroenterology'),
        ('radiology', 'Radiology'),
        ('laboratory', 'Laboratory'),
        ('pharmacy', 'Pharmacy'),
        ('blood_bank', 'Blood Bank'),
        ('icu', 'ICU'),
        ('nicu', 'NICU'),
        ('ccu', 'CCU'),
        ('physiotherapy', 'Physiotherapy'),
        ('dental', 'Dental'),
        ('medical_records', 'Medical Records'),
        ('administration', 'Administration'),
    )

    hospital = models.ForeignKey(
        'hospitals.Hospital',
        on_delete=models.CASCADE,
        related_name='departments'
    )
    name = models.CharField(max_length=50, choices=DEPARTMENT_CHOICES)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(
                fields=['hospital', 'name'],
                name='unique_department_per_hospital'
            )
        ]

    def __str__(self):
        return self.get_name_display()

class HospitalDocument(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('archived', 'Archived'),
    )

    hospital = models.ForeignKey(
        'hospitals.Hospital',
        on_delete=models.CASCADE,
        related_name='hospital_documents'
    )

    name = models.CharField(max_length=255)

    file = models.FileField(
        upload_to='hospital_documents/'
    )

    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='hospital_documents_uploaded'
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active'
    )

    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
class Payroll(models.Model):
    STATUS_CHOICES = (
        ('paid', 'Paid'),
        ('pending', 'Pending'),
    )

    hospital = models.ForeignKey(
        'hospitals.Hospital',
        on_delete=models.CASCADE,
        related_name='payroll_records'
    )

    staff = models.ForeignKey(
    'staff.Staff',
    on_delete=models.CASCADE,
    related_name='payroll_records'
)

    salary_month = models.DateField()

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-salary_month', '-created_at']

    def __str__(self):
        return f"{self.staff} - {self.salary_month.strftime('%B %Y')}"    
