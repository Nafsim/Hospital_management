from django.test import TestCase

from .forms import LoginForm
from .models import User


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
