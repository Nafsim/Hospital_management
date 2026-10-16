import json
from django.shortcuts import render , redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth import login, authenticate
from django.contrib import messages
from .forms import LoginForm, HospitalCreationForm
import calendar
from datetime import datetime, timedelta, date
from django.apps import apps
from patients.models import Patient, Visit
from staff.models import Staff
from .models import Billing, BloodCollection, Medicine
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
from django.http import JsonResponse
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4 
from django.db import models, IntegrityError
from .models import Blood
from .models import DiagnosticTest 
from .models import Facility, MOHJoinRequest
from django.contrib import messages
from .models import VitalSign 
from .models import NursingNote 
from .models import NurseProfile 
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
import csv
from .models import PatientAppointment
from django.db import IntegrityError
from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction
from .models import (
    User, Notice, Department, DoctorPatient, DoctorSchedule,
    DoctorPrescription, DoctorReferral, ChatMessage,
)
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
    total_doctors = User.objects.filter(
        role='doctor',
        is_active=True,
        hospital__is_active=True
    ).count()
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

    facilities = Hospital.objects.filter(is_active=True).order_by('-created_at')

    if search:
        facilities = facilities.filter(
            Q(name__icontains=search) |
            Q(code__icontains=search) |
            Q(city__icontains=search) |
            Q(address__icontains=search)
        )

    total_hospitals = Hospital.objects.filter(is_active=True, facility_type='hospital').count()
    total_clinics   = Hospital.objects.filter(is_active=True, facility_type='clinic').count()
    total_labs      = Hospital.objects.filter(is_active=True, facility_type='lab').count()
    total_specialty = Hospital.objects.filter(is_active=True, facility_type='specialty').count()

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
        total_departments = Department.objects.filter(hospital=hospital).count()

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

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'create':
            if not hospital:
                messages.error(request, 'No hospital is linked to your account yet.')
                return redirect('hospital_admin_notices')

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

    # Keep hospital data isolated; an unassigned admin sees an empty list.
    notices = Notice.objects.filter(
        Q(hospital=hospital) | Q(hospital__isnull=True)
    ).order_by('-created_at') if hospital else Notice.objects.none()

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
    hospital_departments = Department.objects.filter(
        hospital=hospital,
        is_active=True
    ).order_by('name')
    hospital_department_labels = {
        dept.name: dept.get_name_display() for dept in hospital_departments
    }

    if hospital_department_labels:
        department_choices = list(hospital_department_labels.items())
    else:
        department_choices = list(Staff.DEPARTMENT_CHOICES)
        hospital_department_labels = dict(Staff.DEPARTMENT_CHOICES)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'create':
            if not hospital:
                messages.error(request, 'Create a hospital profile before adding doctors.')
                return redirect('hospital_doctors')

            email = request.POST.get('email')
            if User.objects.filter(email=email).exists():
                messages.error(request, 'A user with this email already exists.')
                return redirect('hospital_doctors')

            department = request.POST.get('department', '').strip()
            department_name = hospital_department_labels.get(department)
            if not department_name:
                messages.error(request, 'Please select a valid department.')
                return redirect('hospital_doctors')

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

            department = request.POST.get('department', '').strip()
            department_name = hospital_department_labels.get(department)
            if not department_name:
                messages.error(request, 'Please select a valid department.')
                return redirect('hospital_doctors')

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
        'departments': department_choices,
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
            date_of_joining = request.POST.get('date_of_joining') or timezone.localdate()
            qualification = request.POST.get('qualification', '').strip()
            is_active = request.POST.get('is_active', 'on') == 'on'

            role_map = {
                'Doctor': 'doctor',
                'Nurse': 'nurse',
                'Accountant': 'accountant',
                'Laboratory': 'lab',
                'Counter / Reception': 'counter',
                'Blood Bank': 'bloodbank',
                'Pharmacy': 'pharmacy',          # ← added
            }
            role = role_map.get(department, 'nurse')

            if not password:
                messages.error(request, 'Password is required for the staff login account.')
                return redirect('hospital_staff')

            if User.objects.filter(email=email).exists():
                messages.error(request, 'A staff account with this email already exists.')
                return redirect('hospital_staff')
            if Staff.objects.filter(employee_id=employee_id).exists():
                messages.error(request, 'A staff member with this employee ID already exists.')
                return redirect('hospital_staff')
            if national_id and Staff.objects.filter(national_id=national_id).exists():
                messages.error(request, 'A staff member with this national ID already exists.')
                return redirect('hospital_staff')

            user = User.objects.create_user(
                username=email,
                email=email,
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                password=password,
                role=role,
                hospital=hospital,
                is_active=is_active
            )
            user.set_password(password)
            user.save(update_fields=['password'])

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
            messages.success(request, 'Staff member created successfully.')
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

    if request.method == 'POST':
        if not hospital:
            name = request.POST.get('name', '').strip()
            code = request.POST.get('code', '').strip()
            address = request.POST.get('address', '').strip()
            if not name or not code or not address:
                messages.error(request, 'Hospital name, code, and address are required.')
                return redirect('hospital_profile')
            if Hospital.objects.filter(code=code).exists():
                messages.error(request, 'A hospital with this code already exists.')
                return redirect('hospital_profile')
            hospital = Hospital.objects.create(
                name=name,
                code=code,
                address=address,
                city=request.POST.get('city', '').strip(),
                phone=request.POST.get('phone', '').strip(),
                email=request.POST.get('email', '').strip(),
                facility_type=request.POST.get('facility_type', 'hospital'),
                is_active=False,
            )
            request.user.hospital = hospital
            request.user.save(update_fields=['hospital'])
            messages.success(request, 'Hospital profile created successfully.')
            return redirect('hospital_profile')

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
            name = request.POST.get('name', '').strip()
            is_active = request.POST.get('is_active') == 'on'

            if not name:
                messages.error(request, 'Please select a department name.')
                return redirect('hospital_departments')

            try:
                department, created = Department.objects.get_or_create(
                    hospital=hospital,
                    name=name,
                    defaults={'is_active': is_active},
                )
            except IntegrityError:
                created = False
                department = Department.objects.filter(
                    hospital=hospital,
                    name=name
                ).first()

            if created:
                messages.success(request, 'Department created successfully.')
            else:
                if department and department.is_active != is_active:
                    department.is_active = is_active
                    department.save(update_fields=['is_active', 'updated_at'])
                    messages.info(request, 'Department already existed. Status was updated.')
                else:
                    messages.warning(request, 'This department already exists for your hospital.')

            return redirect('hospital_departments')

        if action == 'edit':
            department_id = request.POST.get('department_id')
            name = request.POST.get('name', '').strip()
            is_active = request.POST.get('is_active') == 'on'

            if not name:
                messages.error(request, 'Please select a department name.')
                return redirect('hospital_departments')

            department = get_object_or_404(
                Department,
                id=department_id,
                hospital=hospital
            )

            try:
                department.name = name
                department.is_active = is_active
                department.save()
                messages.success(request, 'Department updated successfully.')
            except IntegrityError:
                messages.error(
                    request,
                    'Another department with this name already exists in your hospital.'
                )

            return redirect('hospital_departments')

        if action == 'delete':
            department_id = request.POST.get('department_id')

            Department.objects.filter(
                id=department_id,
                hospital=hospital
            ).delete()
            messages.success(request, 'Department deleted successfully.')

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
        if hospital:
            hospital.name = request.POST.get('hospital_name', '').strip()
            hospital.email = request.POST.get('hospital_email', '').strip()
            hospital.phone = request.POST.get('hospital_phone', '').strip()
            hospital.address = request.POST.get('hospital_address', '').strip()
            hospital.save()
        else:
            name = request.POST.get('hospital_name', '').strip()
            code = request.POST.get('hospital_code', '').strip()
            address = request.POST.get('hospital_address', '').strip()
            if not name or not code or not address:
                messages.error(request, 'Hospital name, code, and address are required.')
                return redirect('hospital_admin_settings')
            if Hospital.objects.filter(code=code).exists():
                messages.error(request, 'A hospital with this code already exists.')
                return redirect('hospital_admin_settings')
            hospital = Hospital.objects.create(
                name=name,
                code=code,
                address=address,
                phone=request.POST.get('hospital_phone', '').strip(),
                email=request.POST.get('hospital_email', '').strip(),
                is_active=False,
            )
            request.user.hospital = hospital
            request.user.save(update_fields=['hospital'])

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
def _chat_members(user):
    if user.role == 'doctor':
        patient_codes = DoctorPatient.objects.filter(
            doctor=user,
        ).values_list('patient_id', flat=True)
        appointment_patient_ids = PatientAppointment.objects.filter(
            doctor=user,
        ).exclude(status='cancelled').values_list('patient_user_id', flat=True)
        return User.objects.filter(
            models.Q(
                patient_profile__patient_id__in=patient_codes,
            ) | models.Q(
                id__in=appointment_patient_ids,
            ),
            role='patient',
            is_active=True,
        ).exclude(id=user.id).order_by('first_name', 'last_name', 'username')

    appointment_doctor_ids = PatientAppointment.objects.filter(
        patient_user=user,
    ).exclude(status='cancelled').values_list('doctor_id', flat=True)
    return User.objects.filter(
        id__in=appointment_doctor_ids,
        role='doctor',
        is_active=True,
    ).exclude(id=user.id).order_by('first_name', 'last_name', 'username')


def _chat_hospital_id(user, recipient):
    if user.role == 'doctor':
        relation = DoctorPatient.objects.filter(
            doctor=user,
            patient_id=recipient.patient_profile.patient_id,
        ).first()
        if relation:
            return relation.hospital_id
        appointment = PatientAppointment.objects.filter(
            doctor=user,
            patient_user=recipient,
        ).first()
    else:
        appointment = PatientAppointment.objects.filter(
            patient_user=user,
            doctor=recipient,
        ).first()
    return appointment.hospital_id if appointment else recipient.hospital_id or user.hospital_id


@login_required(login_url='login')
def messages_view(request):
    if request.user.role not in ('doctor', 'patient'):
        return redirect('dashboard')

    user = request.user
    teammates = _chat_members(user)

    selected_id = request.GET.get('user')
    selected_user = teammates.filter(id=selected_id).first() if selected_id else None
    chat_messages = ChatMessage.objects.none()
    if selected_user:
        chat_messages = ChatMessage.objects.filter(
            models.Q(sender=user, recipient=selected_user) |
            models.Q(sender=selected_user, recipient=user)
        ).select_related('sender').order_by('created_at')

    return render(request, 'accounts/chat/messages.html', {
        'base_template': (
            'accounts/doctor/base.html'
            if user.role == 'doctor'
            else 'accounts/patient/base.html'
        ),
        'teammates': teammates,
        'selected_user': selected_user,
        'chat_messages': chat_messages,
        'websocket_url': f'/ws/messages/{selected_user.id}/' if selected_user else '',
        'search_placeholder': (
            'Search patients...' if user.role == 'doctor'
            else 'Search doctors...'
        ),
        'chat_partner_label': 'patient' if user.role == 'doctor' else 'doctor',
        'chat_hours': 'Messages are available from 10 AM to 6 PM.',
    })


@login_required(login_url='login')
def message_upload(request):
    if request.method != 'POST' or request.user.role not in ('doctor', 'patient'):
        return JsonResponse({'error': 'Invalid request.'}, status=400)

    recipient = _chat_members(request.user).filter(
        id=request.POST.get('recipient_id'),
    ).first()
    upload = request.FILES.get('attachment')
    if not recipient or not upload:
        return JsonResponse({'error': 'Recipient and attachment are required.'}, status=400)
    if upload.size > 10 * 1024 * 1024:
        return JsonResponse({'error': 'Files must be 10 MB or smaller.'}, status=400)

    message = ChatMessage.objects.create(
        hospital_id=_chat_hospital_id(request.user, recipient),
        sender=request.user,
        recipient=recipient,
        body='',
        attachment=upload,
        attachment_name=upload.name,
    )
    data = {
        'id': message.id,
        'body': '',
        'sender_id': message.sender_id,
        'sender_name': request.user.get_full_name() or request.user.username,
        'created_at': timezone.localtime(message.created_at).strftime(
            '%d %b %Y, %I:%M %p'
        ),
        'attachment_url': message.attachment.url,
        'attachment_name': message.attachment_name,
    }
    ids = sorted([request.user.id, recipient.id])
    async_to_sync(get_channel_layer().group_send)(
        f'chat_{ids[0]}_{ids[1]}',
        {'type': 'chat_message', 'message': data},
    )
    return JsonResponse(data)


