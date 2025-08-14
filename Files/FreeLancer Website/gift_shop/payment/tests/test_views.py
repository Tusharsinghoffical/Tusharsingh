from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from orders.models import Order
import stripe

class PaymentTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
        
        self.order = Order.objects.create(
            user=self.user,
            first_name='Test',
            last_name='User',
            email='test@example.com',
            address='123 Test St',
            postal_code='12345',
            city='Test City'
        )

    def test_payment_process_view(self):
        response = self.client.get(reverse('payment:process'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'payment/process.html')

    def test_payment_success_view(self):
        response = self.client.get(reverse('payment:success'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'payment/success.html')

    def test_payment_cancel_view(self):
        response = self.client.get(reverse('payment:cancel'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'payment/cancel.html')
