from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import Profile, EmailVerification, SiteSettings

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'email_verified', 'admin_verified', 'created_at', 'admin_actions']
    list_filter = ['email_verified', 'admin_verified']
    search_fields = ['user__username', 'user__email', 'user__first_name', 'user__last_name']
    readonly_fields = ['user']
    
    def created_at(self, obj):
        return obj.user.date_joined.strftime('%Y-%m-%d %H:%M')
    created_at.short_description = 'Joined Date'
    
    def admin_actions(self, obj):
        if not obj.admin_verified:
            approve_url = reverse('admin_approve_verification', args=[obj.user.id])
            reject_url = reverse('admin_reject_verification', args=[obj.user.id])
            return format_html(
                '<a class="button" href="{}">Approve</a> '
                '<a class="button" href="{}" style="background: #ba2121;">Reject</a>',
                approve_url, reject_url
            )
        return "Already verified"
    admin_actions.short_description = 'Actions'

@admin.register(EmailVerification)
class EmailVerificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'email', 'status', 'created_at', 'admin_verified_at', 'admin_actions']
    list_filter = ['status', 'created_at', 'admin_verified_at']
    search_fields = ['user__username', 'email']
    readonly_fields = ['user', 'email', 'verification_key', 'created_at']
    
    def admin_verified_at(self, obj):
        if obj.admin_verified_at:
            return obj.admin_verified_at.strftime('%Y-%m-%d %H:%M')
        return '-'
    admin_verified_at.short_description = 'Admin Verified At'
    
    def admin_actions(self, obj):
        if obj.status == 'pending':
            approve_url = reverse('admin_approve_email_verification', args=[obj.id])
            reject_url = reverse('admin_reject_email_verification', args=[obj.id])
            return format_html(
                '<a class="button" href="{}">Approve</a> '
                '<a class="button" href="{}" style="background: #ba2121;">Reject</a>',
                approve_url, reject_url
            )
        return obj.status.title()
    admin_actions.short_description = 'Actions'
    
    def approve_verifications(self, request, queryset):
        for verification in queryset.filter(status='pending'):
            verification.status = 'approved'
            verification.admin_verified_by = request.user
            verification.admin_verified_at = timezone.now()
            verification.save()
            
            # Update user profile
            profile = verification.user.profile
            profile.admin_verified = True
            profile.admin_verification_date = timezone.now()
            profile.save()
        
        self.message_user(request, f"{queryset.count()} verifications approved successfully.")
    approve_verifications.short_description = "Approve selected verifications"
    
    def reject_verifications(self, request, queryset):
        for verification in queryset.filter(status='pending'):
            verification.status = 'rejected'
            verification.admin_verified_by = request.user
            verification.admin_verified_at = timezone.now()
            verification.save()
        
        self.message_user(request, f"{queryset.count()} verifications rejected successfully.")
    reject_verifications.short_description = "Reject selected verifications"
    
    actions = ['approve_verifications', 'reject_verifications']

@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ['site_name', 'contact_email']
    fieldsets = (
        ('Basic Settings', {
            'fields': ('site_name', 'site_description')
        }),
        ('Contact Information', {
            'fields': ('contact_email', 'contact_phone', 'address')
        }),
        ('Social Media', {
            'fields': ('facebook_url', 'twitter_url', 'instagram_url', 'linkedin_url')
        }),
    ) 