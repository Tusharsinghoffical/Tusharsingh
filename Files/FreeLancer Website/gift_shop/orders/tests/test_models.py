from django.test import TestCase
from django.contrib.auth import get_user_model
from orders.models import Order

class OrderTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.order = Order.objects.create(
            user=self.user,
            first_name='Test',
            last_name='User',
            email='test@example.com',
            address='123 Test St',
            postal_code='12345',
            city='Test City'
        )

    def test_order_str(self):
        self.assertEqual(str(self.order), f'Order {self.order.id}')

    def test_order_total_cost(self):
        self.assertEqual(self.order.get_total_cost(), 0)  # Empty order
