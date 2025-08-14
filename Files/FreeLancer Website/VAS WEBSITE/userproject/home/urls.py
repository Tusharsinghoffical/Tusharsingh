from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from home import views
from .views import (
    add_user_view, attendance_report_view, download_users_csv_view,
    manage_users_view, user_detail_view, download_user_csv,
    edit_user_view, delete_user_view, user_list_view
)

urlpatterns = [
    # ✅ Admin Site
    path('admin/', admin.site.urls),

    # ✅ Landing → Redirects after login
    path('', views.redirect_after_login, name='home'),
    path('redirect-after-login/', views.redirect_after_login, name='redirect_after_login'),

    # ✅ Dashboards
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('user-dashboard/', views.user_dashboard, name='user_dashboard'),

    # ✅ Authentication
    path('login/', views.loginUser, name='login'),
    path('logout/', views.logoutUser, name='logout'),
    path('register/', views.register, name='register'),

    # ✅ Profile
    path('profile/', views.profile_view, name='profile'),

    # ✅ Attendance
    path('attendance/', views.attendance, name='attendance'),
    path('mark_attendance/', views.mark_attendance, name='mark_attendance'),
    path('attendance/history/', views.attendance_history, name='attendance_history'),
    path('attendance/report/', attendance_report_view, name='attendance_report'),
    path('attendance/export/', views.export_attendance_csv, name='export_attendance_csv'),
    path('attendance/user/<int:user_id>/', views.user_attendance_detail, name='user_attendance_detail'),

    # ✅ User's own attendance
    path('user-attendance/', views.user_attendance, name='user_attendance'),

    # ✅ Reports
    path('reports/', views.reports_view, name='reports'),

    # ✅ User Management
    path("add-user/", views.add_user_view, name="add_user"),
    path('manage-users/', manage_users_view, name='manage_users'),
    path('edit-user/<int:user_id>/', edit_user_view, name='edit_user'),
    path('delete-user/<int:user_id>/', delete_user_view, name='delete_user'),
    path('users/', user_list_view, name='user_list'),
    path('user/<int:user_id>/', user_detail_view, name='user_details'),

    # ✅ CSV Downloads
    path('download-csv/', download_users_csv_view, name='download_csv'),
    path('download-users/', download_users_csv_view, name='download_users_csv_view'),
    path('download-user/<int:user_id>/', download_user_csv, name='download_user_csv'),

    # ✅ Password Reset
    path('password-reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]
