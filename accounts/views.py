import json
from django.shortcuts import render , redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib import messages
from .forms import LoginForm, HospitalCreationForm
import calendar
from datetime import datetime, timedelta, date
from django.apps import apps
from patients.models import Patient, Visit
from staff.models import Staff
from .models import Medicine
from hospitals.models import Hospital
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
from .models import Notice 
from django.contrib.auth import get_user_model
from .forms import HospitalCreationForm
from hospitals.models import Hospital
from django.db.models import Count, Q
from .models import SystemSettings
from django.contrib.auth.hashers import make_password
from .models import Department
from .models import HospitalDocument, Payroll  
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4 
from django.db import models
from .models import Blood
from .models import DiagnosticTest 
from .models import Facility, MOHJoinRequest
from django.contrib import messages
from .models import VitalSign 
from .models import NursingNote 
from .models import NurseProfile 
from .models import PatientAppointment
from .models import User, Notice, Department, DoctorPatient, DoctorSchedule, DoctorPrescription, DoctorReferral
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
            elif user.role == 'pharmacy':
                return redirect('pharmacy_dashboard')

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

    elif request.user.role == 'pharmacy':
        return redirect('pharmacy_dashboard')

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
    total_visits = Visit.objects.count()
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

User = get_user_model()

def moh_analytics(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'moh':
        return redirect('dashboard')

    now = timezone.now()

    # Calculate exact last 6 months ranges and labels
    months = []
    month_ranges = []
    for i in range(5, -1, -1):
        year = now.year
        month = now.month - i
        while month <= 0:
            month += 12
            year -= 1
        _, last_day = calendar.monthrange(year, month)
        start_dt = timezone.make_aware(datetime(year, month, 1, 0, 0, 0))
        end_dt = timezone.make_aware(datetime(year, month, last_day, 23, 59, 59, 999999))
        months.append(start_dt.strftime('%b'))
        month_ranges.append((start_dt, end_dt))

    # Platform Usage datasets
    visits_data = []
    reports_data = []
    prescriptions_data = []

    # Disease Trends datasets
    respiratory = []
    diabetes = []
    cardiac = []
    dermatology = []

    # Dynamically check for any dedicated Report or Prescription models if defined in installed apps
    ReportModel = None
    PrescriptionModel = None
    for model in apps.get_models():
        name_lower = model.__name__.lower()
        if 'report' in name_lower and model._meta.app_label in ['laboratory', 'patients', 'accounts', 'hospitals']:
            ReportModel = model
        elif 'prescription' in name_lower and model._meta.app_label in ['patients', 'accounts', 'hospitals', 'counter']:
            PrescriptionModel = model

    for start_dt, end_dt in month_ranges:
        # Visits in this month
        month_visits = Visit.objects.filter(visit_date__gte=start_dt, visit_date__lte=end_dt)
        visits_count = month_visits.count()
        visits_data.append(visits_count)

        # Reports in this month
        if ReportModel:
            date_field = 'created_at' if hasattr(ReportModel, 'created_at') else 'date'
            filter_kwargs = {f'{date_field}__gte': start_dt, f'{date_field}__lte': end_dt}
            reports_count = ReportModel.objects.filter(**filter_kwargs).count()
        else:
            reports_count = month_visits.filter(
                Q(department__icontains='lab') |
                Q(department__icontains='radio') |
                Q(department__icontains='patho') |
                Q(purpose__icontains='report') |
                Q(purpose__icontains='test') |
                Q(purpose__icontains='investigation')
            ).count()
        reports_data.append(reports_count)

        # Prescriptions in this month
        if PrescriptionModel:
            date_field = 'created_at' if hasattr(PrescriptionModel, 'created_at') else 'date'
            filter_kwargs = {f'{date_field}__gte': start_dt, f'{date_field}__lte': end_dt}
            prescriptions_count = PrescriptionModel.objects.filter(**filter_kwargs).count()
        else:
            prescriptions_count = month_visits.filter(
                Q(doctor__isnull=False) |
                Q(department__icontains='pharm') |
                Q(purpose__icontains='presc') |
                Q(purpose__icontains='medic')
            ).count()
        prescriptions_data.append(prescriptions_count)

        # Patients registered in this month
        month_patients = Patient.objects.filter(created_at__gte=start_dt, created_at__lte=end_dt)

        # Respiratory cases
        resp_visits = month_visits.filter(
            Q(department__icontains='respiratory') |
            Q(department__icontains='pulmon') |
            Q(department__icontains='ent') |
            Q(purpose__icontains='respiratory') |
            Q(purpose__icontains='asthma') |
            Q(purpose__icontains='cough') |
            Q(purpose__icontains='lung') |
            Q(purpose__icontains='cold') |
            Q(purpose__icontains='flu') |
            Q(purpose__icontains='pneumonia') |
            Q(purpose__icontains='bronchitis')
        ).count()
        resp_patients = month_patients.filter(
            Q(medical_history__icontains='respiratory') |
            Q(medical_history__icontains='asthma') |
            Q(medical_history__icontains='pneumonia') |
            Q(medical_history__icontains='bronchitis') |
            Q(allergies__icontains='respiratory')
        ).count()
        respiratory.append(resp_visits + resp_patients)

        # Diabetes cases
        diab_visits = month_visits.filter(
            Q(department__icontains='diabet') |
            Q(department__icontains='endocrin') |
            Q(purpose__icontains='diabet') |
            Q(purpose__icontains='sugar') |
            Q(purpose__icontains='glucose') |
            Q(purpose__icontains='insulin')
        ).count()
        diab_patients = month_patients.filter(
            Q(medical_history__icontains='diabet') |
            Q(medical_history__icontains='sugar') |
            Q(medical_history__icontains='glucose')
        ).count()
        diabetes.append(diab_visits + diab_patients)

        # Cardiac cases
        card_visits = month_visits.filter(
            Q(department__icontains='cardio') |
            Q(department__icontains='cardiac') |
            Q(department__icontains='ccu') |
            Q(purpose__icontains='cardiac') |
            Q(purpose__icontains='heart') |
            Q(purpose__icontains='hypertension') |
            Q(purpose__icontains='bp') |
            Q(purpose__icontains='chest pain')
        ).count()
        card_patients = month_patients.filter(
            Q(medical_history__icontains='cardio') |
            Q(medical_history__icontains='cardiac') |
            Q(medical_history__icontains='heart') |
            Q(medical_history__icontains='hypertension')
        ).count()
        cardiac.append(card_visits + card_patients)

        # Dermatology cases
        derm_visits = month_visits.filter(
            Q(department__icontains='derm') |
            Q(purpose__icontains='derm') |
            Q(purpose__icontains='skin') |
            Q(purpose__icontains='rash') |
            Q(purpose__icontains='eczema') |
            Q(purpose__icontains='acne')
        ).count()
        derm_patients = month_patients.filter(
            Q(medical_history__icontains='derm') |
            Q(medical_history__icontains='skin') |
            Q(medical_history__icontains='eczema') |
            Q(allergies__icontains='skin')
        ).count()
        dermatology.append(derm_visits + derm_patients)

    context = {
        'months': json.dumps(months),
        'visits_data': json.dumps(visits_data),
        'reports_data': json.dumps(reports_data),
        'prescriptions_data': json.dumps(prescriptions_data),
        'respiratory': json.dumps(respiratory),
        'diabetes': json.dumps(diabetes),
        'cardiac': json.dumps(cardiac),
        'dermatology': json.dumps(dermatology),
    }
    return render(request, 'accounts/moh/analytics.html', context)

def moh_configuration(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'moh':
        return redirect('dashboard')

    settings = SystemSettings.load()

    if request.method == 'POST':
        settings.company_name = request.POST.get('company_name', settings.company_name)
        settings.company_email = request.POST.get('company_email', settings.company_email)
        settings.phone = request.POST.get('phone', settings.phone)
        settings.address = request.POST.get('address', settings.address)
        settings.timezone = request.POST.get('timezone', settings.timezone)
        settings.currency = request.POST.get('currency', settings.currency)
        settings.date_format = request.POST.get('date_format', settings.date_format)
        settings.maintenance_mode = True if request.POST.get('maintenance_mode') == 'on' else False
        settings.save()
        messages.success(request, 'Settings saved successfully.')
        return redirect('moh_configuration')

    context = {
        'settings': settings,
    }
    return render(request, 'accounts/moh/configuration.html', context)


#hospital admin
User = get_user_model()

def hospital_admin_dashboard(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'hospital_admin':
        return redirect('dashboard')

    hospital = request.user.hospital

    # Dynamic counts
    total_doctors = 0
    total_nurses = 0
    total_patients = 0
    total_departments = 0
    total_staff = 0
    pending_requests = 0

    if hospital:
        total_doctors = Staff.objects.filter(hospital=hospital, user__role='doctor', user__is_active=True).count()
        total_nurses = Staff.objects.filter(hospital=hospital, user__role='nurse', user__is_active=True).count()
        total_patients = Patient.objects.filter(hospital=hospital).count()
        total_staff = Staff.objects.filter(hospital=hospital).count()
        
        total_departments = 0

    context = {
        'hospital': hospital,
        'total_doctors': total_doctors,
        'total_nurses': total_nurses,
        'total_patients': total_patients,
        'total_departments': total_departments,
        'total_staff': total_staff,
        'pending_requests': pending_requests,
    }
    return render(request, 'accounts/hospital_admin/dashboard.html', context)

from django.db.models import Q

def hospital_admin_notices(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'hospital_admin':
        return redirect('dashboard')

    hospital = request.user.hospital
    if not hospital:
        messages.error(request, 'No hospital linked to your account.')
        return redirect('hospital_admin_dashboard')

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'create':
            Notice.objects.create(
                title=request.POST.get('title'),
                content=request.POST.get('content'),
                notice_type=request.POST.get('notice_type', 'general'),
                priority=request.POST.get('priority', 'medium'),
                status=request.POST.get('status', 'published'),
                created_by=request.user,
                hospital=hospital
            )
            messages.success(request, 'Notice created successfully.')
            return redirect('hospital_admin_notices')

        elif action == 'edit':
            notice = get_object_or_404(Notice, pk=request.POST.get('notice_id'), hospital=hospital)
            notice.title = request.POST.get('title')
            notice.content = request.POST.get('content')
            notice.notice_type = request.POST.get('notice_type')
            notice.priority = request.POST.get('priority')
            notice.status = request.POST.get('status')
            notice.save()
            messages.success(request, 'Notice updated successfully.')
            return redirect('hospital_admin_notices')

        elif action == 'delete':
            notice = get_object_or_404(Notice, pk=request.POST.get('notice_id'), hospital=hospital)
            notice.delete()
            messages.success(request, 'Notice deleted successfully.')
            return redirect('hospital_admin_notices')

    # Hospital Admin sees: own hospital notices + MOH notices (hospital=null)
    notices = Notice.objects.filter(
        Q(hospital=hospital) | Q(hospital__isnull=True)
    ).order_by('-created_at')

    context = {
        'notices': notices,
        'hospital': hospital,
    }
    return render(request, 'accounts/hospital_admin/notices.html', context)
User = get_user_model()

def hospital_doctors(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'hospital_admin':
        return redirect('dashboard')

    hospital = request.user.hospital
    if not hospital:
        messages.error(request, 'No hospital linked to your account.')
        return redirect('hospital_admin_dashboard')

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'create':
            email = request.POST.get('email')
            if User.objects.filter(email=email).exists():
                messages.error(request, 'A user with this email already exists.')
                return redirect('hospital_doctors')

            department = request.POST.get('department', 'general')
            department_name = dict(Staff.DEPARTMENT_CHOICES).get(department, 'General Medicine')

            user = User.objects.create_user(
                username=email,
                email=email,
                password=request.POST.get('password'),
                first_name=request.POST.get('first_name'),
                last_name=request.POST.get('last_name'),
                role='doctor',
                phone=request.POST.get('phone', ''),
                hospital=hospital,
                is_active=True
            )

            Staff.objects.create(
                user=user,
                hospital=hospital,
                employee_id=request.POST.get('employee_id'),
                license=request.POST.get('license'),
                department=department,
                designation=request.POST.get('designation', 'Doctor'),
                date_of_joining=request.POST.get('date_of_joining') or timezone.now().date(),
                specialization=department_name,
                qualification=request.POST.get('qualification', ''),
                is_active=True
            )

            messages.success(request, 'Doctor added successfully.')
            return redirect('hospital_doctors')

        elif action == 'edit':
            staff = get_object_or_404(Staff, pk=request.POST.get('staff_id'), hospital=hospital)
            user = staff.user

            user.first_name = request.POST.get('first_name')
            user.last_name = request.POST.get('last_name')
            user.phone = request.POST.get('phone', '')
            user.is_active = True if request.POST.get('is_active') == 'on' else False
            user.save()

            department = request.POST.get('department')
            department_name = dict(Staff.DEPARTMENT_CHOICES).get(department, 'General Medicine')

            staff.employee_id = request.POST.get('employee_id')
            staff.license = request.POST.get('license')
            staff.department = department
            staff.designation = request.POST.get('designation')
            staff.specialization = department_name
            staff.qualification = request.POST.get('qualification', '')
            staff.is_active = user.is_active

            if request.POST.get('date_of_joining'):
                staff.date_of_joining = request.POST.get('date_of_joining')

            staff.save()

            messages.success(request, 'Doctor updated successfully.')
            return redirect('hospital_doctors')

        elif action == 'delete':
            staff = get_object_or_404(Staff, pk=request.POST.get('staff_id'), hospital=hospital)
            user = staff.user
            staff.delete()
            user.delete()
            messages.success(request, 'Doctor deleted successfully.')
            return redirect('hospital_doctors')

    doctors = Staff.objects.filter(
        hospital=hospital,
        user__role='doctor'
    ).select_related('user')

    context = {
        'doctors': doctors,
        'hospital': hospital,
        'departments': Staff.DEPARTMENT_CHOICES,
    }

    return render(request, 'accounts/hospital_admin/doctors.html', context)
User = get_user_model()

def hospital_staff(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'hospital_admin':
        return redirect('dashboard')

    hospital = request.user.hospital
    staff_filter = request.GET.get('staff_filter', 'all')
    search = request.GET.get('search', '').strip()

    if request.method == 'POST':
        action = request.POST.get('action')
        staff_id = request.POST.get('staff_id')

        if action == 'create':
            first_name = request.POST.get('first_name', '').strip()
            last_name = request.POST.get('last_name', '').strip()
            email = request.POST.get('email', '').strip()
            phone = request.POST.get('phone', '').strip()
            password = request.POST.get('password', '').strip()
            employee_id = request.POST.get('employee_id', '').strip()
            department = request.POST.get('department', '').strip()
            designation = request.POST.get('designation', '').strip()
            city = request.POST.get('city', '').strip()
            national_id = request.POST.get('national_id', '').strip()
            date_of_joining = request.POST.get('date_of_joining') or None
            qualification = request.POST.get('qualification', '').strip()
            is_active = request.POST.get('is_active') == 'on'

            role_map = {
                'Nurse': 'nurse',
                'Accountant': 'accountant',
                'Laboratory': 'lab',
                'Counter / Reception': 'counter',
                'Blood Bank': 'bloodbank',
                'Pharmacy': 'pharmacy',          # ← added
            }
            role = role_map.get(department, 'nurse')

            if User.objects.filter(email=email).exists():
                return redirect('hospital_staff')

            user = User.objects.create(
                email=email,
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                password=make_password(password),
                role=role,
                hospital=hospital,
                is_active=is_active
            )

            Staff.objects.create(
                user=user,
                hospital=hospital,
                employee_id=employee_id,
                department=department,
                designation=designation,
                date_of_joining=date_of_joining,
                qualification=qualification,
                city=city,
                national_id=national_id,
                is_active=is_active
            )
            return redirect('hospital_staff')

        if action == 'delete' and staff_id:
            staff_member = Staff.objects.get(id=staff_id, hospital=hospital)
            user = staff_member.user
            staff_member.delete()
            if user:
                user.delete()
            return redirect('hospital_staff')

    # Base queryset
    staff = Staff.objects.filter(hospital=hospital).select_related('user')

    # Search functionality
    if search:
        staff = staff.filter(
            models.Q(user__first_name__icontains=search) |
            models.Q(user__last_name__icontains=search) |
            models.Q(user__email__icontains=search) |
            models.Q(employee_id__icontains=search) |
            models.Q(department__icontains=search)
        )

    # Filtering
    if staff_filter == 'doctor':
        staff = staff.filter(user__role='doctor')
    elif staff_filter == 'nurse':
        staff = staff.filter(user__role='nurse')
    elif staff_filter == 'accountant':
        staff = staff.filter(user__role='accountant')
    elif staff_filter == 'laboratory':
        staff = staff.filter(user__role='lab')
    elif staff_filter == 'counter':
        staff = staff.filter(user__role='counter')
    elif staff_filter == 'blood':
        staff = staff.filter(user__role='bloodbank')
    elif staff_filter == 'pharmacy':
        staff = staff.filter(user__role='pharmacy')         
    elif staff_filter == 'medical':
        staff = staff.filter(department='Medical Records')
    elif staff_filter == 'administration':
        staff = staff.filter(department='HR / Administration')
    # else: staff_filter == 'all' → show everything

    context = {
        'staff': staff,
        'staff_filter': staff_filter,
        'hospital': hospital,
        'search': search
    }
    return render(request, 'accounts/hospital_admin/staff.html', context)
def hospital_profile(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'hospital_admin':
        return redirect('dashboard')

    hospital = request.user.hospital
    if not hospital:
        messages.error(request, 'No hospital linked to your account.')
        return redirect('hospital_admin_dashboard')

    if request.method == 'POST':
        hospital.name = request.POST.get('name', hospital.name)
        hospital.code = request.POST.get('code', hospital.code)
        hospital.address = request.POST.get('address', hospital.address)
        hospital.city = request.POST.get('city', hospital.city)
        hospital.phone = request.POST.get('phone', hospital.phone)
        hospital.email = request.POST.get('email', hospital.email)
        hospital.facility_type = request.POST.get('facility_type', hospital.facility_type)
        hospital.save()

        # Password change
        new_password = request.POST.get('new_password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()

        if new_password:
            if new_password == confirm_password:
                request.user.set_password(new_password)
                request.user.save()
                messages.success(request, 'Hospital profile and password updated successfully. Please login again.')
                return redirect('login')
            else:
                messages.error(request, 'Passwords do not match.')
                return redirect('hospital_profile')

        messages.success(request, 'Hospital profile updated successfully.')
        return redirect('hospital_profile')

    context = {
        'hospital': hospital,
    }
    return render(request, 'accounts/hospital_admin/hospital_profile.html', context)

def hospital_departments(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.user.role != 'hospital_admin':
        return redirect('dashboard')

    hospital = request.user.hospital

    departments = Department.objects.filter(hospital=hospital)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'create':
            name = request.POST.get('name')
            is_active = request.POST.get('is_active') == 'on'

            if name:
                Department.objects.create(
                    hospital=hospital,
                    name=name,
                    is_active=is_active
                )

            return redirect('hospital_departments')

        if action == 'edit':
            department_id = request.POST.get('department_id')
            name = request.POST.get('name')
            is_active = request.POST.get('is_active') == 'on'

            department = Department.objects.get(
                id=department_id,
                hospital=hospital
            )

            department.name = name
            department.is_active = is_active
            department.save()

            return redirect('hospital_departments')

        if action == 'delete':
            department_id = request.POST.get('department_id')

            Department.objects.filter(
                id=department_id,
                hospital=hospital
            ).delete()

            return redirect('hospital_departments')

    context = {
        'hospital': hospital,
        'departments': departments,
        'total_departments': departments.count(),
        'active_departments': departments.filter(is_active=True).count(),
        'inactive_departments': departments.filter(is_active=False).count(),
        'department_choices': Department.DEPARTMENT_CHOICES,
    }

    return render(
        request,
        'accounts/hospital_admin/departments.html',
        context
    )
def hospital_patients(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.user.role != 'hospital_admin':
        return redirect('dashboard')

    hospital = request.user.hospital

    patients = Patient.objects.filter(hospital=hospital) if hospital else Patient.objects.none()

    context = {
        'patients': patients,
        'total_patients': patients.count(),
        'today_appointments': 0,
        'pending_appointments': 0,
    }

    return render(
        request,
        'accounts/hospital_admin/patients.html',
        context
    )
def hospital_documents(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.user.role != 'hospital_admin':
        return redirect('dashboard')

    hospital = request.user.hospital

    documents = HospitalDocument.objects.filter(
        hospital=hospital
    ) if hospital else HospitalDocument.objects.none()

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'upload':
            files = request.FILES.getlist('files')

            for uploaded_file in files[:20]:
                allowed_types = [
                    'application/pdf',
                    'image/jpeg',
                    'image/png'
                ]

                if uploaded_file.content_type not in allowed_types:
                    continue

                if uploaded_file.size > 10 * 1024 * 1024:
                    continue

                HospitalDocument.objects.create(
                    hospital=hospital,
                    name=uploaded_file.name,
                    file=uploaded_file,
                    uploaded_by=request.user
                )

            return redirect('hospital_documents')

        if action == 'delete':
            document_id = request.POST.get('document_id')

            HospitalDocument.objects.filter(
                id=document_id,
                hospital=hospital
            ).delete()

            return redirect('hospital_documents')

    context = {
        'documents': documents,
        'total_documents': documents.count(),
        'pdf_documents': documents.filter(
            file__iendswith='.pdf'
        ).count(),
        'image_documents': documents.filter(
            file__iendswith='.jpg'
        ).count() + documents.filter(
            file__iendswith='.jpeg'
        ).count() + documents.filter(
            file__iendswith='.png'
        ).count(),
    }

    return render(
        request,
        'accounts/hospital_admin/documents.html',
        context
    )

def hospital_payroll(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.user.role != 'hospital_admin':
        return redirect('dashboard')

    hospital = request.user.hospital

    staff = Staff.objects.filter(
        hospital=hospital
    ) if hospital else Staff.objects.none()

    payroll = Payroll.objects.filter(
        hospital=hospital
    ) if hospital else Payroll.objects.none()

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'create':
            staff_id = request.POST.get('staff_id')
            salary_month = request.POST.get('salary_month')
            amount = request.POST.get('amount')
            status = request.POST.get('status', 'pending')

            if staff_id and salary_month and amount:
                selected_staff = Staff.objects.get(
                    id=staff_id,
                    hospital=hospital
                )

                Payroll.objects.create(
                    hospital=hospital,
                    staff=selected_staff,
                    salary_month=salary_month,
                    amount=amount,
                    status=status
                )

            return redirect('hospital_payroll')

        if action == 'edit':
            payroll_id = request.POST.get('payroll_id')
            staff_id = request.POST.get('staff_id')
            salary_month = request.POST.get('salary_month')
            amount = request.POST.get('amount')
            status = request.POST.get('status', 'pending')

            record = Payroll.objects.get(
                id=payroll_id,
                hospital=hospital
            )

            record.staff = Staff.objects.get(
                id=staff_id,
                hospital=hospital
            )
            record.salary_month = salary_month
            record.amount = amount
            record.status = status
            record.save()

            return redirect('hospital_payroll')

        if action == 'delete':
            payroll_id = request.POST.get('payroll_id')

            Payroll.objects.filter(
                id=payroll_id,
                hospital=hospital
            ).delete()

            return redirect('hospital_payroll')

    total_staff = staff.count()
    total_payroll = sum(record.amount for record in payroll)
    pending_payroll = sum(
        record.amount
        for record in payroll
        if record.status == 'pending'
    )

    def format_salary_amount(amount):
        if amount >= 100000:
            return f'{amount / 100000:.1f}L'
        if amount >= 1000:
            return f'{amount / 1000:.0f}k'
        return str(amount)

    context = {
        'hospital': hospital,
        'staff': staff,
        'payroll': payroll,
        'total_staff': total_staff,
        'total_payroll': total_payroll,
        'pending_payroll': pending_payroll,
        'total_payroll_display': format_salary_amount(total_payroll),
        'pending_payroll_display': format_salary_amount(pending_payroll),
    }

    return render(
        request,
        'accounts/hospital_admin/payroll.html',
        context
    )

def export_payroll(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.user.role != 'hospital_admin':
        return redirect('dashboard')

    hospital = request.user.hospital

    department = request.GET.get('department', 'all')
    payroll = Payroll.objects.filter(hospital=hospital).order_by('-salary_month')

    if department != 'all':
        payroll = payroll.filter(staff__department=department)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="payroll_export.pdf"'

    pdf = canvas.Canvas(response, pagesize=A4)
    page_width, page_height = A4
    left_margin = 36
    row_height = 22
    y = page_height - 48

    pdf.setFont('Helvetica-Bold', 16)
    pdf.drawString(left_margin, y, 'Payroll Salary History')
    y -= 24
    pdf.setFont('Helvetica', 9)
    pdf.drawString(left_margin, y, f'Hospital: {hospital}')
    y -= 24

    headers = ['Staff Name', 'Staff ID', 'Department', 'Salary Date', 'Amount', 'Status']
    column_x = [36, 180, 230, 340, 435, 490]

    def draw_headers():
        pdf.setFillColorRGB(0.90, 0.93, 0.97)
        pdf.rect(left_margin, y - 6, page_width - 72, row_height, fill=1, stroke=0)
        pdf.setFillColorRGB(0, 0, 0)
        pdf.setFont('Helvetica-Bold', 8)
        for x, header in zip(column_x, headers):
            pdf.drawString(x, y, header)

    draw_headers()
    y -= row_height
    pdf.setFont('Helvetica', 8)
    for record in payroll:
        amount = record.amount
        if amount >= 100000:
            formatted_amount = f"{amount/100000:.1f}L"
        elif amount >= 1000:
            formatted_amount = f"{amount/1000:.0f}k"
        else:
            formatted_amount = str(amount)

        if y < 48:
            pdf.showPage()
            y = page_height - 48
            draw_headers()
            y -= row_height
            pdf.setFont('Helvetica', 8)

        values = [
            str(record.staff),
            str(record.staff.id),
            record.staff.department if record.staff.department else 'N/A',
            record.salary_month.strftime('%d %B %Y'),
            formatted_amount,
            record.status,
        ]
        for x, value in zip(column_x, values):
            pdf.drawString(x, y, value[:24])
        pdf.setStrokeColorRGB(0.88, 0.90, 0.93)
        pdf.line(left_margin, y - 7, page_width - 36, y - 7)
        y -= row_height

    pdf.save()
    return response

def download_payslip(request, payroll_id):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.user.role != 'hospital_admin':
        return redirect('dashboard')

    hospital = request.user.hospital

    record = Payroll.objects.get(
        id=payroll_id,
        hospital=hospital
    )

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Payslip_{record.staff.id}_{record.salary_month}.pdf"'

    pdf = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(70, height - 80, "NHIMS")

    pdf.setFont("Helvetica", 10)
    pdf.drawString(70, height - 100, "National Health Information Management System")

    pdf.setFont("Helvetica-Bold", 15)
    pdf.drawString(70, height - 145, "STAFF PAYSLIP")

    pdf.line(70, height - 155, width - 70, height - 155)

    y = height - 195

    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(70, y, "Staff Name:")
    pdf.setFont("Helvetica", 10)
    pdf.drawString(170, y, str(record.staff))

    y -= 30
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(70, y, "Staff ID:")
    pdf.setFont("Helvetica", 10)
    pdf.drawString(170, y, str(record.staff.id))

    y -= 30
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(70, y, "Department:")
    pdf.setFont("Helvetica", 10)
    pdf.drawString(170, y, str(record.staff.department or "N/A"))

    y -= 30
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(70, y, "Salary Date:")
    pdf.setFont("Helvetica", 10)
    pdf.drawString(170, y, record.salary_month.strftime("%d %B %Y"))

    y -= 30
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(70, y, "Salary Amount:")
    pdf.setFont("Helvetica", 10)
    pdf.drawString(170, y, f"BDT {record.amount}")

    y -= 30
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(70, y, "Payment Status:")
    pdf.setFont("Helvetica", 10)
    pdf.drawString(170, y, record.get_status_display())

    pdf.line(70, y - 30, width - 70, y - 30)

    pdf.setFont("Helvetica", 9)
    pdf.drawString(70, y - 55, "Generated by Hospital Admin")

    pdf.save()

    return response

def hospital_pharmacy(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.user.role != 'hospital_admin':
        return redirect('dashboard')

    hospital = request.user.hospital

    if request.method == 'POST':
        action = request.POST.get('action')
        medicine_id = request.POST.get('medicine_id')

        if action == 'create':
            Medicine.objects.create(
                hospital=hospital,
                name=request.POST.get('name', '').strip(),
                category=request.POST.get('category', ''),
                strength=request.POST.get('strength', '').strip(),
                stock=int(request.POST.get('stock') or 0),
                unit=request.POST.get('unit', ''),
                reorder_level=int(request.POST.get('reorder_level') or 20),
                expiry_date=request.POST.get('expiry_date') or None,
                batch_number=request.POST.get('batch_number', '').strip(),
                supplier=request.POST.get('supplier', '').strip(),
                price=request.POST.get('price') or 0
            )
            return redirect('hospital_pharmacy')

        if action == 'edit' and medicine_id:
            medicine = Medicine.objects.get(
                id=medicine_id,
                hospital=hospital
            )

            medicine.name = request.POST.get('name', '').strip()
            medicine.category = request.POST.get('category', '')
            medicine.strength = request.POST.get('strength', '').strip()
            medicine.stock = int(request.POST.get('stock') or 0)
            medicine.unit = request.POST.get('unit', '')
            medicine.reorder_level = int(request.POST.get('reorder_level') or 20)
            medicine.expiry_date = request.POST.get('expiry_date') or None
            medicine.batch_number = request.POST.get('batch_number', '').strip()
            medicine.supplier = request.POST.get('supplier', '').strip()
            medicine.price = request.POST.get('price') or 0
            medicine.save()

            return redirect('hospital_pharmacy')

        if action == 'delete' and medicine_id:
            Medicine.objects.filter(
                id=medicine_id,
                hospital=hospital
            ).delete()

            return redirect('hospital_pharmacy')

    medicines = Medicine.objects.filter(
        hospital=hospital
    )

    total_medicines = medicines.count()
    total_stock = sum(m.stock for m in medicines)
    low_stock = medicines.filter(
        stock__gt=0,
        stock__lte=models.F('reorder_level')
    ).count()
    out_of_stock = medicines.filter(stock=0).count()

    today = date.today()
    expiry_limit = today + timedelta(days=30)

    expiring_soon = medicines.filter(
        expiry_date__isnull=False,
        expiry_date__gte=today,
        expiry_date__lte=expiry_limit
    ).count()

    context = {
        'hospital': hospital,
        'medicines': medicines,
        'total_medicines': total_medicines,
        'total_stock': total_stock,
        'low_stock': low_stock,
        'out_of_stock': out_of_stock,
        'expiring_soon': expiring_soon,
        'category_choices': Medicine.CATEGORY_CHOICES,
        'unit_choices': Medicine.UNIT_CHOICES
    }

    return render(
        request,
        'accounts/hospital_admin/pharmacy.html',
        context
    )

def hospital_blood_bank(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.user.role != 'hospital_admin':
        return redirect('dashboard')

    hospital = request.user.hospital

    if request.method == 'POST':
        action = request.POST.get('action')
        blood_id = request.POST.get('blood_id')

        if action == 'create':
            Blood.objects.create(
                hospital=hospital,
                blood_group=request.POST.get('blood_group', ''),
                component=request.POST.get('component', 'whole'),
                units=int(request.POST.get('units') or 0),
                reorder_level=int(request.POST.get('reorder_level') or 5),
                expiry_date=request.POST.get('expiry_date') or None,
                bag_number=request.POST.get('bag_number', '').strip(),
                donor_name=request.POST.get('donor_name', '').strip(),
                collection_date=request.POST.get('collection_date') or None,
                notes=request.POST.get('notes', '').strip()
            )
            return redirect('hospital_blood_bank')

        if action == 'edit' and blood_id:
            blood = Blood.objects.get(id=blood_id, hospital=hospital)
            blood.blood_group = request.POST.get('blood_group', '')
            blood.component = request.POST.get('component', 'whole')
            blood.units = int(request.POST.get('units') or 0)
            blood.reorder_level = int(request.POST.get('reorder_level') or 5)
            blood.expiry_date = request.POST.get('expiry_date') or None
            blood.bag_number = request.POST.get('bag_number', '').strip()
            blood.donor_name = request.POST.get('donor_name', '').strip()
            blood.collection_date = request.POST.get('collection_date') or None
            blood.notes = request.POST.get('notes', '').strip()
            blood.save()
            return redirect('hospital_blood_bank')

        if action == 'delete' and blood_id:
            Blood.objects.filter(id=blood_id, hospital=hospital).delete()
            return redirect('hospital_blood_bank')

    blood_units = Blood.objects.filter(hospital=hospital)

    total_units = blood_units.count()
    total_stock = sum(b.units for b in blood_units)
    low_stock = blood_units.filter(units__gt=0, units__lte=models.F('reorder_level')).count()
    out_of_stock = blood_units.filter(units=0).count()

    today = date.today()
    expiry_limit = today + timedelta(days=14)

    expiring_soon = blood_units.filter(
        expiry_date__isnull=False,
        expiry_date__gte=today,
        expiry_date__lte=expiry_limit
    ).count()

    context = {
        'hospital': hospital,
        'blood_units': blood_units,
        'total_units': total_units,
        'total_stock': total_stock,
        'low_stock': low_stock,
        'out_of_stock': out_of_stock,
        'expiring_soon': expiring_soon,
        'blood_group_choices': Blood.BLOOD_GROUP_CHOICES,
        'component_choices': Blood.COMPONENT_CHOICES,
    }

    return render(request, 'accounts/hospital_admin/blood_bank.html', context)
def hospital_diagnostics(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.user.role != 'hospital_admin':
        return redirect('dashboard')

    hospital = request.user.hospital

    if request.method == 'POST':
        action = request.POST.get('action')
        test_id = request.POST.get('test_id')

        if action == 'create':
            DiagnosticTest.objects.create(
                hospital=hospital,
                name=request.POST.get('name', '').strip(),
                category=request.POST.get('category', 'blood'),
                sample_type=request.POST.get('sample_type', 'blood'),
                price=request.POST.get('price') or 0,
                report_time=request.POST.get('report_time', '').strip(),
                description=request.POST.get('description', '').strip(),
                is_active=request.POST.get('is_active') == 'on'
            )
            return redirect('hospital_diagnostics')

        if action == 'edit' and test_id:
            test = DiagnosticTest.objects.get(id=test_id, hospital=hospital)
            test.name = request.POST.get('name', '').strip()
            test.category = request.POST.get('category', 'blood')
            test.sample_type = request.POST.get('sample_type', 'blood')
            test.price = request.POST.get('price') or 0
            test.report_time = request.POST.get('report_time', '').strip()
            test.description = request.POST.get('description', '').strip()
            test.is_active = request.POST.get('is_active') == 'on'
            test.save()
            return redirect('hospital_diagnostics')

        if action == 'delete' and test_id:
            DiagnosticTest.objects.filter(id=test_id, hospital=hospital).delete()
            return redirect('hospital_diagnostics')

    tests = DiagnosticTest.objects.filter(hospital=hospital)

    total_tests = tests.count()
    active_tests = tests.filter(is_active=True).count()
    inactive_tests = tests.filter(is_active=False).count()
    categories_count = tests.values('category').distinct().count()

    context = {
        'hospital': hospital,
        'tests': tests,
        'total_tests': total_tests,
        'active_tests': active_tests,
        'inactive_tests': inactive_tests,
        'categories_count': categories_count,
        'category_choices': DiagnosticTest.CATEGORY_CHOICES,
        'sample_choices': DiagnosticTest.SAMPLE_CHOICES,
    }

    return render(request, 'accounts/hospital_admin/diagnostics.html', context)


User = get_user_model()

def hospital_users_access(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.user.role != 'hospital_admin':
        return redirect('dashboard')

    hospital = request.user.hospital

    if request.method == 'POST':
        action = request.POST.get('action')
        user_id = request.POST.get('user_id')

        if action == 'toggle' and user_id:
            user = get_object_or_404(User, id=user_id, hospital=hospital)
            field = request.POST.get('field')

            if field in ['pharmacy_access', 'blood_bank_access', 'diagnostics_access', 'patients_access', 'staff_access']:
                current = getattr(user, field)
                setattr(user, field, not current)
                user.save()
            return redirect('hospital_users_access')

        if action == 'toggle_active' and user_id:
            user = get_object_or_404(User, id=user_id, hospital=hospital)
            user.is_active = not user.is_active
            user.save()
            return redirect('hospital_users_access')

    users = User.objects.filter(hospital=hospital).order_by('-date_joined')

    total_users = users.count()
    active_users = users.filter(is_active=True).count()
    inactive_users = users.filter(is_active=False).count()
    staff_count = users.exclude(role='hospital_admin').count()

    context = {
        'hospital': hospital,
        'users': users,
        'total_users': total_users,
        'active_users': active_users,
        'inactive_users': inactive_users,
        'staff_count': staff_count,
    }

    return render(request, 'accounts/hospital_admin/users_access.html', context)
from .models import Facility, MOHJoinRequest
from django.shortcuts import get_object_or_404
from django.contrib import messages

def hospital_facility(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'hospital_admin':
        return redirect('dashboard')

    hospital = request.user.hospital

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'create':
            Facility.objects.create(
                hospital=hospital,
                name=request.POST.get('name', '').strip(),
                facility_type=request.POST.get('facility_type', 'ward'),
                capacity=int(request.POST.get('capacity') or 0),
                status=request.POST.get('status', 'active'),
                location=request.POST.get('location', '').strip(),
                description=request.POST.get('description', '').strip()
            )
            return redirect('hospital_facility')

        if action == 'edit':
            facility = get_object_or_404(Facility, id=request.POST.get('facility_id'), hospital=hospital)
            facility.name = request.POST.get('name', '').strip()
            facility.facility_type = request.POST.get('facility_type', 'ward')
            facility.capacity = int(request.POST.get('capacity') or 0)
            facility.status = request.POST.get('status', 'active')
            facility.location = request.POST.get('location', '').strip()
            facility.description = request.POST.get('description', '').strip()
            facility.save()
            return redirect('hospital_facility')

        if action == 'delete':
            Facility.objects.filter(id=request.POST.get('facility_id'), hospital=hospital).delete()
            return redirect('hospital_facility')

        if action == 'request':
            MOHJoinRequest.objects.create(
                hospital=hospital,
                requested_by=request.user,
                hospital_name=request.POST.get('hospital_name', '').strip(),
                registration_number=request.POST.get('registration_number', '').strip(),
                location=request.POST.get('location', '').strip(),
                contact_person=request.POST.get('contact_person', '').strip(),
                contact_phone=request.POST.get('contact_phone', '').strip(),
                contact_email=request.POST.get('contact_email', '').strip(),
                reason=request.POST.get('reason', '').strip()
            )
            messages.success(request, 'Your request to join MOH has been submitted successfully.')
            return redirect('hospital_facility')

    facilities = Facility.objects.filter(hospital=hospital)

    context = {
        'hospital': hospital,
        'facilities': facilities,
        'total': facilities.count(),
        'active': facilities.filter(status='active').count(),
        'inactive': facilities.filter(status='inactive').count(),
        'maintenance': facilities.filter(status='maintenance').count(),
        'type_choices': Facility.TYPE_CHOICES,
        'status_choices': Facility.STATUS_CHOICES,
    }
    return render(request, 'accounts/hospital_admin/facility.html', context)

from .models import SystemSettings
from django.contrib import messages

def hospital_admin_settings(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'hospital_admin':
        return redirect('dashboard')

    hospital = request.user.hospital
    settings = SystemSettings.load()

    if request.method == 'POST':
        # Update Hospital Profile (per hospital)
        hospital.name = request.POST.get('hospital_name', '').strip()
        hospital.email = request.POST.get('hospital_email', '').strip()
        hospital.phone = request.POST.get('hospital_phone', '').strip()
        hospital.address = request.POST.get('hospital_address', '').strip()
        hospital.save()

        # Update Global Preferences
        settings.timezone = request.POST.get('timezone', 'Asia/Dhaka')
        settings.currency = request.POST.get('currency', 'BDT')
        settings.date_format = request.POST.get('date_format', 'DD-MM-YYYY')
        settings.maintenance_mode = request.POST.get('maintenance_mode') == 'on'
        settings.save()

        messages.success(request, 'Settings updated successfully.')
        return redirect('hospital_admin_settings')

    context = {
        'hospital': hospital,
        'settings': settings,
    }
    return render(request, 'accounts/hospital_admin/settings.html', context)

def hospital_contact_support(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'hospital_admin':
        return redirect('dashboard')

    hospital = request.user.hospital

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'update':
            hospital.phone = request.POST.get('phone', '').strip()
            hospital.email = request.POST.get('email', '').strip()
            hospital.address = request.POST.get('address', '').strip()
            hospital.save()
            messages.success(request, 'Contact information updated successfully.')
            return redirect('hospital_contact_support')

    return render(
        request,
        'accounts/hospital_admin/contact_support.html',
        {'hospital': hospital}
    )


#doctors
def doctor_dashboard(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.user.role != 'doctor':
        return redirect('dashboard')

    doctor = request.user
    hospital = doctor.hospital
    today = timezone.localdate()

    patients = DoctorPatient.objects.filter(
        doctor=doctor,
        hospital=hospital
    )

    today_schedule = DoctorSchedule.objects.filter(
        doctor=doctor,
        hospital=hospital,
        schedule_date=today
    )

    upcoming_schedule = DoctorSchedule.objects.filter(
        doctor=doctor,
        hospital=hospital,
        schedule_date__gte=today,
        status='scheduled'
    ).order_by('schedule_date', 'start_time')[:5]

    recent_patients = patients[:5]

    today_patient_count = today_schedule.values('patient_id').distinct().count()

    pending_schedule_count = DoctorSchedule.objects.filter(
        doctor=doctor,
        hospital=hospital,
        schedule_date__gte=today,
        status='scheduled'
    ).count()

    department_count = Department.objects.filter(
        hospital=hospital,
        is_active=True
    ).count()

    notice_count = Notice.objects.filter(
        hospital=hospital,
        status='published'
    ).count()

    context = {
        'doctor': doctor,
        'hospital': hospital,
        'total_patients': patients.count(),
        'today_patients': today_patient_count,
        'upcoming_count': pending_schedule_count,
        'department_count': department_count,
        'today_schedule': today_schedule,
        'upcoming_schedule': upcoming_schedule,
        'recent_patients': recent_patients,
        'notice_count': notice_count,
        'today': today
    }

    return render(
        request,
        'accounts/doctor/dashboard.html',
        context
    )

def doctor_patient_summary(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.user.role != 'doctor':
        return redirect('dashboard')

    doctor = request.user
    hospital = doctor.hospital

    patients = DoctorPatient.objects.filter(
        doctor=doctor,
        hospital=hospital
    )

    search = request.GET.get('search', '').strip()

    if search:
        patients = patients.filter(
            models.Q(patient_name__icontains=search) |
            models.Q(patient_id__icontains=search) |
            models.Q(phone__icontains=search)
        )

    total_patients = patients.count()
    male_patients = patients.filter(gender__iexact='male').count()
    female_patients = patients.filter(gender__iexact='female').count()

    today = timezone.localdate()

    today_schedule = DoctorSchedule.objects.filter(
        doctor=doctor,
        hospital=hospital,
        schedule_date=today
    )

    today_patient_ids = list(
        today_schedule.values_list(
            'patient_id',
            flat=True
        )
    )

    today_patients = patients.filter(
        patient_id__in=today_patient_ids
    ).count()

    context = {
        'doctor': doctor,
        'hospital': hospital,
        'patients': patients,
        'total_patients': total_patients,
        'male_patients': male_patients,
        'female_patients': female_patients,
        'today_patients': today_patients,
        'today_patient_ids': today_patient_ids,
        'search': search
    }

    return render(
        request,
        'accounts/doctor/patient_summary.html',
        context
    )

def doctor_prescription(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.user.role != 'doctor':
        return redirect('dashboard')

    doctor = request.user
    hospital = doctor.hospital

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'add':
            patient_id = request.POST.get('patient')
            medicine_name = request.POST.get('medicine_name', '').strip()
            dosage = request.POST.get('dosage', '').strip()
            frequency = request.POST.get('frequency', '').strip()
            meal_timing = request.POST.get('meal_timing', '').strip()
            duration = request.POST.get('duration', '').strip()
            notes = request.POST.get('notes', '').strip()

            patient = DoctorPatient.objects.filter(
                id=patient_id,
                doctor=doctor,
                hospital=hospital
            ).first()

            if patient and medicine_name and dosage and frequency and meal_timing and duration:
                DoctorPrescription.objects.create(
                    doctor=doctor,
                    hospital=hospital,
                    patient=patient,
                    medicine_name=medicine_name,
                    dosage=dosage,
                    frequency=frequency,
                    meal_timing=meal_timing,
                    duration=duration,
                    notes=notes
                )

        elif action == 'edit':
            prescription_id = request.POST.get('prescription_id')

            prescription = DoctorPrescription.objects.filter(
                id=prescription_id,
                doctor=doctor,
                hospital=hospital
            ).first()

            if prescription:
                patient_id = request.POST.get('patient')

                patient = DoctorPatient.objects.filter(
                    id=patient_id,
                    doctor=doctor,
                    hospital=hospital
                ).first()

                if patient:
                    prescription.patient = patient

                prescription.medicine_name = request.POST.get('medicine_name', '').strip()
                prescription.dosage = request.POST.get('dosage', '').strip()
                prescription.frequency = request.POST.get('frequency', '').strip()
                prescription.meal_timing = request.POST.get('meal_timing', '').strip()
                prescription.duration = request.POST.get('duration', '').strip()
                prescription.notes = request.POST.get('notes', '').strip()
                prescription.save()

        elif action == 'delete':
            prescription_id = request.POST.get('prescription_id')

            DoctorPrescription.objects.filter(
                id=prescription_id,
                doctor=doctor,
                hospital=hospital
            ).delete()

        return redirect('doctor_prescription')

    prescriptions = DoctorPrescription.objects.filter(
        doctor=doctor,
        hospital=hospital
    ).select_related('patient')

    patients = DoctorPatient.objects.filter(
        doctor=doctor,
        hospital=hospital
    )

    context = {
        'doctor': doctor,
        'hospital': hospital,
        'prescriptions': prescriptions,
        'patients': patients,
    }

    return render(
        request,
        'accounts/doctor/prescription.html',
        context
    )

def doctor_referrals(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.user.role != 'doctor':
        return redirect('dashboard')

    doctor = request.user
    hospital = doctor.hospital

    patients = DoctorPatient.objects.filter(
        doctor=doctor,
        hospital=hospital
    )

    specialists = request.user.__class__.objects.filter(
        role='doctor',
        is_active=True
    ).exclude(
        id=doctor.id
    ).select_related('hospital')

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'add':
            patient_id = request.POST.get('patient')
            specialist_id = request.POST.get('specialist')
            reason = request.POST.get('reason', '').strip()
            priority = request.POST.get('priority', 'routine')

            patient = DoctorPatient.objects.filter(
                id=patient_id,
                doctor=doctor,
                hospital=hospital
            ).first()

            specialist = request.user.__class__.objects.filter(
                id=specialist_id,
                role='doctor',
                is_active=True
            ).exclude(
                id=doctor.id
            ).first()

            if patient and specialist and reason:
                referral = DoctorReferral.objects.create(
                    doctor=doctor,
                    patient=patient,
                    specialist=specialist,
                    reason=reason,
                    priority=priority
                )

                if request.FILES.get('document'):
                    referral.document = request.FILES['document']
                    referral.save()

        elif action == 'edit':
            referral_id = request.POST.get('referral_id')

            referral = DoctorReferral.objects.filter(
                id=referral_id,
                doctor=doctor
            ).first()

            if referral:
                patient_id = request.POST.get('patient')
                specialist_id = request.POST.get('specialist')

                patient = DoctorPatient.objects.filter(
                    id=patient_id,
                    doctor=doctor,
                    hospital=hospital
                ).first()

                specialist = request.user.__class__.objects.filter(
                    id=specialist_id,
                    role='doctor',
                    is_active=True
                ).exclude(
                    id=doctor.id
                ).first()

                if patient:
                    referral.patient = patient

                if specialist:
                    referral.specialist = specialist

                referral.reason = request.POST.get('reason', '').strip()
                referral.priority = request.POST.get(
                    'priority',
                    'routine'
                )

                if request.FILES.get('document'):
                    referral.document = request.FILES['document']

                referral.save()

        elif action == 'delete':
            referral_id = request.POST.get('referral_id')

            DoctorReferral.objects.filter(
                id=referral_id,
                doctor=doctor
            ).delete()

        return redirect('doctor_referrals')

    referrals = DoctorReferral.objects.filter(
        doctor=doctor
    ).select_related(
        'patient',
        'specialist',
        'specialist__hospital'
    )

    context = {
        'doctor': doctor,
        'hospital': hospital,
        'patients': patients,
        'specialists': specialists,
        'referrals': referrals
    }

    return render(
        request,
        'accounts/doctor/referrals.html',
        context
    )

def doctor_appointments(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.user.role != 'doctor':
        return redirect('dashboard')

    doctor = request.user
    hospital = doctor.hospital

    if request.method == 'POST':
        action = request.POST.get('action')
        appointment_id = request.POST.get('appointment_id')

        if action == 'update_status':
            appointment = DoctorSchedule.objects.filter(
                id=appointment_id,
                doctor=doctor,
                hospital=hospital
            ).first()

            if appointment:
                status = request.POST.get('status')

                if status in ['scheduled', 'completed', 'cancelled']:
                    appointment.status = status
                    appointment.save(update_fields=['status'])

        return redirect('doctor_appointments')

    appointments = DoctorSchedule.objects.filter(
        doctor=doctor,
        hospital=hospital
    )

    today = timezone.localdate()

    today_appointments = appointments.filter(
        schedule_date=today
    ).count()

    upcoming_appointments = appointments.filter(
        schedule_date__gte=today,
        status='scheduled'
    ).count()

    completed_appointments = appointments.filter(
        status='completed'
    ).count()

    cancelled_appointments = appointments.filter(
        status='cancelled'
    ).count()

    search = request.GET.get('search', '').strip()

    if search:
        appointments = appointments.filter(
            models.Q(patient_name__icontains=search) |
            models.Q(patient_id__icontains=search)
        )

    appointments = appointments.order_by(
        'schedule_date',
        'start_time'
    )

    context = {
        'doctor': doctor,
        'hospital': hospital,
        'appointments': appointments,
        'today_appointments': today_appointments,
        'upcoming_appointments': upcoming_appointments,
        'completed_appointments': completed_appointments,
        'cancelled_appointments': cancelled_appointments,
        'search': search,
    }

    return render(
        request,
        'accounts/doctor/appointments.html',
        context
    )
from .models import DoctorProfile
from django.contrib import messages

def doctor_profile(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'doctor':
        return redirect('dashboard')

    profile, created = DoctorProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', '').strip()
        user.last_name = request.POST.get('last_name', '').strip()
        user.phone = request.POST.get('phone', '').strip()
        user.save()

        profile.registration_number = request.POST.get('registration_number', '').strip()
        profile.specialization = request.POST.get('specialization', '').strip()
        profile.department = request.POST.get('department', '').strip()
        profile.qualification = request.POST.get('qualification', '').strip()
        profile.experience_years = int(request.POST.get('experience_years') or 0)
        profile.bio = request.POST.get('bio', '').strip()
        profile.address = request.POST.get('address', '').strip()
        profile.gender = request.POST.get('gender', '').strip()
        profile.blood_group = request.POST.get('blood_group', '').strip()

        dob = request.POST.get('date_of_birth')
        profile.date_of_birth = dob if dob else None

        if request.FILES.get('profile_image'):
            profile.profile_image = request.FILES['profile_image']

        profile.save()
        messages.success(request, 'Profile updated successfully.')
        return redirect('doctor_profile')

    context = {
        'profile': profile,
        'user': request.user,
        'hospital': request.user.hospital,
    }
    return render(request, 'accounts/doctor/profile.html', context)



#Nourse
def nurse_dashboard(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'nurse':
        return redirect('dashboard')

    hospital = request.user.hospital
    today = timezone.now().date()
    week_ago = today - timedelta(days=6)

    total_patients = 0
    today_patients = 0
    week_patients = 0
    active_patients = 0

    daily_labels = []
    daily_data = []

    if hospital:
        patients = Patient.objects.filter(hospital=hospital)
        total_patients = patients.count()
        today_patients = patients.filter(created_at__date=today).count()
        week_patients = patients.filter(created_at__date__gte=week_ago).count()
        active_patients = patients.filter(is_active=True).count() if hasattr(Patient, 'is_active') else total_patients

        for i in range(6, -1, -1):
            day = today - timedelta(days=i)
            daily_labels.append(day.strftime('%a'))
            daily_data.append(patients.filter(created_at__date=day).count())

    recent_patients = []
    if hospital:
        recent_patients = Patient.objects.filter(hospital=hospital).order_by('-created_at')[:6]

    context = {
        'hospital': hospital,
        'user': request.user,
        'total_patients': total_patients,
        'today_patients': today_patients,
        'week_patients': week_patients,
        'active_patients': active_patients,
        'daily_labels': json.dumps(daily_labels),   
        'daily_data': json.dumps(daily_data),       
        'recent_patients': recent_patients,
        'today': today,
    }
    return render(request, 'accounts/nurse/dashboard.html', context)
def nurse_vital_signs(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'nurse':
        return redirect('dashboard')

    hospital = request.user.hospital
    patients = Patient.objects.filter(hospital=hospital) if hospital else Patient.objects.none()

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'create':
            VitalSign.objects.create(
                hospital=hospital,
                recorded_by=request.user,
                patient_id=request.POST.get('patient'),
                temperature=request.POST.get('temperature') or None,
                pulse=request.POST.get('pulse') or None,
                blood_pressure=request.POST.get('blood_pressure', '').strip(),
                respiratory_rate=request.POST.get('respiratory_rate') or None,
                spo2=request.POST.get('spo2') or None,
                blood_sugar=request.POST.get('blood_sugar') or None,
                weight=request.POST.get('weight') or None,
                height=request.POST.get('height') or None,
                notes=request.POST.get('notes', '').strip()
            )
            messages.success(request, 'Vital signs recorded successfully.')
            return redirect('nurse_vital_signs')

        if action == 'edit':
            vital = get_object_or_404(VitalSign, id=request.POST.get('vital_id'), hospital=hospital)
            vital.patient_id = request.POST.get('patient')
            vital.temperature = request.POST.get('temperature') or None
            vital.pulse = request.POST.get('pulse') or None
            vital.blood_pressure = request.POST.get('blood_pressure', '').strip()
            vital.respiratory_rate = request.POST.get('respiratory_rate') or None
            vital.spo2 = request.POST.get('spo2') or None
            vital.blood_sugar = request.POST.get('blood_sugar') or None
            vital.weight = request.POST.get('weight') or None
            vital.height = request.POST.get('height') or None
            vital.notes = request.POST.get('notes', '').strip()
            vital.save()
            messages.success(request, 'Vital signs updated successfully.')
            return redirect('nurse_vital_signs')

        if action == 'delete':
            VitalSign.objects.filter(id=request.POST.get('vital_id'), hospital=hospital).delete()
            messages.success(request, 'Vital signs deleted.')
            return redirect('nurse_vital_signs')

    vitals = VitalSign.objects.filter(hospital=hospital).select_related('patient', 'recorded_by') if hospital else VitalSign.objects.none()

    context = {
        'hospital': hospital,
        'patients': patients,
        'vitals': vitals,
        'total': vitals.count(),
        'today_count': vitals.filter(recorded_at__date=timezone.now().date()).count() if hospital else 0,
    }
    return render(request, 'accounts/nurse/vital_signs.html', context)

def nurse_notes(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'nurse':
        return redirect('dashboard')

    hospital = request.user.hospital
    patients = Patient.objects.filter(hospital=hospital) if hospital else Patient.objects.none()

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'create':
            NursingNote.objects.create(
                hospital=hospital,
                recorded_by=request.user,
                patient_id=request.POST.get('patient'),
                note_type=request.POST.get('note_type', 'general'),
                title=request.POST.get('title', '').strip(),
                note=request.POST.get('note', '').strip()
            )
            messages.success(request, 'Nursing note added successfully.')
            return redirect('nurse_notes')

        if action == 'edit':
            note_obj = get_object_or_404(NursingNote, id=request.POST.get('note_id'), hospital=hospital)
            note_obj.patient_id = request.POST.get('patient')
            note_obj.note_type = request.POST.get('note_type', 'general')
            note_obj.title = request.POST.get('title', '').strip()
            note_obj.note = request.POST.get('note', '').strip()
            note_obj.save()
            messages.success(request, 'Nursing note updated successfully.')
            return redirect('nurse_notes')

        if action == 'delete':
            NursingNote.objects.filter(id=request.POST.get('note_id'), hospital=hospital).delete()
            messages.success(request, 'Nursing note deleted.')
            return redirect('nurse_notes')

    notes = NursingNote.objects.filter(hospital=hospital).select_related('patient', 'recorded_by') if hospital else NursingNote.objects.none()

    context = {
        'hospital': hospital,
        'patients': patients,
        'notes': notes,
        'total': notes.count(),
        'today_count': notes.filter(created_at__date=timezone.now().date()).count() if hospital else 0,
        'note_type_choices': NursingNote.NOTE_TYPE_CHOICES,
    }
    return render(request, 'accounts/nurse/nursing_notes.html', context)

def nurse_patients(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'nurse':
        return redirect('dashboard')

    hospital = request.user.hospital
    patients = Patient.objects.filter(hospital=hospital).order_by('-created_at') if hospital else Patient.objects.none()

    search = request.GET.get('search', '').strip()
    if search:
        patients = patients.filter(
            models.Q(patient_name__icontains=search) |
            models.Q(name__icontains=search) |
            models.Q(patient_id__icontains=search) |
            models.Q(phone__icontains=search)
        )

    today = timezone.now().date()
    total = patients.count() if not search else Patient.objects.filter(hospital=hospital).count()
    today_count = Patient.objects.filter(hospital=hospital, created_at__date=today).count() if hospital else 0

    context = {
        'hospital': hospital,
        'patients': patients,
        'total': total,
        'today_count': today_count,
        'search': search,
    }
    return render(request, 'accounts/nurse/patients.html', context)

def nurse_profile(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'nurse':
        return redirect('dashboard')

    profile, created = NurseProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        action = request.POST.get('action', 'update')

        if action == 'remove_photo':
            if profile.profile_image:
                profile.profile_image.delete(save=False)
                profile.profile_image = None
                profile.save()
            messages.success(request, 'Profile photo removed.')
            return redirect('nurse_profile')

        user = request.user
        user.first_name = request.POST.get('first_name', '').strip()
        user.last_name = request.POST.get('last_name', '').strip()
        user.phone = request.POST.get('phone', '').strip()
        user.save()

        profile.registration_number = request.POST.get('registration_number', '').strip()
        profile.department = request.POST.get('department', '').strip()
        profile.qualification = request.POST.get('qualification', '').strip()
        profile.experience_years = int(request.POST.get('experience_years') or 0)
        profile.shift = request.POST.get('shift', '').strip()
        profile.bio = request.POST.get('bio', '').strip()
        profile.address = request.POST.get('address', '').strip()
        profile.gender = request.POST.get('gender', '').strip()
        profile.blood_group = request.POST.get('blood_group', '').strip()

        dob = request.POST.get('date_of_birth')
        profile.date_of_birth = dob if dob else None

        if request.FILES.get('profile_image'):
            if profile.profile_image:
                profile.profile_image.delete(save=False)
            profile.profile_image = request.FILES['profile_image']

        profile.save()
        messages.success(request, 'Profile updated successfully.')
        return redirect('nurse_profile')

    context = {
        'profile': profile,
        'user': request.user,
        'hospital': request.user.hospital,
    }
    return render(request, 'accounts/nurse/profile.html', context)

# Patient
User = get_user_model()

User = get_user_model()

def patient_dashboard(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'patient':
        return redirect('dashboard')

    hospital = request.user.hospital
    today = timezone.now().date()
    user = request.user

    patient = None
    if hospital:
        filters = Q()
        if user.phone:
            filters |= Q(phone=user.phone)
        name = user.get_full_name()
        if name:
            if hasattr(Patient, 'patient_name'):
                filters |= Q(patient_name__icontains=name)
            elif hasattr(Patient, 'name'):
                filters |= Q(name__icontains=name)
        if filters:
            patient = Patient.objects.filter(hospital=hospital).filter(filters).first()

    total_doctors = 0
    total_departments = 0
    upcoming_appointments = 0
    completed_appointments = 0
    recent_appointments = []
    notices = []

    if hospital:
        total_doctors = User.objects.filter(
            hospital=hospital,
            role='doctor',
            is_active=True
        ).count()

        try:
            total_departments = Department.objects.filter(
                hospital=hospital,
                is_active=True
            ).count()
        except Exception:
            total_departments = 0

        appt_qs = DoctorSchedule.objects.filter(hospital=hospital)

        if patient:
            patient_name = getattr(patient, 'patient_name', None) or getattr(patient, 'name', '') or ''
            patient_id = getattr(patient, 'patient_id', '') or ''
            name_filter = Q()
            if patient_id:
                name_filter |= Q(patient_id=patient_id)
            if patient_name:
                name_filter |= Q(patient_name__icontains=patient_name)
            if name_filter:
                appt_qs = appt_qs.filter(name_filter)
        else:
            name = user.get_full_name() or user.username
            appt_qs = appt_qs.filter(patient_name__icontains=name)

        upcoming_appointments = appt_qs.filter(
            schedule_date__gte=today,
            status='scheduled'
        ).count()

        completed_appointments = appt_qs.filter(
            status='completed'
        ).count()

        recent_appointments = appt_qs.order_by(
            '-schedule_date',
            '-start_time'
        )[:5]

        notices = Notice.objects.filter(
            status='published'
        ).filter(
            Q(hospital=hospital) | Q(hospital__isnull=True)
        ).order_by(
            '-publish_date',
            '-created_at'
        )[:5]

    context = {
        'user': user,
        'hospital': hospital,
        'patient': patient,
        'total_doctors': total_doctors,
        'total_departments': total_departments,
        'upcoming_appointments': upcoming_appointments,
        'completed_appointments': completed_appointments,
        'recent_appointments': recent_appointments,
        'notices': notices,
        'today': today,
    }
    return render(request, 'accounts/patient/dashboard.html', context)

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

    hospital = request.user.hospital
    search = request.GET.get('search', '').strip()

    departments = Department.objects.none()
    if hospital:
        departments = Department.objects.filter(hospital=hospital, is_active=True).order_by('name')
        if search:
            departments = departments.filter(name__icontains=search)

    context = {
        'hospital': hospital,
        'departments': departments,
        'total': departments.count(),
        'search': search,
    }
    return render(request, 'accounts/patient/departments.html', context)

def patient_doctors(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'patient':
        return redirect('dashboard')

    hospital = request.user.hospital
    search = request.GET.get('q', '').strip() or request.GET.get('search', '').strip()

    doctors = User.objects.none()
    if hospital:
        doctors = User.objects.filter(
            hospital=hospital,
            role='doctor',
            is_active=True
        ).order_by('first_name', 'last_name')

        if search:
            doctors = doctors.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(email__icontains=search) |
                Q(phone__icontains=search)
            )

    context = {
        'hospital': hospital,
        'doctors': doctors,
        'total': doctors.count(),
        'search': search,
    }
    return render(request, 'accounts/patient/doctors.html', context)
User = get_user_model()

def patient_appointments(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'patient':
        return redirect('dashboard')

    hospital = request.user.hospital
    user = request.user

    doctors = User.objects.none()
    if hospital:
        doctors = User.objects.filter(
            hospital=hospital,
            role='doctor',
            is_active=True
        ).order_by('first_name', 'last_name')

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'book':
            doctor_id = request.POST.get('doctor')
            appt_date = request.POST.get('appointment_date')
            appt_time = request.POST.get('appointment_time')
            reason = request.POST.get('reason', '').strip()
            amount = request.POST.get('amount') or 500
            pay_now = request.POST.get('pay_now') == 'on'

            if not (hospital and doctor_id and appt_date and appt_time):
                messages.error(request, 'Please fill all required fields.')
                return redirect('patient_appointments')

            PatientAppointment.objects.create(
                hospital=hospital,
                patient_user=user,
                doctor_id=doctor_id,
                patient_name=user.get_full_name() or user.username,
                patient_phone=user.phone or '',
                appointment_date=appt_date,
                appointment_time=appt_time,
                reason=reason,
                amount=Decimal(str(amount)),
                payment_status='paid' if pay_now else 'pending',
                status='pending'
            )
            if pay_now:
                messages.success(request, 'Payment successful. Appointment submitted for counter approval.')
            else:
                messages.success(request, 'Appointment submitted. Please complete payment.')
            return redirect('patient_appointments')

        if action == 'pay':
            appt = get_object_or_404(
                PatientAppointment,
                id=request.POST.get('appointment_id'),
                patient_user=user
            )
            appt.payment_status = 'paid'
            appt.save()
            messages.success(request, 'Payment successful. Waiting for counter approval.')
            return redirect('patient_appointments')

        if action == 'cancel':
            appt = get_object_or_404(
                PatientAppointment,
                id=request.POST.get('appointment_id'),
                patient_user=user
            )
            if appt.status in ['pending', 'approved']:
                appt.status = 'cancelled'
                appt.save()
                messages.success(request, 'Appointment cancelled.')
            return redirect('patient_appointments')

    appointments = PatientAppointment.objects.filter(
        patient_user=user
    ).select_related('doctor', 'hospital')

    context = {
        'hospital': hospital,
        'doctors': doctors,
        'appointments': appointments,
        'total': appointments.count(),
        'pending': appointments.filter(status='pending').count(),
        'approved': appointments.filter(status='approved').count(),
    }
    return render(request, 'accounts/patient/appointments.html', context)

from .models import MedicalRecord

def patient_medical_records(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'patient':
        return redirect('dashboard')

    user = request.user
    hospital = user.hospital
    search = request.GET.get('search', '').strip()

    records = MedicalRecord.objects.filter(
        Q(patient_user=user) |
        Q(patient_phone=user.phone) |
        Q(patient_name__icontains=user.get_full_name() or user.username)
    ).select_related('hospital', 'uploaded_by')

    if hospital:
        records = records.filter(hospital=hospital)

    if search:
        records = records.filter(
            Q(title__icontains=search) |
            Q(test_name__icontains=search) |
            Q(record_type__icontains=search)
        )

    context = {
        'hospital': hospital,
        'records': records,
        'total': records.count(),
        'search': search,
    }
    return render(request, 'accounts/patient/medical_records.html', context)

from .models import PatientPayment, PatientAppointment
from decimal import Decimal
def patient_payments(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'patient':
        return redirect('dashboard')

    user = request.user
    hospital = user.hospital

    unpaid_appointments = PatientAppointment.objects.filter(
        patient_user=user,
        payment_status='pending'
    ).exclude(status='cancelled')

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'pay':
            amount = request.POST.get('amount') or 0
            purpose = request.POST.get('purpose', 'appointment')
            method = request.POST.get('method', 'bkash')
            transaction_id = request.POST.get('transaction_id', '').strip()
            note = request.POST.get('note', '').strip()
            appointment_id = request.POST.get('appointment_id') or None

            if not hospital:
                messages.error(request, 'No hospital assigned.')
                return redirect('patient_payments')

            payment = PatientPayment.objects.create(
                hospital=hospital,
                patient_user=user,
                appointment_id=appointment_id if appointment_id else None,
                amount=Decimal(str(amount)),
                purpose=purpose,
                method=method,
                transaction_id=transaction_id,
                note=note,
                status='paid'
            )

            if appointment_id:
                appt = PatientAppointment.objects.filter(
                    id=appointment_id,
                    patient_user=user
                ).first()
                if appt:
                    appt.payment_status = 'paid'
                    appt.save()

            messages.success(request, 'Payment submitted. Counter will verify and receive the amount.')
            return redirect('patient_payments')

    payments = PatientPayment.objects.filter(
        patient_user=user
    ).select_related('appointment', 'hospital')

    total_paid = sum(p.amount for p in payments if p.status in ['paid', 'verified'])
    pending_count = payments.filter(status='pending').count()
    paid_count = payments.filter(status__in=['paid', 'verified']).count()

    context = {
        'hospital': hospital,
        'payments': payments,
        'unpaid_appointments': unpaid_appointments,
        'total_paid': total_paid,
        'pending_count': pending_count,
        'paid_count': paid_count,
        'method_choices': PatientPayment.METHOD_CHOICES,
        'purpose_choices': PatientPayment.PURPOSE_CHOICES,
    }
    return render(request, 'accounts/patient/payments.html', context)

from .models import PatientEmergencyContact, PatientAppointment
User = get_user_model()

def patient_emergency_contact(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'patient':
        return redirect('dashboard')

    user = request.user
    hospital = user.hospital

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'create':
            PatientEmergencyContact.objects.create(
                patient_user=user,
                hospital=hospital,
                contact_name=request.POST.get('contact_name', '').strip(),
                relation=request.POST.get('relation', 'other'),
                phone=request.POST.get('phone', '').strip(),
                is_primary=request.POST.get('is_primary') == 'on'
            )
            messages.success(request, 'Contact added.')
            return redirect('patient_emergency_contact')

        if action == 'edit':
            contact = get_object_or_404(
                PatientEmergencyContact,
                id=request.POST.get('contact_id'),
                patient_user=user
            )
            contact.contact_name = request.POST.get('contact_name', '').strip()
            contact.relation = request.POST.get('relation', 'other')
            contact.phone = request.POST.get('phone', '').strip()
            contact.is_primary = request.POST.get('is_primary') == 'on'
            contact.save()
            messages.success(request, 'Contact updated.')
            return redirect('patient_emergency_contact')

        if action == 'delete':
            PatientEmergencyContact.objects.filter(
                id=request.POST.get('contact_id'),
                patient_user=user
            ).delete()
            messages.success(request, 'Contact deleted.')
            return redirect('patient_emergency_contact')

    contacts = PatientEmergencyContact.objects.filter(patient_user=user)

    doctor_ids = PatientAppointment.objects.filter(
        patient_user=user,
        status__in=['pending', 'approved', 'completed']
    ).values_list('doctor_id', flat=True).distinct()

    doctors = User.objects.filter(id__in=doctor_ids, role='doctor').select_related('doctor_profile')

    context = {
        'hospital': hospital,
        'contacts': contacts,
        'doctors': doctors,
        'relation_choices': PatientEmergencyContact.RELATION_CHOICES,
    }
    return render(request, 'accounts/patient/emergency_contact.html', context)
from .models import PatientProfile

def patient_profile(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'patient':
        return redirect('dashboard')

    profile, created = PatientProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        action = request.POST.get('action', 'update')

        if action == 'remove_photo':
            if profile.profile_image:
                profile.profile_image.delete(save=False)
                profile.profile_image = None
                profile.save()
            messages.success(request, 'Profile photo removed.')
            return redirect('patient_profile')

        user = request.user
        user.first_name = request.POST.get('first_name', '').strip()
        user.last_name = request.POST.get('last_name', '').strip()
        user.phone = request.POST.get('phone', '').strip()
        user.save()

        profile.patient_id = request.POST.get('patient_id', '').strip()
        profile.gender = request.POST.get('gender', '').strip()
        profile.blood_group = request.POST.get('blood_group', '').strip()
        profile.nid = request.POST.get('nid', '').strip()
        profile.address = request.POST.get('address', '').strip()
        profile.city = request.POST.get('city', '').strip()
        profile.emergency_name = request.POST.get('emergency_name', '').strip()
        profile.emergency_phone = request.POST.get('emergency_phone', '').strip()
        profile.allergies = request.POST.get('allergies', '').strip()
        profile.chronic_conditions = request.POST.get('chronic_conditions', '').strip()

        dob = request.POST.get('date_of_birth')
        profile.date_of_birth = dob if dob else None

        if request.FILES.get('profile_image'):
            if profile.profile_image:
                profile.profile_image.delete(save=False)
            profile.profile_image = request.FILES['profile_image']

        profile.save()
        messages.success(request, 'Profile updated successfully.')
        return redirect('patient_profile')

    context = {
        'profile': profile,
        'user': request.user,
        'hospital': request.user.hospital,
    }
    return render(request, 'accounts/patient/profile.html', context)
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


# Pharmacy
def pharmacy_dashboard(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'pharmacy':
        return redirect('dashboard')

    hospital = request.user.hospital
    context = {
        'hospital': hospital,
        'patients_count': Patient.objects.filter(hospital=hospital).count() if hospital else 0,
        'staff_count': Staff.objects.filter(hospital=hospital).count() if hospital else 0,
    }
    return render(request, 'accounts/pharmacy/dashboard.html', context)
