import json
from django.shortcuts import render , redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib import messages
from .forms import LoginForm, HospitalCreationForm
import calendar
from datetime import datetime, timedelta
from django.apps import apps
from patients.models import Patient, Visit
from staff.models import Staff
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
                'Pharmacy': 'pharmacy',
                'Medical Records': 'medical_records',
                'HR / Administration': 'admin'
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
            staff_member = Staff.objects.get(
                id=staff_id,
                hospital=hospital
            )

            user = staff_member.user
            staff_member.delete()

            if user:
                user.delete()

            return redirect('hospital_staff')

    staff = Staff.objects.filter(
        hospital=hospital
    ).select_related('user')

    staff_filter = request.GET.get('staff_filter', 'all')

    if staff_filter == 'doctor':
        staff = staff.filter(
            user__role='doctor'
        )

    elif staff_filter == 'nurse':
        staff = staff.filter(
            user__role='nurse'
        )

    elif staff_filter == 'accountant':
        staff = staff.filter(
            user__role='accountant'
        )

    elif staff_filter == 'laboratory':
        staff = staff.filter(
            user__role='lab'
        )

    elif staff_filter == 'counter':
        staff = staff.filter(
            user__role='counter'
        )

    elif staff_filter == 'blood':
        staff = staff.filter(
            user__role='bloodbank'
        )

    elif staff_filter == 'pharmacy':
        staff = staff.filter(
            user__role='pharmacy'
        )

    elif staff_filter == 'medical':
        staff = staff.filter(
            department__icontains='Medical Records'
        )

    elif staff_filter == 'administration':
        staff = staff.filter(
            department__icontains='Administration'
        )

    context = {
        'staff': staff,
        'staff_filter': staff_filter,
        'hospital': hospital
    }

    return render(
        request,
        'accounts/hospital_admin/staff.html',
        context
    )

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

    context = {
        'hospital': hospital,
        'staff': staff,
        'payroll': payroll,
        'total_staff': total_staff,
        'total_payroll': total_payroll,
        'pending_payroll': pending_payroll,
    }

    return render(
        request,
        'accounts/hospital_admin/payroll.html',
        context
    )
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
