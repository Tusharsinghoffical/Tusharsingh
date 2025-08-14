from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from django.db.models import Count, Q
from datetime import datetime, timedelta
from services.models import Service
from portfolio.models import Project
from testimonials.models import Testimonial
from contact.models import Contact
from contact.forms import ContactForm
from .forms import ProfileImageForm, ProfileUpdateForm
from .models import EmailVerification, Profile
from django.views.decorators.http import require_POST

def is_admin(user):
    return user.is_authenticated and user.is_staff

@staff_member_required
def admin_dashboard(request):
    """Comprehensive admin dashboard with all features"""
    from django.contrib.auth.models import User
    
    # Get statistics
    total_users = User.objects.count()
    new_users_today = User.objects.filter(date_joined__date=timezone.now().date()).count()
    new_users_week = User.objects.filter(date_joined__gte=timezone.now() - timedelta(days=7)).count()
    
    # Email verification stats
    pending_verifications = EmailVerification.objects.filter(status='pending').count()
    approved_today = EmailVerification.objects.filter(
        status='approved',
        admin_verified_at__date=timezone.now().date()
    ).count()
    total_verifications = EmailVerification.objects.count()
    
    # Contact messages
    total_contacts = Contact.objects.count()
    unread_contacts = Contact.objects.filter(is_read=False).count()
    new_contacts_today = Contact.objects.filter(created_at__date=timezone.now().date()).count()
    
    # Content stats
    total_services = Service.objects.count()
    active_services = Service.objects.filter(is_active=True).count()
    total_projects = Project.objects.count()
    active_projects = Project.objects.filter(is_active=True).count()
    total_testimonials = Testimonial.objects.count()
    active_testimonials = Testimonial.objects.filter(is_active=True).count()
    
    # Recent activities
    recent_users = User.objects.order_by('-date_joined')[:5]
    recent_verifications = EmailVerification.objects.order_by('-created_at')[:5]
    recent_contacts = Contact.objects.order_by('-created_at')[:5]
    
    # Pending actions
    pending_users = User.objects.filter(profile__admin_verified=False)[:10]
    pending_verifications_list = EmailVerification.objects.filter(status='pending')[:10]
    
    context = {
        # Statistics
        'total_users': total_users,
        'new_users_today': new_users_today,
        'new_users_week': new_users_week,
        'pending_verifications': pending_verifications,
        'approved_today': approved_today,
        'total_verifications': total_verifications,
        'total_contacts': total_contacts,
        'unread_contacts': unread_contacts,
        'new_contacts_today': new_contacts_today,
        'total_services': total_services,
        'active_services': active_services,
        'total_projects': total_projects,
        'active_projects': active_projects,
        'total_testimonials': total_testimonials,
        'active_testimonials': active_testimonials,
        
        # Recent activities
        'recent_users': recent_users,
        'recent_verifications': recent_verifications,
        'recent_contacts': recent_contacts,
        
        # Pending actions
        'pending_users': pending_users,
        'pending_verifications_list': pending_verifications_list,
    }
    
    return render(request, 'admin/admin_dashboard.html', context)

def home(request):
    """Homepage view with all sections"""
    services = Service.objects.filter(is_active=True).order_by('order')[:6]
    projects = Project.objects.filter(is_active=True).order_by('-created_at')[:6]
    testimonials = Testimonial.objects.filter(is_active=True).order_by('-created_at')[:3]
    
    # Contact form for home page
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact = form.save()
            # You can add email notification here if needed
            return render(request, 'core/home.html', {
                'services': services,
                'projects': projects,
                'testimonials': testimonials,
                'form': ContactForm(),  # Reset form after successful submission
                'contact_success': True
            })
    else:
        form = ContactForm()
    
    context = {
        'services': services,
        'projects': projects,
        'testimonials': testimonials,
        'form': form,
    }
    return render(request, 'core/home.html', context)

@login_required
def dashboard(request):
    """User dashboard view"""
    user_contacts = Contact.objects.filter(user=request.user).order_by('-created_at')
    profile = request.user.profile
    
    if request.method == 'POST':
        form = ProfileImageForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile image updated successfully!')
            return redirect('core:dashboard')
        else:
            messages.error(request, 'Error updating profile image. Please try again.')
    else:
        form = ProfileImageForm(instance=profile)
    
    context = {
        'user_contacts': user_contacts,
        'profile_form': form,
    }
    return render(request, 'core/dashboard.html', context)

