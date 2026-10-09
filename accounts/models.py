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
        ('pharmacy', 'Pharmacy'),
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
    pharmacy_access = models.BooleanField(default=False)
    blood_bank_access = models.BooleanField(default=False)
    diagnostics_access = models.BooleanField(default=False)
    patients_access = models.BooleanField(default=False)
    staff_access = models.BooleanField(default=False)


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
class Medicine(models.Model):
    CATEGORY_CHOICES = (
        ('tablet', 'Tablet'),
        ('capsule', 'Capsule'),
        ('syrup', 'Syrup'),
        ('injection', 'Injection'),
        ('cream', 'Cream'),
        ('ointment', 'Ointment'),
        ('drops', 'Drops'),
        ('inhaler', 'Inhaler'),
        ('other', 'Other'),
    )

    UNIT_CHOICES = (
        ('tablet', 'Tablet'),
        ('capsule', 'Capsule'),
        ('bottle', 'Bottle'),
        ('vial', 'Vial'),
        ('tube', 'Tube'),
        ('box', 'Box'),
        ('piece', 'Piece'),
    )

    hospital = models.ForeignKey(
        'hospitals.Hospital',
        on_delete=models.CASCADE,
        related_name='medicines'
    )
    name = models.CharField(max_length=150)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES)
    strength = models.CharField(max_length=50, blank=True)
    stock = models.PositiveIntegerField(default=0)
    unit = models.CharField(max_length=30, choices=UNIT_CHOICES)
    reorder_level = models.PositiveIntegerField(default=20)
    expiry_date = models.DateField(null=True, blank=True)
    batch_number = models.CharField(max_length=50, blank=True)
    supplier = models.CharField(max_length=150, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

class Blood(models.Model):
    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
    ]

    COMPONENT_CHOICES = [
        ('whole', 'Whole Blood'),
        ('rbc', 'Red Blood Cells'),
        ('plasma', 'Plasma'),
        ('platelets', 'Platelets'),
        ('cryo', 'Cryoprecipitate'),
    ]

    hospital = models.ForeignKey(
        'hospitals.Hospital',
        on_delete=models.CASCADE,
        related_name='blood_units'
    )
    blood_group = models.CharField(max_length=5, choices=BLOOD_GROUP_CHOICES)
    component = models.CharField(max_length=20, choices=COMPONENT_CHOICES, default='whole')
    units = models.PositiveIntegerField(default=0)
    reorder_level = models.PositiveIntegerField(default=5)
    expiry_date = models.DateField(null=True, blank=True)
    bag_number = models.CharField(max_length=50, blank=True)
    donor_name = models.CharField(max_length=100, blank=True)
    collection_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['blood_group', 'component']

    def __str__(self):
        return f"{self.blood_group} - {self.get_component_display()} ({self.units} units)"    

class DiagnosticTest(models.Model):
    CATEGORY_CHOICES = [
        ('blood', 'Blood Test'),
        ('urine', 'Urine Test'),
        ('imaging', 'Imaging'),
        ('pathology', 'Pathology'),
        ('microbiology', 'Microbiology'),
        ('cardiology', 'Cardiology'),
        ('other', 'Other'),
    ]

    SAMPLE_CHOICES = [
        ('blood', 'Blood'),
        ('urine', 'Urine'),
        ('stool', 'Stool'),
        ('swab', 'Swab'),
        ('tissue', 'Tissue'),
        ('none', 'None'),
    ]

    hospital = models.ForeignKey(
        'hospitals.Hospital',
        on_delete=models.CASCADE,
        related_name='diagnostic_tests'
    )
    name = models.CharField(max_length=150)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='blood')
    sample_type = models.CharField(max_length=20, choices=SAMPLE_CHOICES, default='blood')
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    report_time = models.CharField(max_length=50, blank=True, help_text="e.g. 24 hours, 2 days")
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name



