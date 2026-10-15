from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, BloodTestRequest

class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'username', 'role', 'hospital', 'is_active')
    list_filter = ('role', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('Extra Info', {'fields': ('role', 'hospital', 'phone')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Extra Info', {'fields': ('role', 'hospital', 'phone', 'email')}),
    )

admin.site.register(User, CustomUserAdmin)

@admin.register(BloodTestRequest)
class BloodTestRequestAdmin(admin.ModelAdmin):
    list_display = ('request_id', 'patient_name', 'test_name', 'amount', 'payment_status', 'lab_status', 'hospital', 'created_at')
    list_filter = ('lab_status', 'payment_status', 'priority', 'hospital')
    search_fields = ('request_id', 'patient_name', 'patient_phone', 'test_name')
