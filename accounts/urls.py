from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('moh/dashboard/', views.moh_dashboard, name='moh_dashboard'),
    path('moh/notices/', views.moh_notices, name='moh_notices'),
    path('moh/hospital-approval/', views.hospital_approval, name='hospital_approval'),
    path('moh/facilities/', views.moh_facilities, name='moh_facilities'),
    path('moh/analytics/', views.moh_analytics, name='moh_analytics'),
    path('moh/configuration/', views.moh_configuration, name='moh_configuration'),
    path('moh/notifications/', views.moh_notifications, name='moh_notifications'),
    #hospital admin urls
    path('hospital-admin/', views.hospital_admin_dashboard, name='hospital_admin_dashboard'),
path('moh/notifications/', views.moh_notifications, name='moh_notifications'),
path('hospital-admin/', views.hospital_admin_dashboard, name='hospital_admin_dashboard'),
path('hospital-admin/notices/', views.hospital_admin_notices, name='hospital_admin_notices'),
path('hospital-admin/doctors/', views.hospital_doctors, name='hospital_doctors'),
path('hospital-admin/staff/', views.hospital_staff, name='hospital_staff'),
path('hospital-admin/profile/', views.hospital_profile, name='hospital_profile'),
path('hospital-admin/departments/', views.hospital_departments, name='hospital_departments'),
path('hospital-admin/patients/', views.hospital_patients, name='hospital_patients'),
path('hospital-admin/documents/', views.hospital_documents, name='hospital_documents'),
path('hospital-admin/payroll/', views.hospital_payroll, name='hospital_payroll'),
path('hospital-admin/pharmacy/', views.hospital_pharmacy, name='hospital_pharmacy'),
path('hospital-admin/blood-bank/', views.hospital_blood_bank, name='hospital_blood_bank'),
path('hospital-admin/diagnostics/', views.hospital_diagnostics, name='hospital_diagnostics'),
path('hospital-admin/users-access/', views.hospital_users_access, name='hospital_users_access'),
path('hospital-admin/facility/', views.hospital_facility, name='hospital_facility'),
path('hospital-admin/settings/', views.hospital_admin_settings, name='hospital_admin_settings'),
path('hospital-admin/contact-support/', views.hospital_contact_support, name='hospital_contact_support'),
path('hospital-admin/notifications/', views.hospital_notifications, name='hospital_notifications'),
#doctors
path('doctor/', views.doctor_dashboard, name='doctor_dashboard'),
path('doctor/patient-summary/', views.doctor_patient_summary, name='doctor_patient_summary'),
path('doctor/prescription/', views.doctor_prescription, name='doctor_prescription'),
path('doctor/referrals/', views.doctor_referrals, name='doctor_referrals'),
path('doctor/appointments/', views.doctor_appointments, name='doctor_appointments'),
path('doctor/admissions/', views.doctor_admissions, name='doctor_admissions'),
path('doctor/schedule/', views.doctor_schedule, name='doctor_schedule'),
path('doctor/profile/', views.doctor_profile, name='doctor_profile'),


]