@login_required
def profile_view(request):
    profile = request.user.profile
    if request.method == 'POST':
        update_form = ProfileUpdateForm(request.POST, instance=profile, user=request.user)
        image_form = ProfileImageForm(request.POST, request.FILES, instance=profile)
        if update_form.is_valid() and image_form.is_valid():
            update_form.save()
            image_form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile:profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        update_form = ProfileUpdateForm(instance=profile, user=request.user)
        image_form = ProfileImageForm(instance=profile)
    return render(request, 'profile/profile.html', {
        'update_form': update_form,
        'image_form': image_form,
    })

def about(request):
    """About page view"""
    return render(request, 'core/about.html')

def email_verification_sent(request):
    """Custom email verification sent page"""
    return render(request, 'account/email_verification_sent.html')

@user_passes_test(is_admin)
@require_POST
def approve_verification(request, user_id):
    """Admin view to approve user verification"""
    user = get_object_or_404(get_user_model(), id=user_id)
    profile = user.profile
    
    profile.admin_verified = True
    profile.admin_verification_date = timezone.now()
    profile.admin_verification_notes = f"Approved by {request.user.username} on {timezone.now().strftime('%Y-%m-%d %H:%M')}"
    profile.save()
    
    # Update email verification if exists
    verification = EmailVerification.objects.filter(user=user, status='pending').first()
    if verification:
        verification.status = 'approved'
        verification.admin_verified_by = request.user
        verification.admin_verified_at = timezone.now()
        verification.admin_notes = f"Approved by {request.user.username}"
        verification.save()
    
    messages.success(request, f'User {user.username} has been approved successfully!')
    return HttpResponseRedirect(reverse('admin:core_profile_changelist'))

@user_passes_test(is_admin)
@require_POST
def reject_verification(request, user_id):
    """Admin view to reject user verification"""
    user = get_object_or_404(get_user_model(), id=user_id)
    profile = user.profile
    
    profile.admin_verified = False
    profile.admin_verification_notes = f"Rejected by {request.user.username} on {timezone.now().strftime('%Y-%m-%d %H:%M')}"
    profile.save()
    
    # Update email verification if exists
    verification = EmailVerification.objects.filter(user=user, status='pending').first()
    if verification:
        verification.status = 'rejected'
        verification.admin_verified_by = request.user
        verification.admin_verified_at = timezone.now()
        verification.admin_notes = f"Rejected by {request.user.username}"
        verification.save()
    
    messages.warning(request, f'User {user.username} has been rejected.')
    return HttpResponseRedirect(reverse('admin:core_profile_changelist'))

@user_passes_test(is_admin)
@require_POST
def approve_email_verification(request, verification_id):
    """Admin view to approve email verification"""
    verification = get_object_or_404(EmailVerification, id=verification_id)
    
    verification.status = 'approved'
    verification.admin_verified_by = request.user
    verification.admin_verified_at = timezone.now()
    verification.admin_notes = f"Approved by {request.user.username}"
    verification.save()
    
    # Update user profile
    profile = verification.user.profile
    profile.admin_verified = True
    profile.admin_verification_date = timezone.now()
    profile.save()
    
    messages.success(request, f'Email verification for {verification.user.username} has been approved!')
    return HttpResponseRedirect(reverse('admin:core_emailverification_changelist'))

@user_passes_test(is_admin)
@require_POST
def reject_email_verification(request, verification_id):
    """Admin view to reject email verification"""
    verification = get_object_or_404(EmailVerification, id=verification_id)
    
    verification.status = 'rejected'
    verification.admin_verified_by = request.user
    verification.admin_verified_at = timezone.now()
    verification.admin_notes = f"Rejected by {request.user.username}"
    verification.save()
    
    messages.warning(request, f'Email verification for {verification.user.username} has been rejected.')
    return HttpResponseRedirect(reverse('admin:core_emailverification_changelist')) 