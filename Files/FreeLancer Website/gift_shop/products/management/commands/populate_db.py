from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from products.models import Product
from django.utils.text import slugify
import random

class Command(BaseCommand):
    help = 'Populate database with sample data'

    def handle(self, *args, **kwargs):
        # Sample product data
        products_data = [
            {
                'name': 'Handcrafted Wooden Box',
                'description': 'Beautiful handcrafted wooden box perfect for storing jewelry or small treasures. Made from premium oak with intricate carved details.',
                'price': '39.99',
                'stock': 15
            },
            {
                'name': 'Personalized Photo Frame',
                'description': 'Elegant photo frame that can be personalized with names and dates. Available in silver or gold finish.',
                'price': '24.99',
                'stock': 25
            },
            {
                'name': 'Aromatherapy Gift Set',
                'description': 'Luxury aromatherapy set including essential oils, diffuser, and scented candles. Perfect for relaxation and stress relief.',
                'price': '49.99',
                'stock': 20
            },
            {
                'name': 'Custom Name Necklace',
                'description': 'Sterling silver necklace that can be customized with any name or word. Comes in a beautiful gift box.',
                'price': '34.99',
                'stock': 30
            },
            {
                'name': 'Gourmet Chocolate Collection',
                'description': 'Premium assortment of handmade chocolates including dark, milk, and white chocolate varieties with different fillings.',
                'price': '29.99',
                'stock': 40
            },
            {
                'name': 'Leather Travel Journal',
                'description': 'Handmade leather journal perfect for travelers. Includes high-quality paper and a built-in pen holder.',
                'price': '19.99',
                'stock': 35
            },
            {
                'name': 'Smart Plant Pot',
                'description': 'Modern plant pot with built-in sensors to monitor soil moisture, light, and temperature. Perfect for plant lovers.',
                'price': '44.99',
                'stock': 18
            },
            {
                'name': 'Bamboo Tea Set',
                'description': 'Complete tea set made from sustainable bamboo. Includes teapot, cups, and serving tray.',
                'price': '54.99',
                'stock': 12
            },
            {
                'name': 'Crystal Wine Glasses',
                'description': 'Set of 4 elegant crystal wine glasses. Perfect for wine enthusiasts and special occasions.',
                'price': '64.99',
                'stock': 20
            },
            {
                'name': 'Artistic Wall Clock',
                'description': 'Modern wall clock with artistic design. Silent movement and easy to read numbers.',
                'price': '39.99',
                'stock': 15
            }
        ]

        # Create products
        for product_data in products_data:
            product = Product(
                name=product_data['name'],
                slug=slugify(product_data['name']),
                description=product_data['description'],
                price=product_data['price'],
                stock=product_data['stock'],
                available=True
            )
            product.save()
            self.stdout.write(self.style.SUCCESS(f'Created product: {product.name}'))

        self.stdout.write(self.style.SUCCESS('Successfully populated database with sample data'))
