from django.contrib import admin
from .models import ProjectFeature, Project

@admin.register(ProjectFeature)
class ProjectFeatureAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']
    list_filter = ['name']

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'client', 'is_featured', 'is_active', 'created_at']
    list_filter = ['category', 'is_featured', 'is_active', 'created_at']
    search_fields = ['title', 'description', 'client']
    list_editable = ['is_featured', 'is_active']
    prepopulated_fields = {'title': ('title',)}
    filter_horizontal = ['features']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'detailed_description', 'category', 'client')
        }),
        ('Media', {
            'fields': ('image',)
        }),
        ('Technical Details', {
            'fields': ('technologies', 'features', 'challenges')
        }),
        ('Links', {
            'fields': ('live_url', 'github_url')
        }),
        ('Settings', {
            'fields': ('is_featured', 'is_active')
        }),
    ) 