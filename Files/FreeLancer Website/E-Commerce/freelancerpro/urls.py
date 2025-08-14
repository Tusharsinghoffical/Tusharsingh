"""
URL configuration for freelancerpro project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core.views import approve_verification, reject_verification, approve_email_verification, reject_email_verification

urlpatterns = [
    path('admin/', admin.site.urls),
    path('admin/approve-verification/<int:user_id>/', approve_verification, name='admin_approve_verification'),
    path('admin/reject-verification/<int:user_id>/', reject_verification, name='admin_reject_verification'),
    path('admin/approve-email-verification/<int:verification_id>/', approve_email_verification, name='admin_approve_email_verification'),
    path('admin/reject-email-verification/<int:verification_id>/', reject_email_verification, name='admin_reject_email_verification'),
    path('', include('core.urls')),
    path('services/', include('services.urls')),
    path('portfolio/', include('portfolio.urls')),
    path('testimonials/', include('testimonials.urls')),
    path('contact/', include('contact.urls')),
    path('accounts/', include('allauth.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) 