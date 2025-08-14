from django.shortcuts import render
from .models import Testimonial

def testimonial_list(request):
    """List all active testimonials"""
    testimonials = Testimonial.objects.filter(is_active=True).order_by('-created_at')
    return render(request, 'testimonials/testimonial_list.html', {'testimonials': testimonials}) 