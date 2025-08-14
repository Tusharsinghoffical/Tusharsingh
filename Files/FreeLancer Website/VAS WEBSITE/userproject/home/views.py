from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import CustomUserForm
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from datetime import timedelta
from django.utils.timezone import localtime
from django.db.models import Count
from django.db.models.functions import TruncWeek, TruncMonth, TruncYear
import json
import csv
from django.contrib.admin.views.decorators import staff_member_required
from .models import Attendance, Profile
from .forms import ProfileForm
from django.contrib.auth.models import User
from django.utils.timezone import now
from django.contrib.sessions.models import Session
from django.contrib.auth.forms import UserCreationForm
from django.core.paginator import Paginator
from django.db.models import Q
from django import forms
from .forms import UserForm, ProfileForm
from django.conf import settings


@login_required
def home(request):
    return redirect('redirect_after_login')


# ✅ Login View
def loginUser(request):
    if request.user.is_authenticated:
        return redirect('redirect_after_login')

    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('redirect_after_login')
        else:
            messages.error(request, "Invalid username or password")
    return render(request, 'login.html')

# ✅ Logout View


def logoutUser(request):
    logout(request)
    return redirect(settings.LOGOUT_REDIRECT_URL)


@login_required
def index(request):
    return render(request, 'index.html')


# ✅ Homepage (Dashboard)
@login_required
def redirect_after_login(request):
    if request.user.is_staff:
        return redirect('admin_dashboard')
    else:
        return redirect('user_dashboard')


# Create account
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})


class RegisterForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'form-control',
                'placeholder': field.label
            })


# ✅ Admin Section

@login_required
def admin_dashboard(request):
    return render(request, 'admin_dashboard.html')


def admin_reports(request):
    now = timezone.now()
    recent_time_threshold = now - timedelta(days=7)

    context = {
        'total_users': User.objects.count(),
        'active_users': User.objects.filter(is_active=True).count(),
        'staff_users': User.objects.filter(is_staff=True).count(),
        'recent_logins': User.objects.exclude(last_login=None).order_by('-last_login')[:10],
        'recent_signups': User.objects.order_by('-date_joined')[:10],

        'now': now,
    }

    return render(request, 'admin_reports.html', context)


def admin_dashboard_view(request):
    total_users = User.objects.count()
    active_sessions = Session.objects.filter(
        expire_date__gte=timezone.now()).count()

    recent_activities = [
        {'user': 'admin', 'action': 'Logged In', 'timestamp': '2025-07-07 18:20'},
        {'user': 'editor', 'action': 'Edited Profile',
            'timestamp': '2025-07-07 18:10'},
    ]

    return render(request, 'admin_dashboard.html', {
        'total_users': total_users,
        'active_sessions': active_sessions,
        'recent_activities': recent_activities
    })


# ✅ User Dashboard

@login_required
def user_list_view(request):
    query = request.GET.get('q', '')
    users = User.objects.all()

    if query:
        users = users.filter(
            Q(username__icontains=query) |
            Q(email__icontains=query)
        )

    paginator = Paginator(users, 20)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'manage_users.html', {
        'page_obj': page_obj,
        'query': query
    })


def attendance_report_view(request):
    users = User.objects.all()
    staff_users = users.filter(is_staff=True)  

    return render(request, 'attendance_report.html', {
        'users': users,
        'staff_users_count': staff_users.count(),  
    })


def download_user_csv(request, user_id):  
    user = User.objects.get(pk=user_id)

    response = HttpResponse(
        content_type='text/csv',
        headers={
            'Content-Disposition': f'attachment; filename="user_{user.username}.csv"'},
    )

    writer = csv.writer(response)
    writer.writerow(['ID', 'Username', 'Email', 'First Name', 'Last Name'])
    writer.writerow([user.id, user.username, user.email,
                    user.first_name, user.last_name])

    return response


