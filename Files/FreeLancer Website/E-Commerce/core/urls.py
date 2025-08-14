from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('about/', views.about, name='about'),
    path('email-verification-sent/', views.email_verification_sent, name='email_verification_sent'),
    
    # Admin verification URLs
    path('admin/approve-verification/<int:user_id>/', views.approve_verification, name='approve_verification'),
    path('admin/reject-verification/<int:user_id>/', views.reject_verification, name='reject_verification'),
    path('admin/approve-email-verification/<int:verification_id>/', views.approve_email_verification, name='approve_email_verification'),
    path('admin/reject-email-verification/<int:verification_id>/', views.reject_email_verification, name='reject_email_verification'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
] 