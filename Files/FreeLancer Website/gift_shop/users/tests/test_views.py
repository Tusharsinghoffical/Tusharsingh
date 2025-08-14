from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

class UserTests(TestCase):
    def setUp(self):
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        User = get_user_model()
        self.user = User.objects.create_user(**self.user_data)

    def test_user_login(self):
        response = self.client.post(reverse('login'), {
            'username': self.user_data['username'],
            'password': self.user_data['password']
        })
        self.assertEqual(response.status_code, 302)  # Redirect after login

    def test_user_registration(self):
        new_user_data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password1': 'newpass123',
            'password2': 'newpass123'
        }
        response = self.client.post(reverse('register'), new_user_data)
        self.assertEqual(response.status_code, 302)  # Redirect after registration