@login_required(login_url='login')
def message_send(request):
    if request.method != 'POST' or request.user.role not in ('doctor', 'patient'):
        return JsonResponse({'error': 'Invalid request.'}, status=400)

    recipient = _chat_members(request.user).filter(
        id=request.POST.get('recipient_id'),
    ).first()
    body = request.POST.get('body', '').strip()
    if not recipient or not body:
        return JsonResponse({'error': 'Recipient and message are required.'}, status=400)
    if len(body) > 2000:
        return JsonResponse({'error': 'Messages must be 2000 characters or fewer.'}, status=400)

    message = ChatMessage.objects.create(
        hospital_id=_chat_hospital_id(request.user, recipient),
        sender=request.user,
        recipient=recipient,
        body=body,
    )
    data = {
        'id': message.id,
        'body': message.body,
        'sender_id': message.sender_id,
        'sender_name': request.user.get_full_name() or request.user.username,
        'created_at': timezone.localtime(message.created_at).strftime(
            '%d %b %Y, %I:%M %p'
        ),
        'attachment_url': '',
        'attachment_name': '',
    }
    ids = sorted([request.user.id, recipient.id])
    async_to_sync(get_channel_layer().group_send)(
        f'chat_{ids[0]}_{ids[1]}',
        {'type': 'chat_message', 'message': data},
    )
    return JsonResponse(data)


def _sync_doctor_appointments(doctor, hospital):
    """Make counter-approved appointments available to the doctor's screens."""
    if not hospital:
        return

    approved_appointments = PatientAppointment.objects.filter(
        doctor=doctor,
        hospital=hospital,
        status='approved',
    ).select_related('patient_user')

    for appointment in approved_appointments:
        patient_profile = Patient.objects.filter(
            user=appointment.patient_user,
            hospital=hospital,
        ).first()
        patient_id = (
            patient_profile.patient_id
            if patient_profile
            else f'PT-{appointment.patient_user_id:06d}'
        )
        gender = ''
        age = None
        if patient_profile:
            gender = dict(Patient.GENDER_CHOICES).get(
                patient_profile.gender,
                patient_profile.gender or '',
            )
            age = patient_profile.age

        patient, _ = DoctorPatient.objects.update_or_create(
            doctor=doctor,
            hospital=hospital,
            patient_id=patient_id,
            defaults={
                'patient_name': appointment.patient_name,
                'phone': appointment.patient_phone,
                'gender': gender,
                'age': age,
            },
        )

        DoctorSchedule.objects.get_or_create(
            doctor=doctor,
            hospital=hospital,
            patient_name=appointment.patient_name,
            patient_id=patient_id,
            schedule_date=appointment.appointment_date,
            start_time=appointment.appointment_time,
            defaults={
                'end_time': (
                    datetime.combine(
                        appointment.appointment_date,
                        appointment.appointment_time,
                    ) + timedelta(minutes=30)
                ).time(),
                'notes': appointment.reason,
                'status': 'scheduled',
            },
        )


