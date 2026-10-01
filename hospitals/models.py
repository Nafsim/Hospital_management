from django.db import models


class Hospital(models.Model):
    FACILITY_TYPE = (
        ('hospital', 'Hospital'),
        ('clinic', 'Clinic'),
        ('lab', 'Lab'),
        ('specialty', 'Specialty'),
    )

    name = models.CharField(max_length=255)
    code = models.CharField(max_length=20, unique=True)
    address = models.TextField()
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    facility_type = models.CharField(max_length=20, choices=FACILITY_TYPE, default='hospital')
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    @property
    def doctors(self):
        from django.contrib.auth import get_user_model
        from django.db.models import Q
        User = get_user_model()
        return User.objects.filter(
            role='doctor'
        ).filter(
            Q(hospital=self) | Q(staff_profile__hospital=self)
        ).distinct()

    @property
    def doctor_count(self):
        return self.doctors.count()