def download_users_csv_view(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="users.csv"'

    writer = csv.writer(response)
    writer.writerow(['Username', 'Email', 'Is Staff',
                    'Is Active', 'Date Joined'])

    for user in User.objects.all():
        writer.writerow([
            user.username,
            user.email,
            user.is_staff,
            user.is_active,
            user.date_joined.strftime("%Y-%m-%d %H:%M:%S")
        ])

    return response


def user_detail_view(request, user_id):
    user = get_object_or_404(User, id=user_id)
    return render(request, 'user_detail.html', {'user': user})


@login_required
def manage_users(request):
    query = request.GET.get('q', '')
    users = User.objects.all()

    if query:
        users = users.filter(
            Q(username__icontains=query) | Q(email__icontains=query)
        )

    paginator = Paginator(users, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'amanage_users.html', {
        'users': page_obj,
        'query': query,
    })


def manage_users_view(request):
    users = User.objects.all()
    return render(request, 'manage_users.html', {'users': users})


def is_admin(user):
    return user.is_staff or user.is_superuser


# @user_passes_test(is_admin)
# def manage_users_view(request):
#     users = User.objects.all()
#     return render(request, 'manage_users.html', {'users': users})

# @login_required
# def manage_users_view(request):
#     users = User.objects.all()
#     return render(request, 'manage_users.html', {'users': users})


def is_admin(user):
    return user.is_superuser or user.is_staff


# manage files

@user_passes_test(is_admin)
def manage_users_view(request):
    users = User.objects.all()
    return render(request, 'manage_users.html', {'users': users})


@user_passes_test(is_admin)
def edit_user_view(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        user.username = request.POST.get('username')
        user.email = request.POST.get('email')
        user.save()
        return redirect('manage_users')
    return render(request, 'edit_user.html', {'user': user})


@user_passes_test(is_admin)
def delete_user_view(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.delete()
    return redirect('manage_users')


# User dashbaord

@login_required
def user_dashboard(request):
    profile = request.user.profile  
    return render(request, 'user_dashboard.html', {
        'user': request.user,
        'profile': profile,
    })


# Profile pages

@login_required
def profile_view(request):
    user = request.user
    profile, created = Profile.objects.get_or_create(user=user)

    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=user)
        profile_form = ProfileForm(request.POST, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "✅ Profile updated successfully!")
            return redirect('profile')
    else:
        user_form = UserForm(instance=user)
        profile_form = ProfileForm(instance=profile)

    return render(request, 'profile.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'profile': profile,
        'user': user,
    })


@login_required
def add_user_view(request):
    if request.method == 'POST':
        form = CustomUserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            messages.success(request, "✅ New user added successfully!")
            return redirect('manage_users')
    else:
        form = CustomUserForm()

    return render(request, 'add_user.html', {'form': form})


@login_required
def reports_view(request):
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    staff_users = User.objects.filter(is_staff=True).count()
    recent_logins = User.objects.filter(
        last_login__isnull=False).order_by('-last_login')[:5]

    context = {
        'total_users': total_users,
        'active_users': active_users,
        'staff_users': staff_users,
        'recent_logins': recent_logins,
        'now': now(),
    }
    return render(request, 'reports.html', context)


@login_required
def report_view(request):
    now = timezone.now()
    recent_logins = User.objects.filter(
        last_login__isnull=False).order_by('-last_login')[:10]
    recent_signups = User.objects.filter(
        # last 7 days
        date_joined__gte=now - timedelta(days=7)).order_by('-date_joined')

    context = {
        'total_users': User.objects.count(),
        'active_users': User.objects.filter(is_active=True).count(),
        'staff_users': User.objects.filter(is_staff=True).count(),
        'recent_logins': recent_logins,
        'recent_signups': recent_signups,
        'now': now,
    }
    return render(request, 'report.html', context)


# ✅ Attendance Page
@login_required
def attendance(request):
    user = request.user
    try:
        profile = Profile.objects.get(user=user)
    except Profile.DoesNotExist:
        profile = None

    context = {
        'full_name': user.get_full_name() or user.username,
        'email': user.email,
        'username': user.username,
        'user_id': user.id,
        'profile': profile,
    }
    return render(request, "attendance.html", context)


@login_required
def attendance_history(request):
    records = Attendance.objects.filter(
        user=request.user).order_by('-date', '-time')

    context = {
        'records': records,
        'name': request.user.get_full_name() or request.user.username,
        'email': request.user.email,
        'username': request.user.username,
        'user_id': request.user.id,
    }
    return render(request, 'attendance_history.html', context)


@login_required
def qr_attendance_view(request):
    user = request.user

    context = {
        "user": user,
        "name": user.get_full_name() or user.username,
        "email": user.email,
        "username": user.username,
        "user_id": user.id,
    }
    return render(request, "attendance.html", context)


@csrf_exempt
@login_required
def mark_attendance(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            qr_data = data.get("qr_data")
            location_name = data.get("location_name")
            mode = data.get("mode", "check_in")
            today = timezone.now().date()
            now_time = localtime().time()

            ALLOWED_QR_CODE = "https://www.venusjewel.com/"
            if qr_data != ALLOWED_QR_CODE:
                return JsonResponse({"error": "❌ Invalid QR Code scanned."}, status=403)

            record, created = Attendance.objects.get_or_create(
                user=request.user,
                date=today,
                defaults={
                    "name": request.user.get_full_name() or request.user.username,
                    "email": request.user.email,
                    "qr_code": qr_data,
                    "location_name": location_name,
                }
            )

            if mode == "check_in":
                if record.check_in:
                    return JsonResponse({"message": "ℹ️ Already Checked In today."})
                record.check_in = now_time
                record.qr_code = qr_data
                record.location_name = location_name
                record.save()
                return JsonResponse({"message": "✅ Check-In marked successfully!"})

            elif mode == "check_out":
                if not record.check_in:
                    return JsonResponse({"message": "⚠️ You need to Check-In first."})
                if record.check_out:
                    return JsonResponse({"message": "ℹ️ Already Checked Out today."})
                record.check_out = now_time
                record.save()
                return JsonResponse({"message": "✅ Check-Out marked successfully!"})

            else:
                return JsonResponse({"error": "❌ Invalid mode."}, status=400)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Method Not Allowed"}, status=405)


@login_required
def attendance_report(request):
    user = request.user

    weekly = Attendance.objects.filter(user=user).annotate(
        week=TruncWeek('date')
    ).values('week').annotate(total=Count('id')).order_by('-week')

    monthly = Attendance.objects.filter(user=user).annotate(
        month=TruncMonth('date')
    ).values('month').annotate(total=Count('id')).order_by('-month')

    yearly = Attendance.objects.filter(user=user).annotate(
        year=TruncYear('date')
    ).values('year').annotate(total=Count('id')).order_by('-year')

    return render(request, "attendance_report.html", {
        "weekly": weekly,
        "monthly": monthly,
        "yearly": yearly,
    })


@login_required
def export_attendance_csv(request):
    records = Attendance.objects.filter(user=request.user).order_by('-date')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="my_attendance.csv"'

    writer = csv.writer(response)
    writer.writerow(['Date', 'Check-In', 'Check-Out', 'Location', 'QR Code'])

    for record in records:
        writer.writerow([
            record.date,
            record.check_in,
            record.check_out,
            record.location_name,
            record.qr_code,
        ])

    return response


@login_required
def user_attendance_detail_view(request, user_id):
    user = get_object_or_404(User, id=user_id)
    records = Attendance.objects.filter(user=user).order_by('-date')

    return render(request, 'user_attendance_detail.html', {
        'user_obj': user,
        'records': records,
    })


@staff_member_required
def user_attendance_detail(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    records = Attendance.objects.filter(user=user).order_by('-date')

    context = {
        'user_obj': user,
        'records': records,
    }
    return render(request, 'user_attendance_detail.html', context)


@login_required
def user_attendance(request):
    user = request.user
    attendances = Attendance.objects.filter(user=user).order_by('-date')
    return render(request, 'user_attendance.html', {'attendances': attendances})
