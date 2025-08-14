from django.test import TestCase
from products.models import Product

class ProductModelTests(TestCase):
    def setUp(self):
        self.product = Product.objects.create(
            name="Test Product",
            description="Test Description",
            price=99.99,
            stock=10
        )

    def test_product_str(self):
        self.assertEqual(str(self.product), "Test Product")

    def test_product_price_format(self):
        self.assertEqual(self.product.price, 99.99)
