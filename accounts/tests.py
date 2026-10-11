from django.test import TestCase

from .forms import LoginForm
from .models import User
from hospitals.models import Hospital
from patients.models import Patient
from .models import PatientAppointment


class LoginFormTests(TestCase):
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