def doctor_dashboard(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.user.role != 'doctor':
        return redirect('dashboard')

    doctor = request.user
    hospital = doctor.hospital
    _sync_doctor_appointments(doctor, hospital)
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
    _sync_doctor_appointments(doctor, hospital)

    if request.method == 'POST' and request.POST.get('action') == 'referral_status':
        referral = DoctorReferral.objects.filter(
            id=request.POST.get('referral_id'),
            specialist=doctor,
            patient__hospital=hospital,
        ).first()
        status = request.POST.get('status')
        if referral and status in ('accepted', 'declined'):
            referral.status = status
            referral.save(update_fields=['status', 'updated_at'])
        return redirect(f"{reverse('doctor_patient_summary')}?referrals=1")

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

    show_referrals = request.GET.get('referrals') == '1'
    referral_patients = DoctorReferral.objects.filter(
        specialist=doctor,
        patient__hospital=hospital,
    ).select_related('patient', 'doctor')

    all_patient_ids = set(patients.values_list('patient_id', flat=True))
    all_patient_ids.update(
        referral_patients.values_list('patient__patient_id', flat=True)
    )
    latest_vitals = {}
    if hospital and all_patient_ids:
        vital_records = VitalSign.objects.filter(
            hospital=hospital,
            patient__hospital=hospital,
            patient__patient_id__in=all_patient_ids,
        ).select_related('patient').order_by('-recorded_at')
        for vital in vital_records:
            latest_vitals.setdefault(vital.patient.patient_id, vital)

    for patient in patients:
        patient.latest_vital = latest_vitals.get(patient.patient_id)
    for referral in referral_patients:
        referral.patient.latest_vital = latest_vitals.get(
            referral.patient.patient_id
        )

    context = {
        'doctor': doctor,
        'hospital': hospital,
        'patients': patients,
        'total_patients': total_patients,
        'male_patients': male_patients,
        'female_patients': female_patients,
        'today_patients': today_patients,
        'today_patient_ids': today_patient_ids,
        'search': search,
        'show_referrals': show_referrals,
        'referral_patients': referral_patients,
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
    _sync_doctor_appointments(doctor, hospital)

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
    _sync_doctor_appointments(doctor, hospital)

    patients = DoctorPatient.objects.filter(
        doctor=doctor,
        hospital=hospital
    )

    specialists = request.user.__class__.objects.filter(
        role='doctor',
        is_active=True,
        hospital=hospital
    ).exclude(
        id=doctor.id
    ).select_related('hospital', 'staff_profile')

    specialist_department_labels = {}
    if hospital:
        specialist_department_labels = {
            dept.name: dept.get_name_display()
            for dept in Department.objects.filter(hospital=hospital)
        }
    for specialist in specialists:
        staff_profile = getattr(specialist, 'staff_profile', None)
        if staff_profile:
            staff_profile.department_label = specialist_department_labels.get(
                staff_profile.department,
                staff_profile.get_department_display()
            )

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
                is_active=True,
                hospital=hospital
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
                    is_active=True,
                    hospital=hospital
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
    _sync_doctor_appointments(doctor, hospital)

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
        action = request.POST.get('action')

        if action == 'remove_photo':
            profile.profile_image.delete(save=True)
            profile.profile_image = None
            profile.save()
            messages.success(request, 'Profile photo removed successfully.')
            return redirect('doctor_profile')

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
def _sync_nurse_patients(hospital):
    if not hospital:
        return Patient.objects.none()

    appointment_users = User.objects.filter(
        my_appointments__hospital=hospital
    ).distinct()

    for patient_user in appointment_users:
        patient, created = Patient.objects.get_or_create(
            user=patient_user,
            defaults={
                'hospital': hospital,
                'patient_id': f'PT-{patient_user.id:06d}',
            }
        )
        if not created and patient.hospital_id != hospital.id:
            patient.hospital = hospital
            patient.save(update_fields=['hospital', 'updated_at'])

    return Patient.objects.filter(
        hospital=hospital
    ).select_related('user').order_by('-created_at')


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
        patients = _sync_nurse_patients(hospital)
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
        recent_patients = _sync_nurse_patients(hospital)[:6]

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
    patients = _sync_nurse_patients(hospital)

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
    patients = _sync_nurse_patients(hospital)

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
    patients = _sync_nurse_patients(hospital)

    search = request.GET.get('search', '').strip()
    if search:
        patients = patients.filter(
            models.Q(user__first_name__icontains=search) |
            models.Q(user__last_name__icontains=search) |
            models.Q(user__email__icontains=search) |
            models.Q(user__phone__icontains=search) |
            models.Q(patient_id__icontains=search) |
            models.Q(user__username__icontains=search)
        )

    today = timezone.now().date()
    total = patients.count()
    today_count = patients.filter(created_at__date=today).count()

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
    total_hospitals = 0
    upcoming_appointments = 0
    completed_appointments = 0
    recent_appointments = []
    notices = []

    total_hospitals = Hospital.objects.filter(is_active=True).count()
    total_doctors = User.objects.filter(
        role='doctor',
        is_active=True
    ).count()

    department_queryset = Department.objects.filter(is_active=True)
    if hospital:
        department_queryset = department_queryset.filter(hospital=hospital)
    total_departments = department_queryset.count()

    if hospital:
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
        'total_hospitals': total_hospitals,
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

    departments = Department.objects.filter(
        is_active=True
    )
    if hospital:
        departments = departments.filter(hospital=hospital)
    departments = departments.order_by('name')
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

    doctors = User.objects.filter(
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

    doctors = User.objects.filter(
        role='doctor',
        is_active=True
    ).order_by('first_name', 'last_name')

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'book':
            doctor_id = request.POST.get('doctor')
            hospital_id = request.POST.get('hospital')
            appt_date = request.POST.get('appointment_date')
            appt_time = request.POST.get('appointment_time')
            reason = request.POST.get('reason', '').strip()
            amount = request.POST.get('amount') or 500
            pay_now = request.POST.get('pay_now') == 'on'

            if not (doctor_id and appt_date and appt_time):
                messages.error(request, 'Please fill all required fields.')
                return redirect('patient_appointments')

            doctor = get_object_or_404(User, id=doctor_id)
            selected_hospital = doctor.hospital if not hospital_id else get_object_or_404(Hospital, id=hospital_id)

            PatientAppointment.objects.create(
                hospital=selected_hospital,
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

    hospitals = Hospital.objects.filter(is_active=True).order_by('name')
    departments = Department.objects.filter(is_active=True).order_by('name')

    context = {
        'hospital': hospital,
        'doctors': doctors,
        'hospitals': hospitals,
        'departments': departments,
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
from decimal import Decimal, InvalidOperation
def patient_payments(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'patient':
        return redirect('dashboard')

    user = request.user
    hospital = user.hospital
    hospitals = Hospital.objects.filter(is_active=True).order_by('name')

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

            try:
                amount = Decimal(str(amount))
            except (InvalidOperation, TypeError, ValueError):
                messages.error(request, 'Enter a valid payment amount.')
                return redirect('patient_payments')

            if amount <= 0:
                messages.error(request, 'Payment amount must be greater than zero.')
                return redirect('patient_payments')

            if appointment_id:
                appointment = PatientAppointment.objects.filter(
                    id=appointment_id,
                    patient_user=user,
                    payment_status='pending'
                ).exclude(status='cancelled').select_related('hospital').first()
                if not appointment:
                    messages.error(request, 'The selected appointment is not available for payment.')
                    return redirect('patient_payments')
                payment_hospital = appointment.hospital
            else:
                hospital_id = request.POST.get('hospital_id')
                payment_hospital = hospitals.filter(id=hospital_id).first()
                if not payment_hospital:
                    messages.error(request, 'Select a hospital for this payment.')
                    return redirect('patient_payments')

            PatientPayment.objects.create(
                hospital=payment_hospital,
                patient_user=user,
                appointment=appointment if appointment_id else None,
                amount=amount,
                purpose=purpose,
                method=method,
                transaction_id=transaction_id,
                note=note,
                status='paid'
            )

            if appointment_id:
                appointment.payment_status = 'paid'
                appointment.save(update_fields=['payment_status', 'updated_at'])

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
        'hospitals': hospitals,
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
from .models import MedicalRecord, DiagnosticTest
def lab_dashboard(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'lab':
        return redirect('dashboard')

    hospital = request.user.hospital
    today = timezone.now().date()
    week_ago = today - timedelta(days=6)

    patients_count = 0
    total_reports = 0
    today_reports = 0
    week_reports = 0
    total_tests = 0
    recent_reports = []
    daily_labels = []
    daily_data = []

    if hospital:
        patients_count = Patient.objects.filter(hospital=hospital).count()
        reports = MedicalRecord.objects.filter(hospital=hospital)
        total_reports = reports.count()
        today_reports = reports.filter(created_at__date=today).count()
        week_reports = reports.filter(created_at__date__gte=week_ago).count()
        recent_reports = reports.select_related('uploaded_by').order_by('-created_at')[:6]

        try:
            total_tests = DiagnosticTest.objects.filter(hospital=hospital, is_active=True).count()
        except Exception:
            total_tests = 0

        for i in range(6, -1, -1):
            day = today - timedelta(days=i)
            daily_labels.append(day.strftime('%a'))
            daily_data.append(reports.filter(created_at__date=day).count())

    pending_blood_tests = BloodTestRequest.objects.filter(hospital=hospital, lab_status='pending').count() if hospital else 0
    recent_blood_tests = BloodTestRequest.objects.filter(hospital=hospital).order_by('-created_at')[:5] if hospital else []

    context = {
        'hospital': hospital,
        'user': request.user,
        'patients_count': patients_count,
        'total_reports': total_reports,
        'today_reports': today_reports,
        'week_reports': week_reports,
        'total_tests': total_tests,
        'recent_reports': recent_reports,
        'daily_labels': json.dumps(daily_labels),
        'daily_data': json.dumps(daily_data),
        'today': today,
        'pending_blood_tests': pending_blood_tests,
        'recent_blood_tests': recent_blood_tests,
    }
    return render(request, 'accounts/lab/dashboard.html', context)

from .models import MedicalRecord, DiagnosticTest
def lab_upload_report(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'lab':
        return redirect('dashboard')

    hospital = request.user.hospital
    search = request.GET.get('q', '').strip()
    patients = Patient.objects.filter(hospital=hospital).select_related('user').order_by('user__first_name') if hospital else Patient.objects.none()
    tests = DiagnosticTest.objects.filter(hospital=hospital, is_active=True).order_by('name') if hospital else DiagnosticTest.objects.none()

    if request.method == 'POST':
        action = request.POST.get('action', 'upload')

        if action == 'delete':
            MedicalRecord.objects.filter(id=request.POST.get('report_id'), hospital=hospital).delete()
            messages.success(request, 'Report deleted.')
            return redirect('lab_upload_report')

        if action == 'edit':
            report = get_object_or_404(MedicalRecord, id=request.POST.get('report_id'), hospital=hospital)
            report.title = request.POST.get('title', '').strip()
            report.record_type = request.POST.get('record_type', 'lab')
            report.test_name = request.POST.get('test_name', '').strip()
            report.notes = request.POST.get('notes', '').strip()
            report.status = request.POST.get('status', report.status)
            report_date = request.POST.get('report_date')
            report.report_date = report_date if report_date else None

            patient_id = request.POST.get('patient')
            if patient_id:
                p = Patient.objects.filter(id=patient_id, hospital=hospital).select_related('user').first()
                if p:
                    if p.user:
                        report.patient_name = p.user.get_full_name() or p.user.username
                        report.patient_phone = p.user.phone or ''
                        report.patient_user = p.user
                    report.patient_id = p.patient_id or ''
            else:
                if request.POST.get('patient_name', '').strip():
                    report.patient_name = request.POST.get('patient_name', '').strip()
                if request.POST.get('patient_phone', '').strip():
                    report.patient_phone = request.POST.get('patient_phone', '').strip()
                if request.POST.get('patient_code', '').strip():
                    report.patient_id = request.POST.get('patient_code', '').strip()

            if request.FILES.get('file'):
                report.file = request.FILES['file']

            report.save()
            messages.success(request, 'Report updated.')
            return redirect('lab_upload_report')

        title = request.POST.get('title', '').strip()
        record_type = request.POST.get('record_type', 'lab')
        test_name = request.POST.get('test_name', '').strip()
        notes = request.POST.get('notes', '').strip()
        status = request.POST.get('status', 'pending')
        report_date = request.POST.get('report_date') or None
        file = request.FILES.get('file')
        patient_id = request.POST.get('patient')

        if not hospital:
            messages.error(request, 'No hospital assigned.')
            return redirect('lab_upload_report')
        if not title or not file:
            messages.error(request, 'Title and file are required.')
            return redirect('lab_upload_report')

        patient_name = ''
        patient_phone = ''
        patient_code = ''
        patient_user = None

        if patient_id:
            p = Patient.objects.filter(id=patient_id, hospital=hospital).select_related('user').first()
            if p:
                if p.user:
                    patient_name = p.user.get_full_name() or p.user.username
                    patient_phone = p.user.phone or ''
                    patient_user = p.user
                patient_code = p.patient_id or ''

        if not patient_name:
            patient_name = request.POST.get('patient_name', '').strip()
            patient_phone = request.POST.get('patient_phone', '').strip()
            patient_code = request.POST.get('patient_code', '').strip()

        MedicalRecord.objects.create(
            hospital=hospital,
            patient_user=patient_user,
            patient_name=patient_name,
            patient_id=patient_code,
            patient_phone=patient_phone,
            title=title,
            record_type=record_type,
            test_name=test_name,
            file=file,
            notes=notes,
            status=status,
            uploaded_by=request.user,
            report_date=report_date
        )
        messages.success(request, 'Report uploaded successfully.')
        return redirect('lab_upload_report')

    reports = MedicalRecord.objects.none()
    if hospital:
        reports = MedicalRecord.objects.filter(hospital=hospital).select_related('uploaded_by').order_by('-created_at')
        if search:
            reports = reports.filter(
                Q(title__icontains=search) |
                Q(patient_name__icontains=search) |
                Q(patient_id__icontains=search) |
                Q(test_name__icontains=search)
            )

    context = {
        'hospital': hospital,
        'patients': patients,
        'tests': tests,
        'reports': reports,
        'total': reports.count(),
        'pending_count': reports.filter(status='pending').count() if hospital else 0,
        'search': search,
        'record_type_choices': MedicalRecord.RECORD_TYPE_CHOICES,
        'status_choices': MedicalRecord.STATUS_CHOICES,
        'today': timezone.now().date(),
    }
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
    records = MedicalRecord.objects.filter(hospital=hospital, record_type='lab') if hospital else MedicalRecord.objects.none()

    status_filter = request.GET.get('status', 'all').lower()
    search_query = request.GET.get('q', '').strip()

    if status_filter in ['verified', 'pending']:
        records = records.filter(status=status_filter)

    if search_query:
        records = records.filter(
            models.Q(test_name__icontains=search_query) |
            models.Q(title__icontains=search_query) |
            models.Q(patient_name__icontains=search_query) |
            models.Q(patient_id__icontains=search_query)
        )

    context = {
        'records': records,
        'status_filter': status_filter,
        'search_query': search_query,
        'total_count': MedicalRecord.objects.filter(hospital=hospital, record_type='lab').count() if hospital else 0,
        'verified_count': MedicalRecord.objects.filter(hospital=hospital, record_type='lab', status='verified').count() if hospital else 0,
        'pending_count': MedicalRecord.objects.filter(hospital=hospital, record_type='lab', status='pending').count() if hospital else 0,
    }

    return render(request, 'accounts/lab/lab_history.html', context)

def lab_profile(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'lab':
        return redirect('dashboard')

    user = request.user
    hospital = user.hospital

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'update':
            user.first_name = request.POST.get('first_name', '').strip()
            user.last_name = request.POST.get('last_name', '').strip()
            user.email = request.POST.get('email', '').strip()
            user.phone = request.POST.get('phone', '').strip()
            user.save()

            return redirect('lab_profile')

    context = {
        'user': user,
        'hospital': hospital,
    }

    return render(request, 'accounts/lab/profile.html', context)
# Counter
from .models import PatientAppointment, PatientPayment
@login_required(login_url='login')
def counter_dashboard(request):
    if request.user.role != 'counter':
        return redirect('dashboard')

    today = timezone.localdate()
    hospital = request.user.hospital
    User = get_user_model()

    if hospital:
        patients = Patient.objects.filter(hospital=hospital)
        appointments = PatientAppointment.objects.filter(hospital=hospital)
        doctors = User.objects.filter(
            hospital=hospital,
            role='doctor',
            is_active=True
        )
        payments = PatientPayment.objects.filter(
            hospital=hospital,
            created_at__date=today,
            status__in=['paid', 'verified']
        )
    else:
        patients = Patient.objects.none()
        appointments = PatientAppointment.objects.none()
        doctors = User.objects.none()
        payments = PatientPayment.objects.none()

    today_appointments = appointments.filter(
        appointment_date=today
    ).select_related('doctor').order_by('appointment_time')

    appointment_rows = []

    for appointment in today_appointments:
        doctor = appointment.doctor

        doctor_name = doctor.get_full_name() or doctor.username

        status_labels = {
            'pending': 'Waiting',
            'approved': 'Confirmed',
            'confirmed': 'Confirmed',
            'rejected': 'Rejected',
            'completed': 'Completed',
            'cancelled': 'Cancelled',
        }

        appointment_rows.append({
            'patient_name': appointment.patient_name,
            'doctor_name': doctor_name,
            'time': appointment.appointment_time,
            'status': status_labels.get(
                appointment.status,
                appointment.get_status_display()
            ),
            'status_value': appointment.status,
        })

    context = {
        'total_patients': patients.count(),
        'today_appointments_count': today_appointments.count(),
        'available_doctors': doctors.count(),
        'today_collection': payments.aggregate(
            total=Sum('amount')
        )['total'] or 0,
        'today_appointments': appointment_rows,
    }

    return render(
        request,
        'accounts/counter/dashboard.html',
        context
    )
def counter_patients(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'counter':
        return redirect('dashboard')
    hospital = request.user.hospital
    patients = Patient.objects.filter(hospital=hospital) if hospital else []
    context = {'patients': patients}
    return render(request, 'accounts/counter/patients.html', context)

@login_required(login_url='login')
def counter_appointments(request):
    if request.user.role != 'counter':
        return redirect('dashboard')

    hospital = request.user.hospital

    if not hospital:
        appointments = PatientAppointment.objects.none()
    else:
        appointments = PatientAppointment.objects.filter(
            hospital=hospital
        ).select_related('doctor').order_by(
            '-appointment_date',
            '-appointment_time'
        )

    if request.method == 'POST':
        appointment_id = request.POST.get('appointment_id')
        action = request.POST.get('action')

        if not hospital:
            return redirect('counter_appointments')

        appointment = get_object_or_404(
            PatientAppointment,
            id=appointment_id,
            hospital=hospital
        )

        if action == 'approve' and appointment.status == 'pending':
            appointment.status = 'approved'
            appointment.save(update_fields=['status'])

        elif action == 'reject' and appointment.status == 'pending':
            appointment.status = 'rejected'
            appointment.save(update_fields=['status'])

        return redirect('counter_appointments')

    context = {
        'appointments': appointments,
        'total_appointments': appointments.count(),
        'pending_appointments': appointments.filter(status='pending').count(),
        'approved_appointments': appointments.filter(status='approved').count(),
        'rejected_appointments': appointments.filter(status='rejected').count(),
    }

    return render(
        request,
        'accounts/counter/appointments.html',
        context
    )

@login_required(login_url='login')
def counter_doctors(request):
    if request.user.role != 'counter':
        return redirect('dashboard')

    hospital = request.user.hospital

    if hospital:
        doctors = Staff.objects.filter(
            hospital=hospital,
            user__role='doctor'
        ).select_related('user').order_by('user__first_name', 'user__last_name')
    else:
        doctors = Staff.objects.none()

    departments = doctors.values_list('department', flat=True).distinct()
    total_departments = Department.objects.filter(
        hospital=hospital
    ).count() if hospital else 0

    context = {
        'doctors': doctors,
        'total_doctors': doctors.count(),
        'active_doctors': doctors.filter(is_active=True).count(),
        'inactive_doctors': doctors.filter(is_active=False).count(),
        'total_departments': total_departments,
        'departments': departments,
    }

    return render(request, 'accounts/counter/doctors.html', context)

@login_required(login_url='login')
def counter_billing(request):
    if request.user.role != 'counter':
        return redirect('dashboard')

    hospital = request.user.hospital

    if hospital:
        patients = Patient.objects.filter(hospital=hospital)
        payments = PatientPayment.objects.filter(hospital=hospital).order_by('-created_at')
    else:
        patients = Patient.objects.none()
        payments = PatientPayment.objects.none()

    paid_payments = payments.filter(status__in=['paid', 'verified'])
    pending_payments = payments.filter(status='pending')

    context = {
        'patients': patients,
        'payments': payments,
        'total_payments': payments.count(),
        'paid_payments_count': paid_payments.count(),
        'pending_payments_count': pending_payments.count(),
        'total_revenue': paid_payments.aggregate(total=Sum('amount'))['total'] or 0,
    }

    return render(request, 'accounts/counter/billing.html', context)

def counter_notices(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'counter':
        return redirect('dashboard')
    return render(request, 'accounts/counter/notices.html')


@login_required(login_url='login')
def counter_profile(request):
    if request.user.role != 'counter':
        return redirect('dashboard')

    user = request.user
    staff = Staff.objects.filter(user=user).first()

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'update':
            user.first_name = request.POST.get('first_name', '').strip()
            user.last_name = request.POST.get('last_name', '').strip()
            user.email = request.POST.get('email', '').strip()
            user.phone = request.POST.get('phone', '').strip()
            user.save()

            if staff:
                staff.qualification = request.POST.get('qualification', '').strip()
                staff.save(update_fields=['qualification'])

            return redirect('counter_profile')

    context = {
        'profile': staff,
        'user': user,
        'hospital': user.hospital,
    }

    return render(request, 'accounts/counter/profile.html', context)

#blood bank
from .models import Blood
def bloodbank_dashboard(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'bloodbank':
        return redirect('dashboard')

    hospital = request.user.hospital
    today = timezone.now().date()

    total_donors = 0
    total_units = 0
    pending_requests = 0
    today_collection = 0
    inventory = []
    recent_requests = []

    if hospital:
        blood_qs = Blood.objects.filter(hospital=hospital)
        total_units = blood_qs.aggregate(total=Sum('units'))['total'] or 0
        total_donors = blood_qs.exclude(donor_name='').values('donor_name').distinct().count()
        today_collection = blood_qs.filter(collection_date=today).count()

        try:
            from .models import BloodRequest
            pending_requests = BloodRequest.objects.filter(
                hospital=hospital,
                status='pending'
            ).count()
            recent_requests = BloodRequest.objects.filter(
                hospital=hospital
            ).order_by('-created_at')[:5]
        except Exception:
            pending_requests = 0
            recent_requests = []

        groups = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
        labels = {
            'A+': 'A Positive', 'A-': 'A Negative',
            'B+': 'B Positive', 'B-': 'B Negative',
            'AB+': 'AB Positive', 'AB-': 'AB Negative',
            'O+': 'O Positive', 'O-': 'O Negative',
        }
        for g in groups:
            units = blood_qs.filter(blood_group=g).aggregate(t=Sum('units'))['t'] or 0
            reorder = blood_qs.filter(blood_group=g).aggregate(r=Sum('reorder_level'))['r'] or 5
            if units == 0:
                status = 'critical'
                status_label = 'Critical'
            elif units <= reorder:
                status = 'low'
                status_label = 'Low'
            else:
                status = 'available'
                status_label = 'Available'
            inventory.append({
                'group': g,
                'label': labels[g],
                'units': units,
                'status': status,
                'status_label': status_label,
            })

    total_blood_tests = BloodTestRequest.objects.filter(hospital=hospital).count() if hospital else 0
    pending_blood_tests = BloodTestRequest.objects.filter(hospital=hospital, lab_status='pending').count() if hospital else 0
    completed_blood_tests = BloodTestRequest.objects.filter(hospital=hospital, lab_status='completed').count() if hospital else 0
    recent_blood_tests = BloodTestRequest.objects.filter(hospital=hospital).order_by('-created_at')[:5] if hospital else []

    context = {
        'hospital': hospital,
        'user': request.user,
        'total_donors': total_donors,
        'total_units': total_units,
        'pending_requests': pending_requests,
        'today_collection': today_collection,
        'inventory': inventory,
        'recent_requests': recent_requests,
        'total_blood_tests': total_blood_tests,
        'pending_blood_tests': pending_blood_tests,
        'completed_blood_tests': completed_blood_tests,
        'recent_blood_tests': recent_blood_tests,
    }
    return render(request, 'accounts/bloodbank/dashboard.html', context)

from .models import BloodDonor
def bloodbank_donors(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'bloodbank':
        return redirect('dashboard')

    hospital = request.user.hospital
    search = request.GET.get('q', '').strip()

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'create':
            BloodDonor.objects.create(
                hospital=hospital,
                name=request.POST.get('name', '').strip(),
                phone=request.POST.get('phone', '').strip(),
                email=request.POST.get('email', '').strip(),
                gender=request.POST.get('gender', ''),
                blood_group=request.POST.get('blood_group', 'O+'),
                date_of_birth=request.POST.get('date_of_birth') or None,
                address=request.POST.get('address', '').strip(),
                last_donation=request.POST.get('last_donation') or None,
                total_donations=int(request.POST.get('total_donations') or 0),
                status=request.POST.get('status', 'active'),
                notes=request.POST.get('notes', '').strip(),
            )
            messages.success(request, 'Donor added successfully.')
            return redirect('bloodbank_donors')

        if action == 'edit':
            donor = get_object_or_404(BloodDonor, id=request.POST.get('donor_id'), hospital=hospital)
            donor.name = request.POST.get('name', '').strip()
            donor.phone = request.POST.get('phone', '').strip()
            donor.email = request.POST.get('email', '').strip()
            donor.gender = request.POST.get('gender', '')
            donor.blood_group = request.POST.get('blood_group', 'O+')
            donor.date_of_birth = request.POST.get('date_of_birth') or None
            donor.address = request.POST.get('address', '').strip()
            donor.last_donation = request.POST.get('last_donation') or None
            donor.total_donations = int(request.POST.get('total_donations') or 0)
            donor.status = request.POST.get('status', 'active')
            donor.notes = request.POST.get('notes', '').strip()
            donor.save()
            messages.success(request, 'Donor updated successfully.')
            return redirect('bloodbank_donors')

        if action == 'delete':
            BloodDonor.objects.filter(id=request.POST.get('donor_id'), hospital=hospital).delete()
            messages.success(request, 'Donor deleted.')
            return redirect('bloodbank_donors')

    donors = BloodDonor.objects.none()
    if hospital:
        donors = BloodDonor.objects.filter(hospital=hospital)
        if search:
            donors = donors.filter(
                Q(name__icontains=search) |
                Q(phone__icontains=search) |
                Q(blood_group__icontains=search) |
                Q(email__icontains=search)
            )

    context = {
        'hospital': hospital,
        'donors': donors,
        'total': donors.count(),
        'active_count': donors.filter(status='active').count() if hospital else 0,
        'search': search,
        'blood_group_choices': BloodDonor.BLOOD_GROUP_CHOICES,
        'gender_choices': BloodDonor.GENDER_CHOICES,
        'status_choices': BloodDonor.STATUS_CHOICES,
    }
    return render(request, 'accounts/bloodbank/donors.html', context)



def bloodbank_inventory(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'bloodbank':
        return redirect('dashboard')

    hospital = request.user.hospital
    search = request.GET.get('q', '').strip()

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'create':
            Blood.objects.create(
                hospital=hospital,
                blood_group=request.POST.get('blood_group', 'O+'),
                component=request.POST.get('component', 'whole'),
                units=int(request.POST.get('units') or 0),
                reorder_level=int(request.POST.get('reorder_level') or 5),
                expiry_date=request.POST.get('expiry_date') or None,
                bag_number=request.POST.get('bag_number', '').strip(),
                donor_name=request.POST.get('donor_name', '').strip(),
                collection_date=request.POST.get('collection_date') or None,
                notes=request.POST.get('notes', '').strip(),
            )
            messages.success(request, 'Blood unit added to inventory.')
            return redirect('bloodbank_inventory')

        if action == 'edit':
            item = get_object_or_404(Blood, id=request.POST.get('blood_id'), hospital=hospital)
            item.blood_group = request.POST.get('blood_group', 'O+')
            item.component = request.POST.get('component', 'whole')
            item.units = int(request.POST.get('units') or 0)
            item.reorder_level = int(request.POST.get('reorder_level') or 5)
            item.expiry_date = request.POST.get('expiry_date') or None
            item.bag_number = request.POST.get('bag_number', '').strip()
            item.donor_name = request.POST.get('donor_name', '').strip()
            item.collection_date = request.POST.get('collection_date') or None
            item.notes = request.POST.get('notes', '').strip()
            item.save()
            messages.success(request, 'Inventory updated.')
            return redirect('bloodbank_inventory')

        if action == 'delete':
            Blood.objects.filter(id=request.POST.get('blood_id'), hospital=hospital).delete()
            messages.success(request, 'Record deleted.')
            return redirect('bloodbank_inventory')

    items = Blood.objects.none()
    total_units = 0
    low_count = 0
    group_summary = []

    if hospital:
        items = Blood.objects.filter(hospital=hospital).order_by('blood_group', '-created_at')
        if search:
            items = items.filter(
                Q(blood_group__icontains=search) |
                Q(bag_number__icontains=search) |
                Q(donor_name__icontains=search) |
                Q(component__icontains=search)
            )
        total_units = Blood.objects.filter(hospital=hospital).aggregate(t=Sum('units'))['t'] or 0

        for g, label in Blood.BLOOD_GROUP_CHOICES:
            units = Blood.objects.filter(hospital=hospital, blood_group=g).aggregate(t=Sum('units'))['t'] or 0
            blood_records = Blood.objects.filter(hospital=hospital, blood_group=g)
            if blood_records.exists():
                avg_reorder = blood_records.aggregate(r=Sum('reorder_level'))['r'] / blood_records.count()
            else:
                avg_reorder = 5
            if units == 0:
                status, status_label = 'critical', 'Critical'
            elif units <= max(avg_reorder, 5):
                status, status_label = 'low', 'Low'
                low_count += 1
            else:
                status, status_label = 'available', 'Available'
            group_summary.append({
                'group': g,
                'label': label,
                'units': units,
                'status': status,
                'status_label': status_label,
            })

    context = {
        'hospital': hospital,
        'items': items,
        'total_units': total_units,
        'total_records': items.count(),
        'low_count': low_count,
        'group_summary': group_summary,
        'search': search,
        'blood_group_choices': Blood.BLOOD_GROUP_CHOICES,
        'component_choices': Blood.COMPONENT_CHOICES,
    }
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
    search = request.GET.get('q', '').strip()
    donors = BloodDonor.objects.filter(hospital=hospital, status='active') if hospital else BloodDonor.objects.none()

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'create':
            donor_id = request.POST.get('donor')
            donor = None
            donor_name = request.POST.get('donor_name', '').strip()
            donor_phone = request.POST.get('donor_phone', '').strip()
            blood_group = request.POST.get('blood_group', 'O+')

            if donor_id:
                donor = BloodDonor.objects.filter(id=donor_id, hospital=hospital).first()
                if donor:
                    donor_name = donor.name
                    donor_phone = donor.phone
                    blood_group = donor.blood_group

            collection = BloodCollection.objects.create(
                hospital=hospital,
                donor=donor,
                donor_name=donor_name,
                donor_phone=donor_phone,
                blood_group=blood_group,
                component=request.POST.get('component', 'whole'),
                units=int(request.POST.get('units') or 1),
                bag_number=request.POST.get('bag_number', '').strip(),
                collection_date=request.POST.get('collection_date') or timezone.now().date(),
                expiry_date=request.POST.get('expiry_date') or None,
                test_status=request.POST.get('test_status', 'pending'),
                issue_status='in_stock',
                notes=request.POST.get('notes', '').strip(),
                collected_by=request.user,
            )

            if donor:
                donor.total_donations = (donor.total_donations or 0) + 1
                donor.last_donation = collection.collection_date
                donor.save()

            if collection.test_status == 'passed':
                Blood.objects.create(
                    hospital=hospital,
                    blood_group=collection.blood_group,
                    component=collection.component,
                    units=collection.units,
                    bag_number=collection.bag_number,
                    donor_name=collection.donor_name,
                    collection_date=collection.collection_date,
                    expiry_date=collection.expiry_date,
                    notes=f'From collection {collection.bag_number}',
                )

            messages.success(request, 'Collection recorded.')
            return redirect('bloodbank_collection')

        if action == 'edit':
            c = get_object_or_404(BloodCollection, id=request.POST.get('collection_id'), hospital=hospital)
            c.donor_name = request.POST.get('donor_name', '').strip()
            c.donor_phone = request.POST.get('donor_phone', '').strip()
            c.blood_group = request.POST.get('blood_group', 'O+')
            c.component = request.POST.get('component', 'whole')
            c.units = int(request.POST.get('units') or 1)
            c.bag_number = request.POST.get('bag_number', '').strip()
            c.collection_date = request.POST.get('collection_date') or c.collection_date
            c.expiry_date = request.POST.get('expiry_date') or None
            c.test_status = request.POST.get('test_status', c.test_status)
            c.issue_status = request.POST.get('issue_status', c.issue_status)
            c.issued_to = request.POST.get('issued_to', '').strip()
            c.notes = request.POST.get('notes', '').strip()
            c.save()
            messages.success(request, 'Collection updated.')
            return redirect('bloodbank_collection')

        if action == 'pass_test':
            c = get_object_or_404(BloodCollection, id=request.POST.get('collection_id'), hospital=hospital)
            if c.test_status != 'passed':
                c.test_status = 'passed'
                c.save()
                Blood.objects.create(
                    hospital=hospital,
                    blood_group=c.blood_group,
                    component=c.component,
                    units=c.units,
                    bag_number=c.bag_number,
                    donor_name=c.donor_name,
                    collection_date=c.collection_date,
                    expiry_date=c.expiry_date,
                    notes=f'From collection {c.bag_number}',
                )
            messages.success(request, 'Test passed. Added to inventory.')
            return redirect('bloodbank_collection')

        if action == 'fail_test':
            BloodCollection.objects.filter(id=request.POST.get('collection_id'), hospital=hospital).update(test_status='failed', issue_status='discarded')
            messages.success(request, 'Test failed. Marked discarded.')
            return redirect('bloodbank_collection')

        if action == 'issue':
            c = get_object_or_404(BloodCollection, id=request.POST.get('collection_id'), hospital=hospital)
            c.issue_status = 'issued'
            c.issued_to = request.POST.get('issued_to', '').strip()
            c.save()
            Blood.objects.filter(hospital=hospital, bag_number=c.bag_number).update(units=0)
            messages.success(request, 'Blood issued.')
            return redirect('bloodbank_collection')

        if action == 'delete':
            BloodCollection.objects.filter(id=request.POST.get('collection_id'), hospital=hospital).delete()
            messages.success(request, 'Collection deleted.')
            return redirect('bloodbank_collection')

    collections = BloodCollection.objects.none()
    if hospital:
        collections = BloodCollection.objects.filter(hospital=hospital)
        if search:
            collections = collections.filter(
                Q(donor_name__icontains=search) |
                Q(bag_number__icontains=search) |
                Q(blood_group__icontains=search)
            )

    context = {
        'hospital': hospital,
        'collections': collections,
        'donors': donors,
        'total': collections.count(),
        'pending_test': collections.filter(test_status='pending').count() if hospital else 0,
        'today_count': collections.filter(collection_date=timezone.now().date()).count() if hospital else 0,
        'search': search,
        'blood_group_choices': BloodCollection.BLOOD_GROUP_CHOICES,
        'component_choices': BloodCollection.COMPONENT_CHOICES,
        'test_status_choices': BloodCollection.TEST_STATUS_CHOICES,
        'issue_status_choices': BloodCollection.ISSUE_STATUS_CHOICES,
        'today': timezone.now().date(),
    }
    return render(request, 'accounts/bloodbank/collection.html', context)



from .models import BloodTestRequest

def bloodbank_testing(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'bloodbank' and request.user.role != 'hospital_admin':
        return redirect('dashboard')

    hospital = request.user.hospital

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'apply_test':
            patient_id = request.POST.get('patient')
            patient = None
            if patient_id:
                patient = Patient.objects.filter(id=patient_id, hospital=hospital).first()

            patient_name = request.POST.get('patient_name', '').strip()
            if not patient_name and patient:
                patient_name = patient.patient_name

            patient_phone = request.POST.get('patient_phone', '').strip()
            if not patient_phone and patient:
                patient_phone = patient.phone

            patient_gender = request.POST.get('gender', 'M')
            if patient and patient.gender:
                patient_gender = patient.gender

            age_val = request.POST.get('age')
            patient_age = int(age_val) if age_val and age_val.isdigit() else (patient.age if patient else None)

            blood_group = request.POST.get('blood_group', '').strip()
            if not blood_group and patient and patient.blood_group:
                blood_group = patient.blood_group

            test_id = request.POST.get('test_id')
            test = None
            test_name = ''
            if test_id:
                test = DiagnosticTest.objects.filter(id=test_id, hospital=hospital).first()
                if test:
                    test_name = test.name
            if not test_name:
                test_name = request.POST.get('test_name', 'Blood Test').strip()

            amount_str = request.POST.get('amount') or '0'
            try:
                from decimal import Decimal
                amount = Decimal(amount_str)
            except Exception:
                amount = Decimal(test.price if test else 0)

            payment_method = request.POST.get('payment_method', 'cash')
            payment_reference = request.POST.get('payment_reference', '').strip()
            priority = request.POST.get('priority', 'normal')
            doctor_name = request.POST.get('doctor_name', '').strip()
            notes = request.POST.get('notes', '').strip()

            # 1. Create BloodTestRequest
            blood_test = BloodTestRequest.objects.create(
                hospital=hospital,
                patient=patient,
                patient_name=patient_name,
                patient_phone=patient_phone,
                patient_gender=patient_gender,
                patient_age=patient_age,
                blood_group=blood_group,
                test=test,
                test_name=test_name,
                priority=priority,
                doctor_name=doctor_name,
                notes=notes,
                amount=amount,
                payment_method=payment_method,
                payment_status='paid',
                payment_reference=payment_reference,
                lab_status='pending',
                requested_by=request.user,
            )

            # 2. Integrate with Hospital Accountant: Create Billing entry
            billing = Billing.objects.create(
                hospital=hospital,
                patient=patient,
                patient_name=patient_name,
                patient_phone=patient_phone,
                service=f"Blood Test: {test_name}",
                amount=amount,
                discount=Decimal(0),
                total=amount,
                status='paid',
                notes=f"Auto-generated for Blood Test #{blood_test.request_id}",
                bill_date=timezone.now().date(),
                created_by=request.user,
            )

            # 3. Integrate with Hospital Accountant: Create PaymentRecord entry
            payment_record = PaymentRecord.objects.create(
                hospital=hospital,
                billing=billing,
                patient_name=patient_name,
                patient_phone=patient_phone,
                amount=amount,
                method=payment_method,
                status='completed',
                reference=payment_reference,
                notes=f"Payment for Blood Test #{blood_test.request_id} ({test_name})",
                payment_date=timezone.now().date(),
                received_by=request.user,
            )

            # Link billing & payment to blood_test
            blood_test.billing = billing
            blood_test.payment_record = payment_record
            blood_test.save()

            messages.success(
                request,
                f"Blood test request #{blood_test.request_id} submitted! "
                f"Payment of BDT {amount} recorded to Hospital Accounts (Bill #{billing.bill_no}). "
                f"Order sent to Diagnostic Center / Lab."
            )
            return redirect('bloodbank_testing')

        if action == 'delete':
            test_id = request.POST.get('test_id')
            BloodTestRequest.objects.filter(id=test_id, hospital=hospital).delete()
            messages.success(request, 'Blood test request deleted.')
            return redirect('bloodbank_testing')

    # GET
    test_requests = BloodTestRequest.objects.filter(hospital=hospital) if hospital else BloodTestRequest.objects.none()
    current_status = request.GET.get('status', 'all').lower()
    search_query = request.GET.get('q', '').strip()

    if current_status == 'pending':
        test_requests = test_requests.filter(lab_status='pending')
    elif current_status == 'approved':
        test_requests = test_requests.filter(lab_status='approved')
    elif current_status == 'completed':
        test_requests = test_requests.filter(lab_status='completed')

    if search_query:
        test_requests = test_requests.filter(
            Q(request_id__icontains=search_query) |
            Q(patient_name__icontains=search_query) |
            Q(patient_phone__icontains=search_query) |
            Q(test_name__icontains=search_query) |
            Q(doctor_name__icontains=search_query)
        )

    total_tests = BloodTestRequest.objects.filter(hospital=hospital).count() if hospital else 0
    pending_tests = BloodTestRequest.objects.filter(hospital=hospital, lab_status='pending').count() if hospital else 0
    approved_tests = BloodTestRequest.objects.filter(hospital=hospital, lab_status='approved').count() if hospital else 0
    completed_tests = BloodTestRequest.objects.filter(hospital=hospital, lab_status='completed').count() if hospital else 0

    patients = Patient.objects.filter(hospital=hospital).select_related('user') if hospital else Patient.objects.none()
    diagnostic_tests = DiagnosticTest.objects.filter(hospital=hospital, is_active=True).order_by('name') if hospital else DiagnosticTest.objects.none()

    context = {
        'hospital': hospital,
        'test_requests': test_requests,
        'current_status': current_status,
        'search_query': search_query,
        'total_tests': total_tests,
        'pending_tests': pending_tests,
        'approved_tests': approved_tests,
        'completed_tests': completed_tests,
        'patients': patients,
        'diagnostic_tests': diagnostic_tests,
    }
    return render(request, 'accounts/bloodbank/testing.html', context)


def bloodbank_blood_test_slip(request, test_id):
    if not request.user.is_authenticated:
        return redirect('login')
    hospital = request.user.hospital
    test_req = get_object_or_404(BloodTestRequest, id=test_id, hospital=hospital)
    return render(request, 'accounts/bloodbank/test_slip.html', {'test_req': test_req})


def lab_blood_tests(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'lab' and request.user.role != 'hospital_admin':
        return redirect('dashboard')

    hospital = request.user.hospital
    test_requests = BloodTestRequest.objects.filter(hospital=hospital) if hospital else BloodTestRequest.objects.none()

    current_status = request.GET.get('status', 'all').lower()
    search_query = request.GET.get('q', '').strip()

    if current_status == 'pending':
        test_requests = test_requests.filter(lab_status='pending')
    elif current_status == 'approved':
        test_requests = test_requests.filter(lab_status='approved')
    elif current_status == 'completed':
        test_requests = test_requests.filter(lab_status='completed')

    if search_query:
        test_requests = test_requests.filter(
            Q(request_id__icontains=search_query) |
            Q(patient_name__icontains=search_query) |
            Q(patient_phone__icontains=search_query) |
            Q(test_name__icontains=search_query)
        )

    total_tests = BloodTestRequest.objects.filter(hospital=hospital).count() if hospital else 0
    pending_tests = BloodTestRequest.objects.filter(hospital=hospital, lab_status='pending').count() if hospital else 0
    approved_tests = BloodTestRequest.objects.filter(hospital=hospital, lab_status='approved').count() if hospital else 0
    completed_tests = BloodTestRequest.objects.filter(hospital=hospital, lab_status='completed').count() if hospital else 0

    context = {
        'hospital': hospital,
        'test_requests': test_requests,
        'current_status': current_status,
        'search_query': search_query,
        'total_tests': total_tests,
        'pending_tests': pending_tests,
        'approved_tests': approved_tests,
        'completed_tests': completed_tests,
    }
    return render(request, 'accounts/lab/blood_tests.html', context)


def lab_blood_test_approve(request, test_id):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'lab' and request.user.role != 'hospital_admin':
        return redirect('dashboard')

    hospital = request.user.hospital
    test_req = get_object_or_404(BloodTestRequest, id=test_id, hospital=hospital)
    test_req.lab_status = 'approved'
    test_req.lab_technician = request.user
    test_req.approved_at = timezone.now()
    test_req.save()

    messages.success(request, f"Order #{test_req.request_id} ({test_req.test_name}) approved. Sample received and testing started.")
    return redirect('lab_blood_tests')


def lab_blood_test_upload(request, test_id):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'lab' and request.user.role != 'hospital_admin':
        return redirect('dashboard')

    hospital = request.user.hospital
    test_req = get_object_or_404(BloodTestRequest, id=test_id, hospital=hospital)

    if request.method == 'POST':
        report_file = request.FILES.get('report_file')
        findings = request.POST.get('findings', '').strip()
        report_title = request.POST.get('report_title', '').strip() or f"{test_req.test_name} Report"

        if report_file:
            test_req.report_file = report_file
        test_req.findings = findings
        test_req.report_title = report_title
        test_req.lab_status = 'completed'
        test_req.completed_at = timezone.now()
        test_req.lab_technician = request.user

        # Create or link MedicalRecord
        medical_record = MedicalRecord.objects.create(
            hospital=hospital,
            patient_user=test_req.patient.user if test_req.patient and hasattr(test_req.patient, 'user') else None,
            patient_name=test_req.patient_name,
            patient_id=test_req.patient.patient_id if test_req.patient else '',
            patient_phone=test_req.patient_phone,
            title=report_title,
            record_type='lab',
            test_name=test_req.test_name,
            file=test_req.report_file,
            notes=findings,
            status='verified',
            uploaded_by=request.user,
            report_date=timezone.now().date(),
        )
        test_req.medical_record = medical_record
        test_req.save()

        messages.success(
            request,
            f"Test report for #{test_req.request_id} ({test_req.patient_name}) uploaded successfully! "
            f"Test completed and now visible in Blood Bank."
        )

    return redirect('lab_blood_tests')


def lab_blood_test_reject(request, test_id):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'lab' and request.user.role != 'hospital_admin':
        return redirect('dashboard')

    hospital = request.user.hospital
    test_req = get_object_or_404(BloodTestRequest, id=test_id, hospital=hospital)

    if request.method == 'POST':
        reason = request.POST.get('rejection_reason', '').strip()
        test_req.lab_status = 'rejected'
        test_req.rejection_reason = reason
        test_req.save()
        messages.warning(request, f"Order #{test_req.request_id} rejected: {reason}")

    return redirect('lab_blood_tests')


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


from .models import BloodBankProfile
from django.contrib import messages

def bloodbank_profile(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'bloodbank':
        return redirect('dashboard')

    profile, _ = BloodBankProfile.objects.get_or_create(user=request.user)
    hospital = request.user.hospital

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'update':
            user = request.user
            user.first_name = request.POST.get('first_name', '').strip()
            user.last_name = request.POST.get('last_name', '').strip()
            user.phone = request.POST.get('phone', '').strip()
            if request.POST.get('email'):
                user.email = request.POST.get('email').strip()
            user.save()

            profile.employee_id = request.POST.get('employee_id', '').strip()
            profile.designation = request.POST.get('designation', '').strip()
            profile.department = request.POST.get('department', '').strip()
            profile.qualification = request.POST.get('qualification', '').strip()
            profile.experience_years = int(request.POST.get('experience_years') or 0)
            profile.shift = request.POST.get('shift', '').strip()
            profile.bio = request.POST.get('bio', '').strip()
            profile.address = request.POST.get('address', '').strip()
            profile.date_of_birth = request.POST.get('date_of_birth') or None
            profile.gender = request.POST.get('gender', '').strip()
            profile.blood_group = request.POST.get('blood_group', '').strip()

            if request.FILES.get('profile_image'):
                profile.profile_image = request.FILES['profile_image']

            profile.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('bloodbank_profile')

        if action == 'remove_photo':
            if profile.profile_image:
                profile.profile_image.delete(save=False)
                profile.profile_image = None
                profile.save()
            messages.success(request, 'Profile photo removed.')
            return redirect('bloodbank_profile')

    context = {
        'hospital': hospital,
        'profile': profile,
        'user': request.user,
    }
    return render(request, 'accounts/bloodbank/profile.html', context)


# accountant
from django.db.models import Sum, Count, Q
def accountant_dashboard(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'accountant':
        return redirect('dashboard')

    hospital = request.user.hospital
    today = timezone.now().date()
    month_start = today.replace(day=1)

    total_billing = Decimal('0')
    total_payments = Decimal('0')
    total_expenses = Decimal('0')
    pending_invoices = 0
    today_payments = Decimal('0')
    month_income = Decimal('0')
    month_expense = Decimal('0')
    recent_payments = []
    recent_expenses = []

    if hospital:
        # PatientPayment (from patient module) if exists
        try:
            from .models import PatientPayment
            pay_qs = PatientPayment.objects.filter(hospital=hospital)
            total_payments = pay_qs.filter(status='paid').aggregate(t=Sum('amount'))['t'] or Decimal('0')
            today_payments = pay_qs.filter(status='paid', created_at__date=today).aggregate(t=Sum('amount'))['t'] or Decimal('0')
            month_income = pay_qs.filter(status='paid', created_at__date__gte=month_start).aggregate(t=Sum('amount'))['t'] or Decimal('0')
            recent_payments = pay_qs.order_by('-created_at')[:5]
        except Exception:
            pass

        try:
            from .models import Invoice
            inv_qs = Invoice.objects.filter(hospital=hospital)
            total_billing = inv_qs.aggregate(t=Sum('total_amount'))['t'] or Decimal('0')
            pending_invoices = inv_qs.filter(status='pending').count()
        except Exception:
            pass

        try:
            from .models import Expense
            exp_qs = Expense.objects.filter(hospital=hospital)
            total_expenses = exp_qs.aggregate(t=Sum('amount'))['t'] or Decimal('0')
            month_expense = exp_qs.filter(expense_date__gte=month_start).aggregate(t=Sum('amount'))['t'] or Decimal('0')
            recent_expenses = exp_qs.order_by('-expense_date')[:5]
        except Exception:
            pass

    net_balance = (month_income or Decimal('0')) - (month_expense or Decimal('0'))

    context = {
        'hospital': hospital,
        'user': request.user,
        'total_billing': total_billing,
        'total_payments': total_payments,
        'total_expenses': total_expenses,
        'pending_invoices': pending_invoices,
        'today_payments': today_payments,
        'month_income': month_income,
        'month_expense': month_expense,
        'net_balance': net_balance,
        'recent_payments': recent_payments,
        'recent_expenses': recent_expenses,
    }
    return render(request, 'accounts/accountant/dashboard.html', context)
def accountant_billing(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'accountant':
        return redirect('dashboard')

    hospital = request.user.hospital
    search = request.GET.get('q', '').strip()
    patients = Patient.objects.filter(hospital=hospital) if hospital else Patient.objects.none()

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'create':
            patient_id = request.POST.get('patient')
            patient = None
            patient_name = request.POST.get('patient_name', '').strip()
            patient_phone = request.POST.get('patient_phone', '').strip()
            if patient_id:
                patient = Patient.objects.filter(id=patient_id, hospital=hospital).first()
                if patient:
                    patient_name = getattr(patient, 'patient_name', None) or getattr(patient, 'name', None) or str(patient)
                    patient_phone = getattr(patient, 'phone', '') or patient_phone

            amount = Decimal(request.POST.get('amount') or 0)
            discount = Decimal(request.POST.get('discount') or 0)
            Billing.objects.create(
                hospital=hospital,
                patient=patient,
                patient_name=patient_name,
                patient_phone=patient_phone,
                service=request.POST.get('service', '').strip(),
                amount=amount,
                discount=discount,
                status=request.POST.get('status', 'pending'),
                notes=request.POST.get('notes', '').strip(),
                bill_date=request.POST.get('bill_date') or timezone.now().date(),
                created_by=request.user,
            )
            messages.success(request, 'Bill created.')
            return redirect('accountant_billing')

        if action == 'edit':
            bill = get_object_or_404(Billing, id=request.POST.get('bill_id'), hospital=hospital)
            bill.patient_name = request.POST.get('patient_name', '').strip()
            bill.patient_phone = request.POST.get('patient_phone', '').strip()
            bill.service = request.POST.get('service', '').strip()
            bill.amount = Decimal(request.POST.get('amount') or 0)
            bill.discount = Decimal(request.POST.get('discount') or 0)
            bill.status = request.POST.get('status', bill.status)
            bill.notes = request.POST.get('notes', '').strip()
            bill.bill_date = request.POST.get('bill_date') or bill.bill_date
            bill.save()
            messages.success(request, 'Bill updated.')
            return redirect('accountant_billing')

        if action == 'delete':
            Billing.objects.filter(id=request.POST.get('bill_id'), hospital=hospital).delete()
            messages.success(request, 'Bill deleted.')
            return redirect('accountant_billing')

    bills = Billing.objects.none()
    total_amount = 0
    pending_count = 0
    paid_count = 0
    if hospital:
        bills = Billing.objects.filter(hospital=hospital)
        if search:
            bills = bills.filter(
                Q(bill_no__icontains=search) |
                Q(patient_name__icontains=search) |
                Q(service__icontains=search) |
                Q(patient_phone__icontains=search)
            )
        total_amount = bills.aggregate(t=Sum('total'))['t'] or 0
        pending_count = bills.filter(status='pending').count()
        paid_count = bills.filter(status='paid').count()

    context = {
        'hospital': hospital,
        'bills': bills,
        'patients': patients,
        'total': bills.count() if hospital else 0,
        'total_amount': total_amount,
        'pending_count': pending_count,
        'paid_count': paid_count,
        'search': search,
        'status_choices': Billing.STATUS_CHOICES,
        'today': timezone.now().date(),
    }
    return render(request, 'accounts/accountant/billing.html', context)


def accountant_billing_pdf(request, bill_id):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'accountant':
        return redirect('dashboard')

    hospital = request.user.hospital
    bill = get_object_or_404(Billing, id=bill_id, hospital=hospital)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{bill.bill_no}.pdf"'

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4
    y = height - 50

    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, y, hospital.name if hospital else "NHIMS")
    y -= 22
    p.setFont("Helvetica", 11)
    p.drawString(50, y, "Hospital Bill / Invoice")
    y -= 30
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y, f"Bill No: {bill.bill_no}")
    y -= 18
    p.setFont("Helvetica", 11)
    p.drawString(50, y, f"Date: {bill.bill_date.strftime('%d %b %Y')}")
    y -= 18
    p.drawString(50, y, f"Patient: {bill.patient_name}")
    y -= 18
    p.drawString(50, y, f"Phone: {bill.patient_phone or '—'}")
    y -= 18
    p.drawString(50, y, f"Service: {bill.service}")
    y -= 18
    p.drawString(50, y, f"Amount: BDT {bill.amount}")
    y -= 18
    p.drawString(50, y, f"Discount: BDT {bill.discount}")
    y -= 18
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y, f"Total: BDT {bill.total}")
    y -= 18
    p.setFont("Helvetica", 11)
    p.drawString(50, y, f"Status: {bill.get_status_display()}")
    if bill.notes:
        y -= 24
        p.drawString(50, y, f"Notes: {bill.notes[:80]}")
    y -= 40
    p.setFont("Helvetica", 9)
    p.drawString(50, y, "Generated by NHIMS Accountant Module")
    p.showPage()
    p.save()
    return response
from .models import PaymentRecord, Billing
def accountant_payments(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'accountant':
        return redirect('dashboard')

    hospital = request.user.hospital
    search = request.GET.get('q', '').strip()
    bills = Billing.objects.filter(hospital=hospital, status__in=['pending', 'partial']) if hospital else Billing.objects.none()

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'create':
            bill_id = request.POST.get('billing')
            billing = None
            patient_name = request.POST.get('patient_name', '').strip()
            patient_phone = request.POST.get('patient_phone', '').strip()
            if bill_id:
                billing = Billing.objects.filter(id=bill_id, hospital=hospital).first()
                if billing:
                    patient_name = billing.patient_name
                    patient_phone = billing.patient_phone or patient_phone

            PaymentRecord.objects.create(
                hospital=hospital,
                billing=billing,
                patient_name=patient_name,
                patient_phone=patient_phone,
                amount=Decimal(request.POST.get('amount') or 0),
                method=request.POST.get('method', 'cash'),
                status=request.POST.get('status', 'completed'),
                reference=request.POST.get('reference', '').strip(),
                notes=request.POST.get('notes', '').strip(),
                payment_date=request.POST.get('payment_date') or timezone.now().date(),
                received_by=request.user,
            )
            if billing and request.POST.get('status') == 'completed':
                billing.status = 'paid'
                billing.save()
            messages.success(request, 'Payment recorded.')
            return redirect('accountant_payments')

        if action == 'edit':
            pay = get_object_or_404(PaymentRecord, id=request.POST.get('payment_id'), hospital=hospital)
            pay.patient_name = request.POST.get('patient_name', '').strip()
            pay.patient_phone = request.POST.get('patient_phone', '').strip()
            pay.amount = Decimal(request.POST.get('amount') or 0)
            pay.method = request.POST.get('method', 'cash')
            pay.status = request.POST.get('status', pay.status)
            pay.reference = request.POST.get('reference', '').strip()
            pay.notes = request.POST.get('notes', '').strip()
            pay.payment_date = request.POST.get('payment_date') or pay.payment_date
            pay.save()
            messages.success(request, 'Payment updated.')
            return redirect('accountant_payments')

        if action == 'delete':
            PaymentRecord.objects.filter(id=request.POST.get('payment_id'), hospital=hospital).delete()
            messages.success(request, 'Payment deleted.')
            return redirect('accountant_payments')

    payments = PaymentRecord.objects.none()
    total_amount = 0
    today_amount = 0
    completed = 0
    if hospital:
        payments = PaymentRecord.objects.filter(hospital=hospital)
        if search:
            payments = payments.filter(
                Q(payment_no__icontains=search) |
                Q(patient_name__icontains=search) |
                Q(reference__icontains=search)
            )
        total_amount = payments.filter(status='completed').aggregate(t=Sum('amount'))['t'] or 0
        today_amount = payments.filter(status='completed', payment_date=timezone.now().date()).aggregate(t=Sum('amount'))['t'] or 0
        completed = payments.filter(status='completed').count()

    context = {
        'hospital': hospital,
        'payments': payments,
        'bills': bills,
        'total': payments.count() if hospital else 0,
        'total_amount': total_amount,
        'today_amount': today_amount,
        'completed': completed,
        'search': search,
        'method_choices': PaymentRecord.METHOD_CHOICES,
        'status_choices': PaymentRecord.STATUS_CHOICES,
        'today': timezone.now().date(),
    }
    return render(request, 'accounts/accountant/payments.html', context)


def accountant_payment_pdf(request, payment_id):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'accountant':
        return redirect('dashboard')

    hospital = request.user.hospital
    pay = get_object_or_404(PaymentRecord, id=payment_id, hospital=hospital)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{pay.payment_no}.pdf"'

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4
    y = height - 50

    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, y, hospital.name if hospital else "NHIMS")
    y -= 22
    p.setFont("Helvetica", 11)
    p.drawString(50, y, "Payment Receipt")
    y -= 30
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y, f"Payment No: {pay.payment_no}")
    y -= 18
    p.setFont("Helvetica", 11)
    p.drawString(50, y, f"Date: {pay.payment_date.strftime('%d %b %Y')}")
    y -= 18
    p.drawString(50, y, f"Patient: {pay.patient_name}")
    y -= 18
    p.drawString(50, y, f"Phone: {pay.patient_phone or '—'}")
    y -= 18
    p.drawString(50, y, f"Amount: BDT {pay.amount}")
    y -= 18
    p.drawString(50, y, f"Method: {pay.get_method_display()}")
    y -= 18
    p.drawString(50, y, f"Status: {pay.get_status_display()}")
    y -= 18
    p.drawString(50, y, f"Reference: {pay.reference or '—'}")
    y -= 40
    p.setFont("Helvetica", 9)
    p.drawString(50, y, "Generated by NHIMS Accountant Module")
    p.showPage()
    p.save()
    return response
from .models import Invoice
def accountant_invoices(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'accountant':
        return redirect('dashboard')

    hospital = request.user.hospital
    search = request.GET.get('q', '').strip()
    patients = Patient.objects.filter(hospital=hospital) if hospital else Patient.objects.none()

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'create':
            patient_id = request.POST.get('patient')
            patient_name = request.POST.get('patient_name', '').strip()
            patient_phone = request.POST.get('patient_phone', '').strip()
            if patient_id:
                patient = Patient.objects.filter(id=patient_id, hospital=hospital).first()
                if patient:
                    patient_name = getattr(patient, 'patient_name', None) or getattr(patient, 'name', None) or str(patient)
                    patient_phone = getattr(patient, 'phone', '') or patient_phone

            Invoice.objects.create(
                hospital=hospital,
                patient_name=patient_name,
                patient_phone=patient_phone,
                patient_address=request.POST.get('patient_address', '').strip(),
                description=request.POST.get('description', '').strip(),
                amount=Decimal(request.POST.get('amount') or 0),
                tax=Decimal(request.POST.get('tax') or 0),
                status=request.POST.get('status', 'draft'),
                due_date=request.POST.get('due_date') or None,
                invoice_date=request.POST.get('invoice_date') or timezone.now().date(),
                notes=request.POST.get('notes', '').strip(),
                created_by=request.user,
            )
            messages.success(request, 'Invoice created.')
            return redirect('accountant_invoices')

        if action == 'edit':
            inv = get_object_or_404(Invoice, id=request.POST.get('invoice_id'), hospital=hospital)
            inv.patient_name = request.POST.get('patient_name', '').strip()
            inv.patient_phone = request.POST.get('patient_phone', '').strip()
            inv.patient_address = request.POST.get('patient_address', '').strip()
            inv.description = request.POST.get('description', '').strip()
            inv.amount = Decimal(request.POST.get('amount') or 0)
            inv.tax = Decimal(request.POST.get('tax') or 0)
            inv.status = request.POST.get('status', inv.status)
            inv.due_date = request.POST.get('due_date') or None
            inv.invoice_date = request.POST.get('invoice_date') or inv.invoice_date
            inv.notes = request.POST.get('notes', '').strip()
            inv.save()
            messages.success(request, 'Invoice updated.')
            return redirect('accountant_invoices')

        if action == 'delete':
            Invoice.objects.filter(id=request.POST.get('invoice_id'), hospital=hospital).delete()
            messages.success(request, 'Invoice deleted.')
            return redirect('accountant_invoices')

    invoices = Invoice.objects.none()
    total_amount = 0
    pending = 0
    paid = 0
    if hospital:
        invoices = Invoice.objects.filter(hospital=hospital)
        if search:
            invoices = invoices.filter(
                Q(invoice_no__icontains=search) |
                Q(patient_name__icontains=search) |
                Q(description__icontains=search)
            )
        total_amount = invoices.aggregate(t=Sum('total_amount'))['t'] or 0
        pending = invoices.filter(status__in=['draft', 'sent', 'overdue']).count()
        paid = invoices.filter(status='paid').count()

    context = {
        'hospital': hospital,
        'invoices': invoices,
        'patients': patients,
        'total': invoices.count() if hospital else 0,
        'total_amount': total_amount,
        'pending': pending,
        'paid': paid,
        'search': search,
        'status_choices': Invoice.STATUS_CHOICES,
        'today': timezone.now().date(),
    }
    return render(request, 'accounts/accountant/invoices.html', context)


def accountant_invoice_pdf(request, invoice_id):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'accountant':
        return redirect('dashboard')

    hospital = request.user.hospital
    inv = get_object_or_404(Invoice, id=invoice_id, hospital=hospital)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{inv.invoice_no}.pdf"'

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4
    y = height - 50

    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, y, hospital.name if hospital else "NHIMS")
    y -= 22
    p.setFont("Helvetica", 11)
    p.drawString(50, y, "Tax Invoice")
    y -= 30
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y, f"Invoice No: {inv.invoice_no}")
    y -= 18
    p.setFont("Helvetica", 11)
    p.drawString(50, y, f"Date: {inv.invoice_date.strftime('%d %b %Y')}")
    y -= 18
    if inv.due_date:
        p.drawString(50, y, f"Due Date: {inv.due_date.strftime('%d %b %Y')}")
        y -= 18
    p.drawString(50, y, f"Bill To: {inv.patient_name}")
    y -= 18
    p.drawString(50, y, f"Phone: {inv.patient_phone or '—'}")
    y -= 18
    p.drawString(50, y, f"Description: {inv.description}")
    y -= 18
    p.drawString(50, y, f"Amount: BDT {inv.amount}")
    y -= 18
    p.drawString(50, y, f"Tax: BDT {inv.tax}")
    y -= 18
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y, f"Total: BDT {inv.total_amount}")
    y -= 18
    p.setFont("Helvetica", 11)
    p.drawString(50, y, f"Status: {inv.get_status_display()}")
    y -= 40
    p.setFont("Helvetica", 9)
    p.drawString(50, y, "Generated by NHIMS Accountant Module")
    p.showPage()
    p.save()
    return response

def accountant_expenses(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'accountant':
        return redirect('dashboard')
    hospital = request.user.hospital
    expenses = Expense.objects.filter(hospital=hospital) if hospital else Expense.objects.none()
    search = request.GET.get('q', '').strip()
    if search:
        expenses = expenses.filter(Q(expense_no__icontains=search) | Q(title__icontains=search) | Q(paid_to__icontains=search) | Q(description__icontains=search) | Q(reference__icontains=search))
    if request.method == 'POST':
        action = request.POST.get('action')
        if not hospital:
            messages.error(request, 'Your account is not linked to a hospital.')
            return redirect('accountant_expenses')
        if action == 'delete':
            expense = get_object_or_404(Expense, id=request.POST.get('expense_id'), hospital=hospital)
            expense.delete()
            messages.success(request, 'Expense deleted.')
            return redirect('accountant_expenses')
        if action in ['create', 'edit']:
            try:
                amount = Decimal(request.POST.get('amount') or '0')
                if amount < 0:
                    raise InvalidOperation
                expense_date = request.POST.get('expense_date') or timezone.localdate().isoformat()
                title = request.POST.get('title', '').strip()
                if not title:
                    raise ValueError('Expense title is required.')
                category = request.POST.get('category', 'other')
                payment_method = request.POST.get('payment_method', 'cash')
                status = request.POST.get('status', 'pending')
                if category not in dict(Expense.CATEGORY_CHOICES):
                    raise ValueError('Select a valid category.')
                if payment_method not in dict(Expense.PAYMENT_CHOICES):
                    raise ValueError('Select a valid payment method.')
                if status not in dict(Expense.STATUS_CHOICES):
                    raise ValueError('Select a valid status.')
                if action == 'create':
                    expense = Expense(hospital=hospital, created_by=request.user)
                else:
                    expense = get_object_or_404(Expense, id=request.POST.get('expense_id'), hospital=hospital)
                expense.title = title
                expense.category = category
                expense.description = request.POST.get('description', '').strip()
                expense.amount = amount
                expense.payment_method = payment_method
                expense.status = status
                expense.expense_date = expense_date
                expense.paid_to = request.POST.get('paid_to', '').strip()
                expense.reference = request.POST.get('reference', '').strip()
                expense.notes = request.POST.get('notes', '').strip()
                expense.save()
                messages.success(request, 'Expense created.' if action == 'create' else 'Expense updated.')
            except (InvalidOperation, ValueError, TypeError):
                messages.error(request, 'Please enter valid expense details and a non-negative amount.')
            return redirect('accountant_expenses')
    all_expenses = Expense.objects.filter(hospital=hospital) if hospital else Expense.objects.none()
    context = {
        'hospital': hospital,
        'expenses': expenses,
        'total': all_expenses.count(),
        'total_amount': all_expenses.aggregate(total=Sum('amount'))['total'] or Decimal('0'),
        'pending': all_expenses.filter(status='pending').count(),
        'paid': all_expenses.filter(status='paid').count(),
        'search': search,
        'category_choices': Expense.CATEGORY_CHOICES,
        'payment_choices': Expense.PAYMENT_CHOICES,
        'status_choices': Expense.STATUS_CHOICES,
        'today': timezone.localdate(),
    }
    return render(request, 'accounts/accountant/expenses.html', context)
from decimal import Decimal, InvalidOperation
from .models import Expense
from patients.models import Patient


def accountant_expense_pdf(request, expense_id):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'accountant':
        return redirect('dashboard')
    hospital = request.user.hospital
    expense = get_object_or_404(Expense, id=expense_id, hospital=hospital)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{expense.expense_no}.pdf"'
    pdf = canvas.Canvas(response, pagesize=A4)
    width, height = A4
    y = height - 55
    pdf.setFont('Helvetica-Bold', 17)
    pdf.drawString(50, y, (hospital.name if hospital else 'NHIMS')[:80])
    y -= 30
    pdf.setFont('Helvetica-Bold', 14)
    pdf.drawString(50, y, 'Expense Report')
    y -= 30
    pdf.setFont('Helvetica', 11)
    details = [
        ('Expense No', expense.expense_no),
        ('Title', expense.title),
        ('Category', expense.get_category_display()),
        ('Description', expense.description),
        ('Amount', f'BDT {expense.amount}'),
        ('Payment Method', expense.get_payment_method_display()),
        ('Status', expense.get_status_display()),
        ('Expense Date', expense.expense_date.strftime('%d %b %Y')),
        ('Paid To', expense.paid_to or '-'),
        ('Reference', expense.reference or '-'),
        ('Notes', expense.notes or '-'),
    ]
    for label, value in details:
        lines = pdf.beginText(50, y)
        lines.setFont('Helvetica', 11)
        lines.textLine(f'{label}:')
        pdf.drawText(lines)
        value_lines = str(value).encode('ascii', 'replace').decode('ascii')
        pdf.setFont('Helvetica', 11)
        pdf.drawString(160, y, value_lines[:95])
        y -= 24
        if y < 60:
            pdf.showPage()
            y = height - 55
    pdf.setFont('Helvetica', 9)
    pdf.drawString(50, 35, 'Generated by NHIMS Accountant Module')
    pdf.save()
    return response

def accountant_payroll(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'accountant':
        return redirect('dashboard')
    hospital = request.user.hospital
    staff = Staff.objects.filter(hospital=hospital) if hospital else []
    context = {'staff': staff}
    return render(request, 'accounts/accountant/payroll.html', context)
from decimal import Decimal, InvalidOperation
from .models import BankAccount, BankTransaction
@login_required(login_url='login')
def accountant_accounts(request):
    if request.user.role != 'accountant':
        return redirect('dashboard')

    hospital = request.user.hospital
    if not hospital:
        return render(request, 'accounts/accountant/accounts.html', {
            'hospital': None,
            'accounts': [],
            'transactions': [],
            'total_accounts': 0,
            'active_accounts': 0,
            'total_balance': Decimal('0.00'),
            'total_transactions': 0,
            'search': '',
            'account_types': BankAccount.ACCOUNT_TYPES,
        })

    if request.method == 'POST':
        action = request.POST.get('action')

        if action in ['create_account', 'edit_account']:
            account_id = request.POST.get('account_id')
            bank_name = request.POST.get('bank_name', '').strip()
            account_name = request.POST.get('account_name', '').strip()
            account_number = request.POST.get('account_number', '').strip()
            branch_name = request.POST.get('branch_name', '').strip()
            account_type = request.POST.get('account_type', 'current')
            notes = request.POST.get('notes', '').strip()

            try:
                opening_balance = Decimal(request.POST.get('opening_balance', '0'))
                if opening_balance < 0:
                    raise InvalidOperation
                if not bank_name or not account_name or not account_number:
                    raise ValueError
                if account_type not in dict(BankAccount.ACCOUNT_TYPES):
                    raise ValueError

                if action == 'create_account':
                    account = BankAccount(
                        hospital=hospital,
                        created_by=request.user,
                    )
                else:
                    account = get_object_or_404(
                        BankAccount,
                        id=account_id,
                        hospital=hospital,
                    )

                account.bank_name = bank_name
                account.account_name = account_name
                account.account_number = account_number
                account.branch_name = branch_name
                account.account_type = account_type
                account.notes = notes

                if action == 'create_account':
                    account.opening_balance = opening_balance
                elif account.opening_balance != opening_balance:
                    messages.error(request, 'Opening balance cannot be changed after the account is created.')
                    return redirect('accountant_accounts')

                account.save()
                messages.success(request, 'Bank account saved successfully.')

            except (InvalidOperation, ValueError, TypeError):
                messages.error(request, 'Please enter valid account information and a non-negative opening balance.')

        elif action == 'add_transaction':
            account = get_object_or_404(
                BankAccount,
                id=request.POST.get('account_id'),
                hospital=hospital,
                status='active',
            )
            transaction_type = request.POST.get('transaction_type')
            description = request.POST.get('description', '').strip()
            reference = request.POST.get('reference', '').strip()

            try:
                amount = Decimal(request.POST.get('amount', '0'))
                transaction_date = datetime.strptime(
                    request.POST.get('transaction_date', ''),
                    '%Y-%m-%d'
                ).date()

                if amount <= 0 or transaction_type not in dict(BankTransaction.TRANSACTION_TYPES) or not description:
                    raise ValueError

                if transaction_type == 'withdrawal' and amount > account.current_balance:
                    messages.error(request, 'Withdrawal amount cannot exceed the current account balance.')
                else:
                    BankTransaction.objects.create(
                        account=account,
                        transaction_type=transaction_type,
                        amount=amount,
                        transaction_date=transaction_date,
                        reference=reference,
                        description=description,
                        recorded_by=request.user,
                    )
                    messages.success(request, 'Transaction recorded successfully.')

            except (InvalidOperation, ValueError, TypeError):
                messages.error(request, 'Enter a valid amount, date, transaction type, and description.')

        elif action == 'toggle_status':
            account = get_object_or_404(
                BankAccount,
                id=request.POST.get('account_id'),
                hospital=hospital,
            )
            account.status = 'inactive' if account.status == 'active' else 'active'
            account.save(update_fields=['status', 'updated_at'])
            messages.success(request, f'Account marked {account.status}.')

        return redirect('accountant_accounts')

    search = request.GET.get('search', '').strip()
    accounts = BankAccount.objects.filter(hospital=hospital).prefetch_related('transactions')

    if search:
        accounts = accounts.filter(
            Q(bank_name__icontains=search) |
            Q(account_name__icontains=search) |
            Q(account_number__icontains=search) |
            Q(branch_name__icontains=search)
        )

    all_accounts = BankAccount.objects.filter(hospital=hospital).prefetch_related('transactions')
    transactions = BankTransaction.objects.filter(
        account__hospital=hospital
    ).select_related('account', 'recorded_by')[:20]

    total_balance = sum(
        (account.current_balance for account in all_accounts),
        Decimal('0.00')
    )

    context = {
        'hospital': hospital,
        'accounts': accounts,
        'transactions': transactions,
        'total_accounts': all_accounts.count(),
        'active_accounts': all_accounts.filter(status='active').count(),
        'total_balance': total_balance,
        'total_transactions': BankTransaction.objects.filter(account__hospital=hospital).count(),
        'search': search,
        'account_types': BankAccount.ACCOUNT_TYPES,
        'transaction_types': BankTransaction.TRANSACTION_TYPES,
        'today': timezone.localdate().isoformat(),
    }
    return render(request, 'accounts/accountant/accounts.html', context)


@login_required(login_url='login')
def accountant_reports(request):
    if request.user.role != 'accountant':
        return redirect('dashboard')

    hospital = request.user.hospital
    today = timezone.localdate()
    current_month_start = today.replace(day=1)

    expenses = Expense.objects.filter(
        hospital=hospital
    ).exclude(status='cancelled')

    transactions = BankTransaction.objects.filter(
        account__hospital=hospital
    )
    from .models import PatientPayment, PaymentRecord

    patient_payments = PatientPayment.objects.filter(
        hospital=hospital,
        status__in=['paid', 'verified'],
    )
    payment_records = PaymentRecord.objects.filter(
        hospital=hospital,
        status='completed',
    )

    def deposit_total(start_date=None, end_date=None):
        patient_filter = {}
        payment_filter = {}
        transaction_filter = {'transaction_type': 'deposit'}
        if start_date and end_date:
            patient_filter['created_at__date__gte'] = start_date
            patient_filter['created_at__date__lte'] = end_date
            payment_filter['payment_date__gte'] = start_date
            payment_filter['payment_date__lte'] = end_date
            transaction_filter['transaction_date__gte'] = start_date
            transaction_filter['transaction_date__lte'] = end_date

        patient_total = patient_payments.filter(**patient_filter).aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0.00')
        payment_total = payment_records.filter(**payment_filter).aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0.00')
        bank_total = transactions.filter(**transaction_filter).aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0.00')
        return patient_total + payment_total + bank_total

    total_expenses = expenses.filter(
        status='paid'
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

    total_deposits = deposit_total()

    total_withdrawals = transactions.filter(
        transaction_type='withdrawal'
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

    total_transactions = transactions.count()
    net_cash_movement = total_deposits - total_withdrawals

    monthly_labels = []
    monthly_deposits = []
    monthly_expenses = []
    report_rows = []

    for offset in range(5, -1, -1):
        month_number = current_month_start.month - offset
        year_number = current_month_start.year

        while month_number <= 0:
            month_number += 12
            year_number -= 1

        month_start = date(year_number, month_number, 1)
        last_day = calendar.monthrange(year_number, month_number)[1]
        month_end = date(year_number, month_number, last_day)

        month_deposits = deposit_total(month_start, month_end)

        month_expenses = expenses.filter(
            status='paid',
            expense_date__gte=month_start,
            expense_date__lte=month_end
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

        month_withdrawals = transactions.filter(
            transaction_type='withdrawal',
            transaction_date__gte=month_start,
            transaction_date__lte=month_end
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

        monthly_labels.append(month_start.strftime('%b %Y'))
        monthly_deposits.append(float(month_deposits))
        monthly_expenses.append(float(month_expenses))

        report_rows.append({
            'year': year_number,
            'month': month_number,
            'report_name': 'Monthly Financial Summary',
            'period': month_start.strftime('%B %Y'),
            'month_name': month_start.strftime('%B'),
            'deposits': month_deposits,
            'expenses': month_expenses,
            'withdrawals': month_withdrawals,
            'net': month_deposits - month_withdrawals,
            'net_cash_movement': month_deposits - month_withdrawals,
        })

    category_data = []
    category_totals = expenses.filter(
        status='paid',
        expense_date__year=today.year
    ).values('category').annotate(
        total=Sum('amount')
    ).order_by('-total')

    for item in category_totals:
        category_display = dict(Expense._meta.get_field('category').choices).get(
            item['category'], item['category']
        )
        category_data.append({
            'label': category_display,
            'amount': float(item['total'] or 0)
        })

    context = {
        'hospital': hospital,
        'today': today,
        'total_deposits': total_deposits,
        'total_expenses': total_expenses,
        'total_withdrawals': total_withdrawals,
        'net_cash_movement': net_cash_movement,
        'total_transactions': total_transactions,
        'monthly_labels': monthly_labels,
        'monthly_deposits': monthly_deposits,
        'monthly_expenses': monthly_expenses,
        'category_data': category_data,
        'report_rows': report_rows,
    }

    return render(request, 'accounts/accountant/reports.html', context)


@login_required(login_url='login')
def accountant_report_download(request, year, month):
    if request.user.role != 'accountant':
        return redirect('dashboard')

    if month < 1 or month > 12:
        return redirect('accountant_reports')

    hospital = request.user.hospital
    last_day = calendar.monthrange(year, month)[1]
    month_start = date(year, month, 1)
    month_end = date(year, month, last_day)

    expenses = Expense.objects.filter(
        hospital=hospital,
        status='paid',
        expense_date__gte=month_start,
        expense_date__lte=month_end
    )

    transactions = BankTransaction.objects.filter(
        account__hospital=hospital,
        transaction_date__gte=month_start,
        transaction_date__lte=month_end
    )

    writer = csv.writer(response)
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response.write('\ufeff')
    response['Content-Disposition'] = (
        f'attachment; filename="financial_report_{year}_{month:02d}.csv"'
    )

    writer = csv.writer(response)
    writer.writerow(['NHIMS - Hospital Financial Report'])
    writer.writerow(['Hospital', str(hospital)])
    writer.writerow(['Reporting Period', month_start.strftime('%B %Y')])
    writer.writerow([])
    writer.writerow(['Record Type', 'Date', 'Account / Expense', 'Category / Transaction Type', 'Reference', 'Amount (BDT)', 'Description'])

    for transaction in transactions:
        writer.writerow([
            'Bank Transaction',
            transaction.transaction_date.strftime('%Y-%m-%d'),
            transaction.account.account_name,
            transaction.get_transaction_type_display(),
            transaction.reference,
            transaction.amount,
            transaction.description,
        ])

    for expense in expenses:
        writer.writerow([
            'Expense',
            expense.expense_date.strftime('%Y-%m-%d'),
            expense.title,
            expense.get_category_display(),
            expense.reference,
            expense.amount,
            expense.description,
        ])

    return response

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

    user = request.user

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'update':
            user.first_name = request.POST.get('first_name', '').strip()
            user.last_name = request.POST.get('last_name', '').strip()
            user.email = request.POST.get('email', '').strip()
            user.phone = request.POST.get('phone', '').strip()
            user.save()

            return redirect('accountant_profile')

    context = {
        'user': user,
        'profile': None,
        'hospital': user.hospital,
    }

    return render(
        request,
        'accounts/accountant/profile.html',
        context
    )

# Pharmacy
from .models import Medicine, PharmacyProfile
from django.db.models import Sum, Q, F
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta

def pharmacy_dashboard(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'pharmacy':
        return redirect('dashboard')

    hospital = request.user.hospital
    today = timezone.now().date()
    total_medicines = 0
    total_stock = 0
    low_stock = 0
    out_of_stock = 0
    expiring_soon = 0
    recent = []

    if hospital:
        meds = Medicine.objects.filter(hospital=hospital)
        total_medicines = meds.count()
        total_stock = meds.aggregate(t=Sum('stock'))['t'] or 0
        low_stock = meds.filter(stock__gt=0, stock__lte=F('reorder_level')).count()
        out_of_stock = meds.filter(stock=0).count()
        expiring_soon = meds.filter(
            expiry_date__isnull=False,
            expiry_date__gte=today,
            expiry_date__lte=today + timedelta(days=30)
        ).count()
        recent = meds.order_by('-updated_at')[:6]

    context = {
        'hospital': hospital,
        'user': request.user,
        'total_medicines': total_medicines,
        'total_stock': total_stock,
        'low_stock': low_stock,
        'out_of_stock': out_of_stock,
        'expiring_soon': expiring_soon,
        'recent': recent,
    }
    return render(request, 'accounts/pharmacy/dashboard.html', context)


def pharmacy_stock(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'pharmacy':
        return redirect('dashboard')

    hospital = request.user.hospital
    search = request.GET.get('q', '').strip()

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'create':
            payment_amount = Decimal(request.POST.get('payment_amount') or '0')
            if payment_amount < 0:
                messages.error(request, 'Payment amount cannot be negative.')
                return redirect('pharmacy_stock')

            with transaction.atomic():
                medicine = Medicine.objects.create(
                    hospital=hospital,
                    name=request.POST.get('name', '').strip(),
                    category=request.POST.get('category', 'tablet'),
                    strength=request.POST.get('strength', '').strip(),
                    stock=int(request.POST.get('stock') or 0),
                    unit=request.POST.get('unit', 'tablet'),
                    reorder_level=int(request.POST.get('reorder_level') or 20),
                    expiry_date=request.POST.get('expiry_date') or None,
                    batch_number=request.POST.get('batch_number', '').strip(),
                    company=request.POST.get('company', '').strip(),
                    supplier=request.POST.get('supplier', '').strip(),
                    price=request.POST.get('price') or 0,
                    payment_amount=payment_amount,
                )
                if payment_amount:
                    Expense.objects.create(
                        hospital=hospital,
                        category='medicine',
                        title=f'Medicine stock: {medicine.name}',
                        description=f'{medicine.stock} {medicine.get_unit_display()} of {medicine.name}'
                        f' from {medicine.company or medicine.supplier or "unspecified company"}',
                        amount=payment_amount,
                        payment_method=request.POST.get('payment_method', 'cash'),
                        status='paid',
                        expense_date=timezone.localdate(),
                        paid_to=medicine.company or medicine.supplier,
                        created_by=request.user,
                    )
            messages.success(request, 'Medicine added.')
            return redirect('pharmacy_stock')

        if action == 'edit':
            m = get_object_or_404(Medicine, id=request.POST.get('medicine_id'), hospital=hospital)
            m.name = request.POST.get('name', '').strip()
            m.category = request.POST.get('category', 'tablet')
            m.strength = request.POST.get('strength', '').strip()
            m.stock = int(request.POST.get('stock') or 0)
            m.unit = request.POST.get('unit', 'tablet')
            m.reorder_level = int(request.POST.get('reorder_level') or 20)
            m.expiry_date = request.POST.get('expiry_date') or None
            m.batch_number = request.POST.get('batch_number', '').strip()
            m.company = request.POST.get('company', '').strip()
            m.supplier = request.POST.get('supplier', '').strip()
            m.price = request.POST.get('price') or 0
            m.payment_amount = Decimal(request.POST.get('payment_amount') or '0')
            m.save()
            messages.success(request, 'Medicine updated.')
            return redirect('pharmacy_stock')

        if action == 'delete':
            Medicine.objects.filter(id=request.POST.get('medicine_id'), hospital=hospital).delete()
            messages.success(request, 'Medicine deleted.')
            return redirect('pharmacy_stock')

    medicines = Medicine.objects.none()
    company_filter = request.GET.get('company', '').strip()
    companies = []
    if hospital:
        medicines = Medicine.objects.filter(hospital=hospital)
        companies = medicines.exclude(company='').values_list(
            'company', flat=True
        ).distinct().order_by('company')
        if search:
            medicines = medicines.filter(
                Q(name__icontains=search) |
                Q(category__icontains=search) |
                Q(batch_number__icontains=search) |
                Q(company__icontains=search) |
                Q(supplier__icontains=search)
            )
        if company_filter:
            medicines = medicines.filter(company__iexact=company_filter)

    context = {
        'hospital': hospital,
        'medicines': medicines,
        'total': medicines.count(),
        'low_stock': medicines.filter(stock__gt=0, stock__lte=F('reorder_level')).count() if hospital else 0,
        'out_of_stock': medicines.filter(stock=0).count() if hospital else 0,
        'search': search,
        'company_filter': company_filter,
        'companies': companies,
        'category_choices': Medicine.CATEGORY_CHOICES,
        'unit_choices': Medicine.UNIT_CHOICES,
        'payment_choices': Expense.PAYMENT_CHOICES,
    }
    return render(request, 'accounts/pharmacy/stock.html', context)


def pharmacy_profile(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role != 'pharmacy':
        return redirect('dashboard')

    profile, _ = PharmacyProfile.objects.get_or_create(user=request.user)
    hospital = request.user.hospital

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'update':
            user = request.user
            user.first_name = request.POST.get('first_name', '').strip()
            user.last_name = request.POST.get('last_name', '').strip()
            user.phone = request.POST.get('phone', '').strip()
            if request.POST.get('email'):
                user.email = request.POST.get('email').strip()
            user.save()

            profile.employee_id = request.POST.get('employee_id', '').strip()
            profile.designation = request.POST.get('designation', '').strip()
            profile.qualification = request.POST.get('qualification', '').strip()
            profile.experience_years = int(request.POST.get('experience_years') or 0)
            profile.license_number = request.POST.get('license_number', '').strip()
            profile.shift = request.POST.get('shift', '').strip()
            profile.bio = request.POST.get('bio', '').strip()
            profile.address = request.POST.get('address', '').strip()
            profile.date_of_birth = request.POST.get('date_of_birth') or None
            profile.gender = request.POST.get('gender', '').strip()
            profile.blood_group = request.POST.get('blood_group', '').strip()
            if request.FILES.get('profile_image'):
                profile.profile_image = request.FILES['profile_image']
            profile.save()
            messages.success(request, 'Profile updated.')
            return redirect('pharmacy_profile')

        if action == 'remove_photo':
            if profile.profile_image:
                profile.profile_image.delete(save=False)
                profile.profile_image = None
                profile.save()
            messages.success(request, 'Photo removed.')
            return redirect('pharmacy_profile')

    context = {'hospital': hospital, 'profile': profile, 'user': request.user}
    return render(request, 'accounts/pharmacy/profile.html', context)
