from django.contrib import admin
from .models import ServiceFeature, Service

@admin.register(ServiceFeature)
class ServiceFeatureAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']
    list_filter = ['name']

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'price', 'price_type', 'order', 'is_popular', 'is_active', 'created_at']
    list_filter = ['category', 'price_type', 'is_popular', 'is_active', 'created_at']
    search_fields = ['title', 'description']
    list_editable = ['is_popular', 'is_active', 'order']
    prepopulated_fields = {'title': ('title',)}
    filter_horizontal = ['features']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'category', 'icon')
        }),
        ('Pricing', {
            'fields': ('price', 'price_type', 'duration', 'team_size', 'delivery_time')
        }),
        ('Features', {
            'fields': ('features', 'additional_info')
        }),
        ('Settings', {
            'fields': ('is_popular', 'is_active', 'order')
        }),
    ) 