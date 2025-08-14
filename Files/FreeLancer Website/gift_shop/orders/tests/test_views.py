from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from orders.models import Order

class OrderViewTests(TestCase):
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

    def test_order_create_view(self):
        response = self.client.get(reverse('orders:order_create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'orders/create.html')

    def test_order_detail_view(self):
        response = self.client.get(
            reverse('orders:order_detail', args=[self.order.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'orders/detail.html')
        self.assertContains(response, self.order.first_name)
        self.assertContains(response, self.order.address)

    def test_order_create_post(self):
        order_data = {
            'first_name': 'New',
            'last_name': 'User',
            'email': 'new@example.com',
            'address': '456 New St',
            'postal_code': '67890',
            'city': 'New City'
        }
        response = self.client.post(reverse('orders:order_create'), order_data)
        self.assertEqual(response.status_code, 302)  # Redirect after creation
        self.assertTrue(
            Order.objects.filter(email='new@example.com').exists()
        )
