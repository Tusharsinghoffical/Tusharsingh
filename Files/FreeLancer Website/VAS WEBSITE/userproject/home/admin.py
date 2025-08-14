from django.contrib import admin  # type: ignore
from django.contrib.auth.models import User, Group  # type: ignore
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin  # type: ignore
from django.http import HttpResponse  # type: ignore
from home.models import Profile, Attendance
from import_export.admin import ImportExportModelAdmin  # type: ignore
from import_export import resources, fields  # type: ignore
from import_export.widgets import ForeignKeyWidget  # type: ignore
import csv

# ✅ Inline Profile Admin
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'

# ✅ Export Users to CSV
def export_user_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="users_export.csv"'
    writer = csv.writer(response)
    writer.writerow(['Username', 'Email', 'First Name', 'Last Name', 'Is Staff', 'Phone', 'Position', 'Address'])

    for user in queryset:
        profile = Profile.objects.filter(user=user).first()
        writer.writerow([
            user.username,
            user.email,
            user.first_name,
            user.last_name,
            user.is_staff,
            profile.phone if profile else '',
            profile.position if profile else '',
            profile.address if profile else '',
        ])
    return response

export_user_csv.short_description = "Export Selected Users to CSV"

# ✅ User Import Resource
class CustomUserResource(resources.ModelResource):
    first_name = fields.Field(attribute='first_name', column_name='First Name')
    last_name = fields.Field(attribute='last_name', column_name='Last Name')
    email = fields.Field(attribute='email', column_name='Email')
    username = fields.Field(attribute='username', column_name='Username')

    class Meta:
        model = User
        import_id_fields = ['username']
        fields = ('username', 'first_name', 'last_name', 'email')
        export_order = ('username', 'first_name', 'last_name', 'email')

# ✅ Profile Import Resource
class ProfileResource(resources.ModelResource):
    user = fields.Field(
        column_name='Username',
        attribute='user',
        widget=ForeignKeyWidget(User, 'username')
    )
    phone = fields.Field(attribute='phone', column_name='Phone')
    position = fields.Field(attribute='position', column_name='Position')
    address = fields.Field(attribute='address', column_name='Address')

    class Meta:
        model = Profile
        import_id_fields = ['user']
        fields = ('user', 'phone', 'position', 'address')
        export_order = ('user', 'phone', 'position', 'address')

# ✅ Custom User Admin
class CustomUserAdmin(ImportExportModelAdmin):
    resource_class = CustomUserResource
    inlines = [ProfileInline]
    actions = [export_user_csv]
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff']
    search_fields = ['username', 'email']

# ✅ Register Updated Admin
admin.site.unregister(User)
admin.site.unregister(Group)
admin.site.register(User, CustomUserAdmin)

# ✅ Profile Admin
@admin.register(Profile)
class ProfileAdmin(ImportExportModelAdmin):
    resource_class = ProfileResource
    list_display = ('user', 'phone', 'position')

# ✅ Attendance Export

def export_attendance_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="attendance_export.csv"'
    writer = csv.writer(response)
    writer.writerow(['Username', 'Email', 'Date', 'Check-In', 'Check-Out', 'Location', 'QR Code'])

    for record in queryset:
        writer.writerow([
            record.user.username,
            record.email,
            record.date,
            record.check_in,
            record.check_out,
            record.location_name,
            record.qr_code,
        ])
    return response

export_attendance_csv.short_description = "Export Selected Attendance Records to CSV"

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'check_in', 'check_out', 'location_name')
    search_fields = ('user__username', 'location_name', 'email')
    list_filter = ('date', 'user')
    actions = [export_attendance_csv]
