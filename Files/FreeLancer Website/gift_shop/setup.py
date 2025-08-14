#!/usr/bin/env python
import os
import sys
import subprocess
import venv
from pathlib import Path

def main():
    # Create virtual environment
    print("Creating virtual environment...")
    venv.create("myvenv", with_pip=True)

    # Determine the pip and python executable paths
    if sys.platform == "win32":
        python_path = "myvenv\\Scripts\\python.exe"
        pip_path = "myvenv\\Scripts\\pip.exe"
    else:
        python_path = "myvenv/bin/python"
        pip_path = "myvenv/bin/pip"

    # Upgrade pip
    print("Upgrading pip...")
    subprocess.run([python_path, "-m", "pip", "install", "--upgrade", "pip"])

    # Install requirements
    print("Installing requirements...")
    subprocess.run([pip_path, "install", "-r", "requirements.txt"])

    # Create .env file if it doesn't exist
    if not os.path.exists(".env"):
        print("Creating .env file...")
        with open(".env", "w") as f:
            f.write("""SECRET_KEY=your_secret_key_here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3

# Stripe Settings
STRIPE_PUBLIC_KEY=your_stripe_public_key
STRIPE_SECRET_KEY=your_stripe_secret_key
STRIPE_WEBHOOK_SECRET=your_stripe_webhook_secret

# Email Settings
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_email_password
""")

    # Run migrations
    print("Running migrations...")
    subprocess.run([python_path, "manage.py", "migrate"])

    # Create superuser if none exists
    print("Checking for superuser...")
    result = subprocess.run(
        [python_path, "manage.py", "shell", "-c", 
         "from django.contrib.auth import get_user_model; print(get_user_model().objects.filter(is_superuser=True).exists())"],
        capture_output=True,
        text=True
    )
    
    if "False" in result.stdout:
        print("Creating superuser...")
        print("Please enter superuser credentials:")
        subprocess.run([python_path, "manage.py", "createsuperuser"])

    # Collect static files
    print("Collecting static files...")
    subprocess.run([python_path, "manage.py", "collectstatic", "--noinput"])

    print("\nSetup complete! You can now:")
    print("1. Update the .env file with your actual settings")
    print("2. Run the development server: python manage.py runserver")
    print("3. Access the admin interface at: http://127.0.0.1:8000/admin/")

if __name__ == "__main__":
    main()
