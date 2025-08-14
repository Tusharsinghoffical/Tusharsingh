from django.test import TestCase
from django.contrib.auth import get_user_model
from cart.cart import Cart
from django.test.client import RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware

class CartTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.request = self.factory.get('/')
        middleware = SessionMiddleware(lambda x: None)
        middleware.process_request(self.request)
        self.request.session.save()
        
    def test_cart_creation(self):
        cart = Cart(self.request)
        self.assertEqual(len(cart), 0)
        
    def test_add_to_cart(self):
        cart = Cart(self.request)
        product_data = {
            'product_id': 1,
            'quantity': 1,
            'price': '10.00'
        }
        cart.add(product_data)
        self.assertEqual(len(cart), 1)
