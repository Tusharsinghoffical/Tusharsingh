from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='profile_images/', null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=100, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    email_verified = models.BooleanField(default=False)
    email_verification_date = models.DateTimeField(null=True, blank=True)
    admin_verified = models.BooleanField(default=False)
    admin_verification_date = models.DateTimeField(null=True, blank=True)
    admin_verification_notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    def get_image_url(self):
        """Return the profile image URL or a default avatar"""
        if self.image and hasattr(self.image, 'url'):
            return self.image.url
        return '/static/images/default-avatar.png'  # Default avatar path

class EmailVerification(models.Model):
    VERIFICATION_STATUS = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    email = models.EmailField()
    verification_key = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=VERIFICATION_STATUS, default='pending')
    admin_notes = models.TextField(blank=True)
    admin_verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='verifications_approved')
    admin_verified_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Email verification for {self.user.username} - {self.status}"
    
    class Meta:
        ordering = ['-created_at']

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

class SiteSettings(models.Model):
    site_name = models.CharField(max_length=100, default='FreelancerPro')
    site_description = models.TextField(blank=True)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    facebook_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    
    def __str__(self):
        return f"Site Settings"
    
    class Meta:
        verbose_name_plural = "Site Settings" 