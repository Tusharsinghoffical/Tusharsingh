# Django FreelancerPro Setup Guide

## 🚀 Quick Start

### 1. Install Python and Django

First, make sure you have Python installed. Then install Django:

```bash
# Install Django and dependencies
pip install -r requirements.txt
```

### 2. Run Django Commands

```bash
# Make migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser (admin)
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

### 3. Access Your Website

Open your browser and go to:
- **Main Website**: http://127.0.0.1:8000/
- **Admin Panel**: http://127.0.0.1:8000/admin/

## 📁 Project Structure

```
freelancerpro/
├── manage.py                 # Django management script
├── requirements.txt          # Python dependencies
├── freelancerpro/           # Main project settings
│   ├── __init__.py
│   ├── settings.py          # Django settings
│   ├── urls.py             # Main URL configuration
│   └── wsgi.py             # WSGI configuration
├── core/                    # Core app
│   ├── models.py           # User profiles, site settings
│   ├── views.py            # Homepage views
│   └── urls.py             # Core URLs
├── services/               # Services app
│   ├── models.py          # Service offerings
│   ├── views.py           # Service views
│   └── urls.py            # Service URLs
├── portfolio/              # Portfolio app
│   ├── models.py          # Project models
│   ├── views.py           # Portfolio views
│   └── urls.py            # Portfolio URLs
├── testimonials/           # Testimonials app
│   ├── models.py          # Client reviews
│   ├── views.py           # Testimonial views
│   └── urls.py            # Testimonial URLs
├── contact/                # Contact app
│   ├── models.py          # Contact form
│   ├── forms.py           # Contact forms
│   ├── views.py           # Contact views
│   └── urls.py            # Contact URLs
├── templates/              # HTML templates
│   ├── base.html          # Base template
│   └── core/
│       └── home.html      # Homepage template
├── static/                 # Static files (CSS, JS, images)
└── media/                  # User uploaded files
```

## 🎨 Features

### ✅ Complete E-commerce Website
- **Professional Portfolio** - Showcase your work
- **Service Catalog** - Display services with pricing
- **Client Testimonials** - Build trust with reviews
- **Contact Forms** - Easy client communication
- **Admin Panel** - Manage content easily
- **Responsive Design** - Works on all devices

### ✅ Technical Features
- **Django 4.2** - Latest stable version
- **Bootstrap 5** - Modern UI framework
- **SQLite Database** - Easy to set up
- **User Authentication** - Login/logout system
- **Form Handling** - Contact forms with validation
- **Image Upload** - Portfolio and avatar uploads
- **Email Integration** - Contact form notifications

## 🛠️ Customization

### 1. Update Site Information

**Admin Panel**: http://127.0.0.1:8000/admin/
- Add your services
- Upload portfolio projects
- Add client testimonials
- Update site settings

### 2. Customize Templates

**File**: `templates/base.html`
- Update navigation links
- Change colors and styling
- Add your logo
- Modify footer information

### 3. Update Content

**File**: `templates/core/home.html`
- Update hero section text
- Change service descriptions
- Add your own projects
- Update contact information

### 4. Database Management

```bash
# Create new migrations after model changes
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Load sample data (if available)
python manage.py loaddata sample_data.json
```

## 📧 Email Configuration

Update email settings in `freelancerpro/settings.py`:

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
```

## 🚀 Deployment

### 1. Production Settings

Update `freelancerpro/settings.py`:

```python
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']

# Use PostgreSQL for production
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'your_db_name',
        'USER': 'your_db_user',
        'PASSWORD': 'your_db_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### 2. Static Files

```bash
# Collect static files
python manage.py collectstatic

# Serve with nginx or Apache
```

### 3. Deployment Platforms

- **Heroku** - Easy deployment
- **DigitalOcean** - VPS hosting
- **AWS** - Scalable cloud hosting
- **Vercel** - Static site hosting

## 🔧 Development

### Available Commands

```bash
# Run development server
python manage.py runserver

# Create new app
python manage.py startapp myapp

# Make migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Shell
python manage.py shell

# Test
python manage.py test
```

### Environment Variables

Create `.env` file:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
STRIPE_PUBLISHABLE_KEY=your-stripe-key
STRIPE_SECRET_KEY=your-stripe-secret
```

## 📊 Admin Panel

Access admin at: http://127.0.0.1:8000/admin/

**Manage:**
- Services
- Portfolio projects
- Client testimonials
- Contact submissions
- User profiles
- Site settings

## 🎯 Next Steps

1. **Install Dependencies**: `pip install -r requirements.txt`
2. **Run Migrations**: `python manage.py migrate`
3. **Create Admin**: `python manage.py createsuperuser`
4. **Start Server**: `python manage.py runserver`
5. **Customize Content**: Update templates and add your data
6. **Deploy**: Choose your hosting platform

## 🆘 Support

If you encounter issues:

1. Check Python version (3.8+ required)
2. Verify Django installation
3. Check database migrations
4. Review error logs
5. Ensure all dependencies are installed

---

**Your Django freelancer website is ready! 🚀** 