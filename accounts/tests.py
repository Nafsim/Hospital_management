from django.test import TestCase

from .forms import LoginForm
from .models import User, Expense, Medicine, PaymentRecord
from hospitals.models import Hospital
from patients.models import Patient
from staff.models import Staff
from .models import PatientAppointment


class LoginFormTests(TestCase):
    def test_hospital_admin_can_edit_staff(self):
        hospital = Hospital.objects.create(
            name='Staff Edit Hospital',
            code='TEST-STAFF-EDIT',
            address='Test address',
        )
        admin = User.objects.create_user(
            username='admin@example.com',
            email='admin@example.com',
            password='ValidPass123!',
            role='hospital_admin',
            hospital=hospital,
        )
        staff_user = User.objects.create_user(
            username='staff@example.com',
            email='staff@example.com',
            password='ValidPass123!',
            role='nurse',
            hospital=hospital,
        )
        staff = Staff.objects.create(
            user=staff_user,
            hospital=hospital,
            employee_id='EMP-001',
            department='Nurse',
            designation='Nurse',
            date_of_joining='2026-01-01',
        )

        self.client.force_login(admin)
        response = self.client.post(
            '/accounts/hospital-admin/staff/',
            {
                'action': 'edit',
                'staff_id': staff.id,
                'first_name': 'Updated',
                'last_name': 'Staff',
                'email': 'updated-staff@example.com',
                'phone': '01700000000',
                'employee_id': 'EMP-002',
                'department': 'Accountant',
                'designation': 'Senior Accountant',
                'city': 'Dhaka',
                'national_id': 'NID-002',
                'date_of_joining': '2026-02-01',
                'qualification': 'BBA',
                'is_active': 'on',
            },
        )

        self.assertRedirects(response, '/accounts/hospital-admin/staff/')
        staff_user.refresh_from_db()
        staff.refresh_from_db()
        self.assertEqual(staff_user.first_name, 'Updated')
        self.assertEqual(staff_user.email, 'updated-staff@example.com')
        self.assertEqual(staff_user.username, 'staff@example.com')
        self.assertEqual(staff_user.role, 'accountant')
        self.assertEqual(staff.employee_id, 'EMP-002')
        self.assertEqual(staff.designation, 'Senior Accountant')
        self.assertEqual(staff.city, 'Dhaka')
        self.assertEqual(staff.national_id, 'NID-002')
        self.assertEqual(staff.qualification, 'BBA')

    def test_pharmacy_stock_company_filter_and_payment_creates_accounting_expense(self):
        hospital = Hospital.objects.create(
            name='Pharmacy Test Hospital',
            code='TEST-PHARMACY',
            address='Test address',
        )
        pharmacist = User.objects.create_user(
            username='pharmacist@example.com',
            email='pharmacist@example.com',
            password='ValidPass123!',
            role='pharmacy',
            hospital=hospital,
        )

        self.client.force_login(pharmacist)
        response = self.client.post(
            '/accounts/pharmacy/stock/',
            {
                'action': 'create',
                'name': 'Paracetamol',
                'category': 'tablet',
                'strength': '500mg',
                'stock': '100',
                'unit': 'tablet',
                'reorder_level': '20',
                'company': 'Square',
                'payment_amount': '1250.00',
                'payment_method': 'bank',
            },
        )

        self.assertRedirects(response, '/accounts/pharmacy/stock/')
        medicine = Medicine.objects.get(hospital=hospital)
        self.assertEqual(medicine.company, 'Square')
        self.assertEqual(medicine.payment_amount, 1250)
        expense = Expense.objects.get(hospital=hospital)
        self.assertEqual(expense.category, 'medicine')
        self.assertEqual(expense.amount, 1250)
        self.assertEqual(expense.paid_to, 'Square')

        response = self.client.get(
            '/accounts/pharmacy/stock/',
            {'q': 'square'},
        )
        self.assertContains(response, 'Paracetamol')
        response = self.client.get(
            '/accounts/pharmacy/stock/',
            {'company': 'Square'},
        )
        self.assertContains(response, 'Paracetamol')

    def test_accountant_report_includes_completed_payment_records(self):
        hospital = Hospital.objects.create(
            name='Reports Test Hospital',
            code='TEST-REPORTS',
            address='Test address',
        )
        accountant = User.objects.create_user(
            username='accountant@example.com',
            email='accountant@example.com',
            password='ValidPass123!',
            role='accountant',
            hospital=hospital,
        )
        PaymentRecord.objects.create(
            hospital=hospital,
            patient_name='Report Patient',
            amount='850.00',
            status='completed',
            payment_date='2026-10-15',
        )

        self.client.force_login(accountant)
        response = self.client.get('/accounts/accountant/reports/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '850.00')

    def test_lab_login_normalizes_email_before_authentication(self):
        user = User.objects.create_user(
            username='Lab.User@Example.com',
            email='Lab.User@Example.com',
            password='ValidPass123!',
            role='lab',
        )

        form = LoginForm(
            data={
                'username': ' lab.user@example.com ',
                'password': 'ValidPass123!',
                'role': 'lab',
            }
        )

        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.get_user(), user)

    def test_patient_can_submit_non_appointment_payment_without_assigned_hospital(self):
        hospital = Hospital.objects.create(
            name='Test Hospital',
            code='TEST-PAY',
            address='Test address',
        )
        user = User.objects.create_user(
            username='patient@example.com',
            email='patient@example.com',
            password='ValidPass123!',
            role='patient',
        )

        self.client.force_login(user)
        response = self.client.post(
            '/accounts/patient/payments/',
            {
                'action': 'pay',
                'hospital_id': hospital.id,
                'amount': '750',
                'purpose': 'medicine',
                'method': 'bkash',
                'transaction_id': 'TXN-123',
                'note': 'Medicine purchase',
            },
        )

        self.assertRedirects(response, '/accounts/patient/payments/')
        payment = user.payments.get()
        self.assertEqual(payment.hospital, hospital)
        self.assertEqual(payment.purpose, 'medicine')
        self.assertEqual(payment.amount, 750)

    def test_nurse_patient_search_uses_patient_user_fields(self):
        hospital = Hospital.objects.create(
            name='Nurse Test Hospital',
            code='TEST-NURSE',
            address='Test address',
        )
        nurse = User.objects.create_user(
            username='nurse@example.com',
            email='nurse@example.com',
            password='ValidPass123!',
            role='nurse',
            hospital=hospital,
        )
        patient_user = User.objects.create_user(
            username='patient-display@example.com',
            email='patient-display@example.com',
            password='ValidPass123!',
            first_name='Patient',
            last_name='Display',
            phone='01700000000',
            role='patient',
        )
        patient = Patient.objects.create(
            user=patient_user,
            hospital=hospital,
            patient_id='PT-TEST-01',
            date_of_birth='1990-01-01',
            gender='M',
        )

        self.client.force_login(nurse)
        response = self.client.get(
            '/accounts/nurse/patients/',
            {'search': 'patient'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Patient Display')
        self.assertContains(response, patient.patient_id)

    def test_nurse_pages_sync_patients_from_approved_appointments(self):
        hospital = Hospital.objects.create(
            name='Appointment Hospital',
            code='TEST-APPT-NURSE',
            address='Test address',
        )
        nurse = User.objects.create_user(
            username='appointment-nurse@example.com',
            email='appointment-nurse@example.com',
            password='ValidPass123!',
            role='nurse',
            hospital=hospital,
        )
        patient_user = User.objects.create_user(
            username='appointment-patient@example.com',
            email='appointment-patient@example.com',
            password='ValidPass123!',
            first_name='Appointment',
            last_name='Patient',
            role='patient',
        )
        PatientAppointment.objects.create(
            hospital=hospital,
            patient_user=patient_user,
            doctor=nurse,
            patient_name='Appointment Patient',
            appointment_date='2026-10-11',
            appointment_time='10:00',
            payment_status='paid',
            status='approved',
        )

        self.client.force_login(nurse)
        dashboard = self.client.get('/accounts/nurse/dashboard/')
        vital_signs = self.client.get('/accounts/nurse/vital-signs/')
        notes = self.client.get('/accounts/nurse/nursing-notes/')
        patients = self.client.get('/accounts/nurse/patients/')

        self.assertEqual(dashboard.status_code, 200)
        self.assertEqual(vital_signs.status_code, 200)
        self.assertEqual(notes.status_code, 200)
        self.assertEqual(patients.status_code, 200)
        self.assertContains(vital_signs, 'Appointment Patient')
        self.assertContains(notes, 'Appointment Patient')
        self.assertContains(patients, 'Appointment Patient')
        self.assertEqual(Patient.objects.filter(user=patient_user, hospital=hospital).count(), 1)
