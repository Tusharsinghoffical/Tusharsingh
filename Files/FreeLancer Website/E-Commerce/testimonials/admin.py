from django.contrib import admin
from .models import Testimonial

@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ['name', 'role', 'company', 'rating', 'is_active', 'created_at']
    list_filter = ['rating', 'is_active', 'created_at']
    search_fields = ['name', 'role', 'company', 'content']
    list_editable = ['is_active', 'rating']
    
    fieldsets = (
        ('Client Information', {
            'fields': ('name', 'role', 'company', 'avatar')
        }),
        ('Testimonial', {
            'fields': ('content', 'rating')
        }),
        ('Settings', {
            'fields': ('is_active',)
        }),
    ) 