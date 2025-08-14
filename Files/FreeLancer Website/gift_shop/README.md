# GiftNest E-commerce Platform

A Django-based e-commerce platform for gift shopping with integrated payment processing and email notifications.

## Features

- Product catalog with search and filtering
- Shopping cart functionality
- Secure payment processing with Stripe
- User authentication and profiles
- Order management system
- Email notifications for orders and account actions
- Responsive design with Bootstrap

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd gift_shop
```

2. Create and activate virtual environment:
```bash
python -m venv myvenv
source myvenv/bin/activate  # On Windows: myvenv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create .env file and set environment variables:
```
SECRET_KEY=your_secret_key
DEBUG=True
STRIPE_PUBLIC_KEY=your_stripe_public_key
STRIPE_SECRET_KEY=your_stripe_secret_key
EMAIL_HOST=your_smtp_host
EMAIL_HOST_USER=your_email
EMAIL_HOST_PASSWORD=your_email_password
```

5. Run migrations:
```bash
python manage.py migrate
```

6. Create superuser:
```bash
python manage.py createsuperuser
```

7. Run development server:
```bash
python manage.py runserver
```

## Testing

Run tests with:
```bash
python manage.py test
```

## Project Structure

- `cart/` - Shopping cart functionality
- `orders/` - Order processing and management
- `payment/` - Payment integration with Stripe
- `products/` - Product catalog and management
- `users/` - User authentication and profiles
- `templates/` - HTML templates
- `static/` - Static files (CSS, JS, images)
- `utils/` - Utility functions

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License.
