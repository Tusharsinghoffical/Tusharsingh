from django.contrib import admin
from django.urls import path
from home import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    
     
    path('home/', views.home, name='home'),  # Moved home to its own path
    # path('home/', views.index, name='index'),     # ✅ Corrected
    

    path("profile/", views.profile_view, name="profile"),
    path("attendance/", views.attendance, name="attendance"),
    path("mark_attendance/", views.mark_attendance, name="mark_attendance"),
    path('attendance/history/', views.attendance_history, name='attendance_history'),
    path("attendance/report/", views.attendance_report, name="attendance_report"),
    path("attendance/export/", views.export_attendance_csv, name="export_attendance_csv"),
    



]