class Facility(models.Model):
    TYPE_CHOICES = [
        ('ward', 'Ward'),
        ('icu', 'ICU'),
        ('ot', 'Operation Theater'),
        ('lab', 'Laboratory'),
        ('pharmacy', 'Pharmacy'),
        ('blood_bank', 'Blood Bank'),
        ('emergency', 'Emergency'),
        ('opd', 'OPD'),
        ('radiology', 'Radiology'),
        ('other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('maintenance', 'Under Maintenance'),
    ]

    hospital = models.ForeignKey(
        'hospitals.Hospital',
        on_delete=models.CASCADE,
        related_name='facilities'
    )
    name = models.CharField(max_length=150)
    facility_type = models.CharField(max_length=30, choices=TYPE_CHOICES, default='ward')
    capacity = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    location = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = "Facilities"

    def __str__(self):
        return f"{self.name} ({self.get_facility_type_display()})"


class MOHJoinRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    hospital = models.ForeignKey(
        'hospitals.Hospital',
        on_delete=models.CASCADE,
        related_name='moh_join_requests'
    )
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )
    hospital_name = models.CharField(max_length=200)
    registration_number = models.CharField(max_length=100)
    location = models.CharField(max_length=255)
    contact_person = models.CharField(max_length=150)
    contact_phone = models.CharField(max_length=20)
    contact_email = models.EmailField()
    reason = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    moh_note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.hospital_name} - {self.get_status_display()}"

class EmergencyContact(models.Model):
    RELATION_CHOICES = [
        ('spouse', 'Spouse'),
        ('father', 'Father'),
        ('mother', 'Mother'),
        ('brother', 'Brother'),
        ('sister', 'Sister'),
        ('son', 'Son'),
        ('daughter', 'Daughter'),
        ('friend', 'Friend'),
        ('colleague', 'Colleague'),
        ('other', 'Other'),
    ]

    hospital = models.ForeignKey(
        'hospitals.Hospital',
        on_delete=models.CASCADE,
        related_name='emergency_contacts'
    )
    staff = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='emergency_contacts'
    )
    contact_name = models.CharField(max_length=150)
    relation = models.CharField(max_length=20, choices=RELATION_CHOICES, default='other')
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_primary', 'contact_name']

    def __str__(self):
        return f"{self.contact_name} ({self.get_relation_display()})"

class DoctorPatient(models.Model):
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='doctor_patients'
    )
    hospital = models.ForeignKey(
        'hospitals.Hospital',
        on_delete=models.CASCADE,
        related_name='doctor_patients'
    )
    patient_name = models.CharField(max_length=150)
    patient_id = models.CharField(max_length=50)
    phone = models.CharField(max_length=20, blank=True)
    gender = models.CharField(max_length=20, blank=True)
    age = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.patient_name} - {self.patient_id}"


class DoctorSchedule(models.Model):
    STATUS_CHOICES = (
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )

    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='doctor_schedules'
    )
    hospital = models.ForeignKey(
        'hospitals.Hospital',
        on_delete=models.CASCADE,
        related_name='doctor_schedules'
    )
    patient_name = models.CharField(max_length=150)
    patient_id = models.CharField(max_length=50, blank=True)
    schedule_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='scheduled'
    )
    notes = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['schedule_date', 'start_time']

    def __str__(self):
        return f"{self.doctor.get_full_name()} - {self.patient_name}"
class DoctorPrescription(models.Model):
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='doctor_prescriptions'
    )
    hospital = models.ForeignKey(
        'hospitals.Hospital',
        on_delete=models.CASCADE,
        related_name='doctor_prescriptions'
    )
    patient = models.ForeignKey(
        DoctorPatient,
        on_delete=models.CASCADE,
        related_name='prescriptions'
    )
    medicine_name = models.CharField(max_length=150)
    dosage = models.CharField(max_length=100)
    frequency = models.CharField(max_length=50)
    meal_timing = models.CharField(max_length=20)
    duration = models.CharField(max_length=50)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.patient.patient_name} - {self.medicine_name}"
