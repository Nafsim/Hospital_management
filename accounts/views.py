from django.shortcuts import render , redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib import messages
from .forms import LoginForm, HospitalCreationForm
from patients.models import Patient
from staff.models import Staff
from hospitals.models import Hospital
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
from .models import Notice 
from django.contrib.auth import get_user_model
from .forms import HospitalCreationForm
from hospitals.models import Hospital
from django.db.models import Q
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)

        if form.is_valid():
            user = form.get_user()
            login(request, user)

            if user.role == 'moh':
                return redirect('moh_dashboard')
            elif user.role == 'hospital_admin':
                return redirect('hospital_admin_dashboard')
            elif user.role == 'doctor':
                return redirect('doctor_dashboard')
            elif user.role == 'nurse':
                return redirect('nurse_dashboard')
            elif user.role == 'patient':
                return redirect('patient_dashboard')
            elif user.role == 'lab':
                return redirect('lab_dashboard')
            elif user.role == 'counter':
                return redirect('counter_dashboard')
            elif user.role == 'bloodbank':
                return redirect('bloodbank_dashboard')
            elif user.role == 'accountant':
                return redirect('accountant_dashboard')

            return redirect('login')

    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form})

#role based dashboard
def dashboard(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.user.role == 'moh':
        return redirect('moh_dashboard')

    elif request.user.role == 'hospital_admin':
        return redirect('hospital_admin_dashboard')

    elif request.user.role == 'doctor':
        return redirect('doctor_dashboard')

    elif request.user.role == 'nurse':
        return redirect('nurse_dashboard')

    elif request.user.role == 'patient':
        return redirect('patient_dashboard')

    elif request.user.role == 'lab':
        return redirect('lab_dashboard')

    elif request.user.role == 'counter':
        return redirect('counter_dashboard')

    elif request.user.role == 'bloodbank':
        return redirect('bloodbank_dashboard')

    elif request.user.role == 'accountant':
        return redirect('accountant_dashboard')

    return redirect('login')
#MOH 
User = get_user_model()

def moh_dashboard(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'moh':
        return redirect('dashboard')

    total_hospitals = Hospital.objects.filter(is_active=True).count()
    total_doctors = User.objects.filter(role='doctor', is_active=True).count()
    total_patients = Patient.objects.count()
    pending_hospitals = Hospital.objects.filter(is_active=False).count()

    today = timezone.now().date()
    active_users_today = User.objects.filter(last_login__date=today).count()
    hospitals_connected = total_hospitals
    total_visits = (
    Patient.objects.count() * 6 + 
    User.objects.filter(role='doctor', is_active=True).count() * 40 + 
    Hospital.objects.filter(is_active=True).count() * 180
)
    reports_today = 0

    chart_labels = []
    chart_data = []

    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        chart_labels.append(day.strftime('%d %b'))
        count = Hospital.objects.filter(created_at__date=day).count()
        chart_data.append(count)

    context = {
        'total_hospitals': total_hospitals,
        'total_doctors': total_doctors,
        'total_patients': total_patients,
        'pending_hospitals': pending_hospitals,
        'active_users_today': active_users_today,
        'hospitals_connected': hospitals_connected,
        'total_visits': total_visits,
        'reports_today': reports_today,
        'chart_labels': chart_labels,
        'chart_data': chart_data,
    }

    return render(request, 'accounts/moh/dashboard.html', context)
def moh_notices(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'moh':
        return redirect('dashboard')

    notices = Notice.objects.all().order_by('-created_at')
    context = {
        'notices': notices,
    }
    return render(request, 'accounts/moh/notices.html', context)


def moh_notice_create(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'moh':
        return redirect('dashboard')

    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        notice_type = request.POST.get('notice_type')
        priority = request.POST.get('priority')
        status = request.POST.get('status')

        Notice.objects.create(
            title=title,
            content=content,
            notice_type=notice_type,
            priority=priority,
            status=status,
            created_by=request.user
        )
        messages.success(request, 'Notice created successfully.')
        return redirect('moh_notices')

    return render(request, 'accounts/moh/notice_form.html', {
        'action': 'Create',
        'notice': None
    })


def moh_notice_edit(request, pk):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'moh':
        return redirect('dashboard')

    notice = get_object_or_404(Notice, pk=pk)

    if request.method == 'POST':
        notice.title = request.POST.get('title')
        notice.content = request.POST.get('content')
        notice.notice_type = request.POST.get('notice_type')
        notice.priority = request.POST.get('priority')
        notice.status = request.POST.get('status')
        notice.save()
        messages.success(request, 'Notice updated successfully.')
        return redirect('moh_notices')

    return render(request, 'accounts/moh/notice_form.html', {
        'action': 'Edit',
        'notice': notice
    })


def moh_notice_delete(request, pk):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'moh':
        return redirect('dashboard')

    notice = get_object_or_404(Notice, pk=pk)
    notice.delete()
    messages.success(request, 'Notice deleted successfully.')
    return redirect('moh_notices')


def moh_notice_view(request, pk):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'moh':
        return redirect('dashboard')

    notice = get_object_or_404(Notice, pk=pk)
    return render(request, 'accounts/moh/notice_detail.html', {
        'notice': notice
    })
#hospital approval
User = get_user_model()

def hospital_approval(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'moh':
        return redirect('dashboard')
    form = HospitalCreationForm()
    tab = request.GET.get('tab', 'all')  

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'create':
            form = HospitalCreationForm(request.POST)
            if form.is_valid():
                hospital = Hospital.objects.create(
                    name=form.cleaned_data['name'],
                    code=form.cleaned_data['code'],
                    address=form.cleaned_data['address'],
                    city=form.cleaned_data.get('city', ''),
                    facility_type=form.cleaned_data.get('facility_type', 'hospital'),
                    phone=form.cleaned_data.get('phone', ''),
                    email=form.cleaned_data.get('email', ''),
                    is_active=True
                )
                User.objects.create_user(
                    username=form.cleaned_data['admin_email'],
                    email=form.cleaned_data['admin_email'],
                    password=form.cleaned_data['admin_password'],
                    first_name=form.cleaned_data['admin_first_name'],
                    last_name=form.cleaned_data['admin_last_name'],
                    role='hospital_admin',
                    phone=form.cleaned_data.get('admin_phone', ''),
                    hospital=hospital,
                    is_active=True
                )
                messages.success(request, f'{hospital.get_facility_type_display()} "{hospital.name}" and admin created successfully.')
                return redirect('hospital_approval')
            else:
                messages.error(request, 'Please correct the errors below.')
        elif action == 'approve':
            hospital = get_object_or_404(Hospital, pk=request.POST.get('hospital_id'))
            hospital.is_active = True
            hospital.save()
            messages.success(request, f'{hospital.get_facility_type_display()} "{hospital.name}" approved successfully.')
            return redirect(f"{request.path}?tab=pending")
        elif action == 'reject':
            hospital = get_object_or_404(Hospital, pk=request.POST.get('hospital_id'))
            hospital.delete()
            messages.success(request, 'Hospital request rejected and removed.')
            return redirect(f"{request.path}?tab=pending")
        elif action == 'delete':
            hospital = get_object_or_404(Hospital, pk=request.POST.get('hospital_id'))
            hospital.delete()
            messages.success(request, 'Hospital deleted successfully.')
            return redirect('hospital_approval')
        elif action == 'edit':
            hospital = get_object_or_404(Hospital, pk=request.POST.get('hospital_id'))
            hospital.name = request.POST.get('name')
            hospital.code = request.POST.get('code')
            hospital.address = request.POST.get('address')
            hospital.city = request.POST.get('city', '')
            hospital.facility_type = request.POST.get('facility_type', hospital.facility_type or 'hospital')
            hospital.phone = request.POST.get('phone', '')
            hospital.email = request.POST.get('email', '')
            hospital.is_active = True if request.POST.get('is_active') else False
            hospital.save()
            messages.success(request, f'{hospital.get_facility_type_display()} "{hospital.name}" updated successfully.')
            return redirect('hospital_approval')
        else:
            form = HospitalCreationForm()

    if tab == 'pending':
        hospitals = Hospital.objects.filter(is_active=False).order_by('-created_at')
    else:
        hospitals = Hospital.objects.all().order_by('-created_at')

    context = {
        'form': form,
        'hospitals': hospitals,
        'tab': tab,
        'total_all': Hospital.objects.count(),
        'total_pending': Hospital.objects.filter(is_active=False).count(),
    }
    return render(request, 'accounts/moh/hospital_approval.html', context)
def moh_facilities(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'moh':
        return redirect('dashboard')

    search = request.GET.get('q', '').strip()

    facilities = Hospital.objects.all().order_by('-created_at')

    if search:
        facilities = facilities.filter(
            Q(name__icontains=search) |
            Q(code__icontains=search) |
            Q(city__icontains=search) |
            Q(address__icontains=search)
        )

    total_hospitals = Hospital.objects.filter(facility_type='hospital').count()
    total_clinics   = Hospital.objects.filter(facility_type='clinic').count()
    total_labs      = Hospital.objects.filter(facility_type='lab').count()
    total_specialty = Hospital.objects.filter(facility_type='specialty').count()

    context = {
        'facilities': facilities,
        'search': search,
        'total_hospitals': total_hospitals,
        'total_clinics': total_clinics,
        'total_labs': total_labs,
        'total_specialty': total_specialty,
    }
    return render(request, 'accounts/moh/facilities.html', context)

def moh_analytics(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'accounts/moh/analytics.html')

def moh_configuration(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'accounts/moh/configuration.html')

def moh_notifications(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'accounts/moh/notifications.html')
#hospital admin
def hospital_admin_dashboard(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'hospital_admin':
        return redirect('dashboard')
    hospital = request.user.hospital
    context = {
        'hospital': hospital,
        'patients_count': Patient.objects.filter(hospital=hospital).count() if hospital else 0,
        'staff_count': Staff.objects.filter(hospital=hospital).count() if hospital else 0,
    }
    return render(request, 'accounts/hospital_admin/dashboard.html', context)

def hospital_admin_notices(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'hospital_admin':
        return redirect('dashboard')
    return render(request, 'accounts/hospital_admin/notices.html')

def hospital_doctors(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'hospital_admin':
        return redirect('dashboard')
    hospital = request.user.hospital
    doctors = Staff.objects.filter(hospital=hospital, user__role='doctor') if hospital else []
    context = {'doctors': doctors}
    return render(request, 'accounts/hospital_admin/doctors.html', context)

def hospital_staff(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'hospital_admin':
        return redirect('dashboard')
    hospital = request.user.hospital
    staff = Staff.objects.filter(hospital=hospital) if hospital else []
    context = {'staff': staff}
    return render(request, 'accounts/hospital_admin/staff.html', context)

def hospital_profile(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'hospital_admin':
        return redirect('dashboard')
    hospital = request.user.hospital
    context = {'hospital': hospital}
    return render(request, 'accounts/hospital_admin/hospital_profile.html', context)

def hospital_departments(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'hospital_admin':
        return redirect('dashboard')
    return render(request, 'accounts/hospital_admin/departments.html')

def hospital_patients(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'hospital_admin':
        return redirect('dashboard')
    hospital = request.user.hospital
    patients = Patient.objects.filter(hospital=hospital) if hospital else []
    context = {'patients': patients}
    return render(request, 'accounts/hospital_admin/patients.html', context)

def hospital_documents(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'hospital_admin':
        return redirect('dashboard')
    return render(request, 'accounts/hospital_admin/documents.html')

def hospital_payroll(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'hospital_admin':
        return redirect('dashboard')
    hospital = request.user.hospital
    staff = Staff.objects.filter(hospital=hospital) if hospital else []
    context = {'staff': staff}
    return render(request, 'accounts/hospital_admin/payroll.html', context)

def hospital_pharmacy(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'hospital_admin':
        return redirect('dashboard')
    return render(request, 'accounts/hospital_admin/pharmacy.html')

def hospital_blood_bank(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'hospital_admin':
        return redirect('dashboard')
    return render(request, 'accounts/hospital_admin/blood_bank.html')

def hospital_diagnostics(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'hospital_admin':
        return redirect('dashboard')
    return render(request, 'accounts/hospital_admin/diagnostics.html')

def hospital_users_access(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'hospital_admin':
        return redirect('dashboard')
    hospital = request.user.hospital
    from django.contrib.auth import get_user_model
    User = get_user_model()
    users = User.objects.filter(hospital=hospital) if hospital else []
    context = {'users': users}
    return render(request, 'accounts/hospital_admin/users_access.html', context)

def hospital_facility(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'hospital_admin':
        return redirect('dashboard')
    return render(request, 'accounts/hospital_admin/facility.html')

def hospital_admin_settings(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'hospital_admin':
        return redirect('dashboard')
    return render(request, 'accounts/hospital_admin/settings.html')

def hospital_contact_support(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'hospital_admin':
        return redirect('dashboard')
    return render(request, 'accounts/hospital_admin/contact_support.html')

def hospital_notifications(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'hospital_admin':
        return redirect('dashboard')
    return render(request, 'accounts/hospital_admin/notifications.html')

#doctors
def doctor_dashboard(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'accounts/doctor/dashboard.html')

def doctor_patient_summary(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'accounts/doctor/patient_summary.html')

def doctor_prescription(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'accounts/doctor/prescription.html')

def doctor_referrals(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'accounts/doctor/referrals.html')

def doctor_appointments(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'accounts/doctor/appointments.html')

def doctor_admissions(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'accounts/doctor/admissions.html')

def doctor_schedule(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'accounts/doctor/schedule.html')

def doctor_profile(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'accounts/doctor/profile.html')

#Nourse
def nurse_dashboard(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'nurse':
        return redirect('dashboard')
    hospital = request.user.hospital
    context = {
        'hospital': hospital,
        'patients_count': Patient.objects.filter(hospital=hospital).count() if hospital else 0,
    }
    return render(request, 'accounts/nurse/dashboard.html', context)

def nurse_vital_signs(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'nurse':
        return redirect('dashboard')
    hospital = request.user.hospital
    patients = Patient.objects.filter(hospital=hospital) if hospital else []
    context = {'patients': patients}
    return render(request, 'accounts/nurse/vital_signs.html', context)

def nurse_notes(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'nurse':
        return redirect('dashboard')
    hospital = request.user.hospital
    patients = Patient.objects.filter(hospital=hospital) if hospital else []
    context = {'patients': patients}
    return render(request, 'accounts/nurse/nursing_notes.html', context)

def nurse_patients(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'nurse':
        return redirect('dashboard')
    hospital = request.user.hospital
    patients = Patient.objects.filter(hospital=hospital) if hospital else []
    context = {'patients': patients}
    return render(request, 'accounts/nurse/patients.html', context)

def nurse_notifications(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'nurse':
        return redirect('dashboard')
    return render(request, 'accounts/nurse/notifications.html')

def nurse_profile(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'nurse':
        return redirect('dashboard')
    return render(request, 'accounts/nurse/profile.html')
# Patient
def patient_dashboard(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'patient':
        return redirect('dashboard')
    return render(request, 'accounts/patient/dashboard.html')

def patient_notices(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'patient':
        return redirect('dashboard')
    return render(request, 'accounts/patient/notices.html')

def patient_departments(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'patient':
        return redirect('dashboard')
    return render(request, 'accounts/patient/departments.html')

def patient_doctors(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'patient':
        return redirect('dashboard')
    return render(request, 'accounts/patient/doctors.html')

def patient_appointments(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'patient':
        return redirect('dashboard')
    return render(request, 'accounts/patient/appointments.html')

def patient_medical_records(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'patient':
        return redirect('dashboard')
    return render(request, 'accounts/patient/medical_records.html')

def patient_payments(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'patient':
        return redirect('dashboard')
    return render(request, 'accounts/patient/payments.html')

def patient_emergency_contact(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'patient':
        return redirect('dashboard')
    return render(request, 'accounts/patient/emergency_contact.html')

def patient_profile(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'patient':
        return redirect('dashboard')
    return render(request, 'accounts/patient/profile.html')
# Diagnostic Center

def lab_dashboard(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'lab':
        return redirect('dashboard')
    hospital = request.user.hospital
    context = {
        'hospital': hospital,
        'patients_count': Patient.objects.filter(hospital=hospital).count() if hospital else 0,
    }
    return render(request, 'accounts/lab/dashboard.html', context)

def lab_upload_report(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'lab':
        return redirect('dashboard')
    hospital = request.user.hospital
    patients = Patient.objects.filter(hospital=hospital) if hospital else []
    context = {'patients': patients}
    return render(request, 'accounts/lab/upload_report.html', context)

def lab_report_status(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'lab':
        return redirect('dashboard')
    hospital = request.user.hospital
    patients = Patient.objects.filter(hospital=hospital) if hospital else []
    context = {'patients': patients}
    return render(request, 'accounts/lab/report_status.html', context)

def lab_report_preview(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'lab':
        return redirect('dashboard')
    hospital = request.user.hospital
    patients = Patient.objects.filter(hospital=hospital) if hospital else []
    context = {'patients': patients}
    return render(request, 'accounts/lab/report_preview.html', context)

def lab_history(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'lab':
        return redirect('dashboard')
    hospital = request.user.hospital
    patients = Patient.objects.filter(hospital=hospital) if hospital else []
    context = {'patients': patients}
    return render(request, 'accounts/lab/lab_history.html', context)

def lab_profile(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'lab':
        return redirect('dashboard')
    return render(request, 'accounts/lab/profile.html')
# Counter
def counter_dashboard(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'counter':
        return redirect('dashboard')
    hospital = request.user.hospital
    context = {
        'hospital': hospital,
        'patients_count': Patient.objects.filter(hospital=hospital).count() if hospital else 0,
    }
    return render(request, 'accounts/counter/dashboard.html', context)

def counter_patients(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'counter':
        return redirect('dashboard')
    hospital = request.user.hospital
    patients = Patient.objects.filter(hospital=hospital) if hospital else []
    context = {'patients': patients}
    return render(request, 'accounts/counter/patients.html', context)

def counter_appointments(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'counter':
        return redirect('dashboard')
    hospital = request.user.hospital
    patients = Patient.objects.filter(hospital=hospital) if hospital else []
    context = {'patients': patients}
    return render(request, 'accounts/counter/appointments.html', context)

def counter_doctors(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'counter':
        return redirect('dashboard')
    hospital = request.user.hospital
    doctors = Staff.objects.filter(hospital=hospital, user__role='doctor') if hospital else []
    context = {'doctors': doctors}
    return render(request, 'accounts/counter/doctors.html', context)

def counter_billing(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'counter':
        return redirect('dashboard')
    hospital = request.user.hospital
    patients = Patient.objects.filter(hospital=hospital) if hospital else []
    context = {'patients': patients}
    return render(request, 'accounts/counter/billing.html', context)

def counter_notices(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'counter':
        return redirect('dashboard')
    return render(request, 'accounts/counter/notices.html')

def counter_profile(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'counter':
        return redirect('dashboard')
    return render(request, 'accounts/counter/profile.html')
#blood bank
def bloodbank_dashboard(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'bloodbank':
        return redirect('dashboard')
    hospital = request.user.hospital
    context = {
        'hospital': hospital,
        'patients_count': Patient.objects.filter(hospital=hospital).count() if hospital else 0,
    }
    return render(request, 'accounts/bloodbank/dashboard.html', context)


def bloodbank_donors(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'bloodbank':
        return redirect('dashboard')
    hospital = request.user.hospital
    patients = Patient.objects.filter(hospital=hospital) if hospital else []
    context = {'patients': patients}
    return render(request, 'accounts/bloodbank/donors.html', context)


def bloodbank_inventory(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'bloodbank':
        return redirect('dashboard')
    hospital = request.user.hospital
    context = {'hospital': hospital}
    return render(request, 'accounts/bloodbank/inventory.html', context)


def bloodbank_requests(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'bloodbank':
        return redirect('dashboard')
    hospital = request.user.hospital
    patients = Patient.objects.filter(hospital=hospital) if hospital else []
    context = {'patients': patients}
    return render(request, 'accounts/bloodbank/requests.html', context)


def bloodbank_collection(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'bloodbank':
        return redirect('dashboard')
    hospital = request.user.hospital
    patients = Patient.objects.filter(hospital=hospital) if hospital else []
    context = {'patients': patients}
    return render(request, 'accounts/bloodbank/collection.html', context)


def bloodbank_testing(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'bloodbank':
        return redirect('dashboard')
    hospital = request.user.hospital
    patients = Patient.objects.filter(hospital=hospital) if hospital else []
    context = {'patients': patients}
    return render(request, 'accounts/bloodbank/testing.html', context)


def bloodbank_issue(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'bloodbank':
        return redirect('dashboard')
    hospital = request.user.hospital
    patients = Patient.objects.filter(hospital=hospital) if hospital else []
    context = {'patients': patients}
    return render(request, 'accounts/bloodbank/issue.html', context)


def bloodbank_notices(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'bloodbank':
        return redirect('dashboard')
    return render(request, 'accounts/bloodbank/notices.html')


def bloodbank_profile(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'bloodbank':
        return redirect('dashboard')
    return render(request, 'accounts/bloodbank/profile.html')


# accountant
def accountant_dashboard(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'accountant':
        return redirect('dashboard')
    hospital = request.user.hospital
    context = {
        'hospital': hospital,
        'patients_count': Patient.objects.filter(hospital=hospital).count() if hospital else 0,
        'staff_count': Staff.objects.filter(hospital=hospital).count() if hospital else 0,
    }
    return render(request, 'accounts/accountant/dashboard.html', context)
def accountant_billing(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'accountant':
        return redirect('dashboard')
    hospital = request.user.hospital
    patients = Patient.objects.filter(hospital=hospital) if hospital else []
    context = {'patients': patients}
    return render(request, 'accounts/accountant/billing.html', context)
def accountant_payments(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'accountant':
        return redirect('dashboard')
    hospital = request.user.hospital
    patients = Patient.objects.filter(hospital=hospital) if hospital else []
    context = {'patients': patients}
    return render(request, 'accounts/accountant/payments.html', context)
def accountant_invoices(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'accountant':
        return redirect('dashboard')
    hospital = request.user.hospital
    patients = Patient.objects.filter(hospital=hospital) if hospital else []
    context = {'patients': patients}
    return render(request, 'accounts/accountant/invoices.html', context)
def accountant_expenses(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'accountant':
        return redirect('dashboard')
    hospital = request.user.hospital
    context = {'hospital': hospital}
    return render(request, 'accounts/accountant/expenses.html', context)
def accountant_payroll(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'accountant':
        return redirect('dashboard')
    hospital = request.user.hospital
    staff = Staff.objects.filter(hospital=hospital) if hospital else []
    context = {'staff': staff}
    return render(request, 'accounts/accountant/payroll.html', context)
def accountant_accounts(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'accountant':
        return redirect('dashboard')
    hospital = request.user.hospital
    context = {'hospital': hospital}
    return render(request, 'accounts/accountant/accounts.html', context)
def accountant_reports(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'accountant':
        return redirect('dashboard')
    hospital = request.user.hospital
    context = {'hospital': hospital}
    return render(request, 'accounts/accountant/reports.html', context)
def accountant_notices(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'accountant':
        return redirect('dashboard')
    return render(request, 'accounts/accountant/notices.html')
def accountant_notifications(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'accountant':
        return redirect('dashboard')
    return render(request, 'accounts/accountant/notifications.html')
def accountant_profile(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'accountant':
        return redirect('dashboard')
    return render(request, 'accounts/accountant/profile.html')