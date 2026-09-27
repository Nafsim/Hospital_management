from django.shortcuts import render , redirect
from django.contrib.auth import login, authenticate
from django.contrib import messages
from .forms import LoginForm


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            if user.role == "hospital_admin":
                return redirect("hospital_admin_dashboard")
            elif user.role == "doctor":
                return redirect("doctor_dashboard")
            elif user.role == "moh":
                return redirect("moh_dashboard")
            elif user.is_superuser:
                return redirect("moh_dashboard")

            return redirect("dashboard")
        else:
            messages.error(request, "Invalid email, password or role. Please try again.")
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form})


def dashboard(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role == "hospital_admin":
        return redirect('hospital_admin_dashboard')
    elif request.user.role == "moh":
        return redirect('moh_dashboard')
    elif request.user.is_superuser:
        return redirect("moh_dashboard")
    return redirect("login")

def moh_dashboard(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'accounts/moh/dashboard.html')

def moh_notices(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'accounts/moh/notices.html')

def hospital_approval(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'accounts/moh/hospital_approval.html')

def moh_facilities(request):
    if not request.user.is_authenticated:
        return redirect('login')
    search = request.GET.get('q', '')
    return render(request, 'accounts/moh/facilities.html', {'search': search})

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

def hospital_admin_dashboard(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'accounts/hospital_admin/dashboard.html')

def hospital_admin_notices(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'accounts/hospital_admin/notices.html')

def hospital_doctors(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'accounts/hospital_admin/doctors.html')

def hospital_staff(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'accounts/hospital_admin/staff.html')

def hospital_profile(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'accounts/hospital_admin/hospital_profile.html')

def hospital_departments(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'accounts/hospital_admin/departments.html')

def hospital_patients(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'accounts/hospital_admin/patients.html')

def hospital_documents(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'accounts/hospital_admin/documents.html')

def hospital_payroll(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'accounts/hospital_admin/payroll.html')

def hospital_pharmacy(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'accounts/hospital_admin/pharmacy.html')

def hospital_blood_bank(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'accounts/hospital_admin/blood_bank.html')

def hospital_diagnostics(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'accounts/hospital_admin/diagnostics.html')

def hospital_users_access(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'accounts/hospital_admin/users_access.html')

def hospital_facility(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'accounts/hospital_admin/facility.html')

def hospital_admin_settings(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'accounts/hospital_admin/settings.html')

def hospital_contact_support(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'accounts/hospital_admin/contact_support.html')

def hospital_notifications(request):
    if not request.user.is_authenticated:
        return redirect('login')
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