class DoctorReferral(models.Model):
    PRIORITY_CHOICES = (
        ('routine', 'Routine'),
        ('urgent', 'Urgent'),
        ('emergency', 'Emergency'),
    )

    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )

    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_referrals'
    )
    patient = models.ForeignKey(
        DoctorPatient,
        on_delete=models.CASCADE,
        related_name='referrals'
    )
    specialist = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_referrals'
    )
    reason = models.TextField()
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='routine'
    )
    document = models.FileField(
        upload_to='referrals/',
        blank=True,
        null=True
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.patient.patient_name} - {self.specialist.get_full_name()}"    

class DoctorProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='doctor_profile'
    )
    registration_number = models.CharField(max_length=50, blank=True)
    specialization = models.CharField(max_length=100, blank=True)
    department = models.CharField(max_length=100, blank=True)
    qualification = models.CharField(max_length=255, blank=True, help_text="e.g. MBBS, FCPS, MD")
    experience_years = models.PositiveIntegerField(default=0)
    bio = models.TextField(blank=True)
    address = models.TextField(blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=20, blank=True)
    blood_group = models.CharField(max_length=5, blank=True)
    profile_image = models.ImageField(upload_to='doctor_profiles/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.registration_number}"

class VitalSign(models.Model):
    hospital = models.ForeignKey(
        'hospitals.Hospital',
        on_delete=models.CASCADE,
        related_name='vital_signs'
    )
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='vital_signs_recorded'
    )
    patient = models.ForeignKey(
        'patients.Patient',
        on_delete=models.CASCADE,
        related_name='vital_signs'
    )
    temperature = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True, help_text="°C")
    pulse = models.PositiveIntegerField(null=True, blank=True, help_text="bpm")
    blood_pressure = models.CharField(max_length=20, blank=True, help_text="e.g. 120/80")
    respiratory_rate = models.PositiveIntegerField(null=True, blank=True, help_text="breaths/min")
    spo2 = models.PositiveIntegerField(null=True, blank=True, help_text="%")
    blood_sugar = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True, help_text="mg/dL")
    weight = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True, help_text="kg")
    height = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True, help_text="cm")
    notes = models.TextField(blank=True)
    recorded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-recorded_at']

    def __str__(self):
        return f"{self.patient} - {self.recorded_at.strftime('%d %b %Y %H:%M')}"    

class NursingNote(models.Model):
    NOTE_TYPE_CHOICES = [
        ('general', 'General'),
        ('observation', 'Observation'),
        ('medication', 'Medication'),
        ('procedure', 'Procedure'),
        ('incident', 'Incident'),
        ('handover', 'Handover'),
    ]

    hospital = models.ForeignKey(
        'hospitals.Hospital',
        on_delete=models.CASCADE,
        related_name='nursing_notes'
    )
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='nursing_notes_recorded'
    )
    patient = models.ForeignKey(
        'patients.Patient',
        on_delete=models.CASCADE,
        related_name='nursing_notes'
    )
    note_type = models.CharField(max_length=20, choices=NOTE_TYPE_CHOICES, default='general')
    title = models.CharField(max_length=200)
    note = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.patient} - {self.title}"    
class NurseProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='nurse_profile'
    )
    registration_number = models.CharField(max_length=50, blank=True)
    department = models.CharField(max_length=100, blank=True)
    qualification = models.CharField(max_length=255, blank=True)
    experience_years = models.PositiveIntegerField(default=0)
    shift = models.CharField(max_length=50, blank=True)
    bio = models.TextField(blank=True)
    address = models.TextField(blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=20, blank=True)
    blood_group = models.CharField(max_length=5, blank=True)
    profile_image = models.ImageField(upload_to='nurse_profiles/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.registration_number}"    