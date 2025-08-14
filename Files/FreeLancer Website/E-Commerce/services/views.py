from django.shortcuts import render, get_object_or_404
from .models import Service

def service_list(request):
    """List all active services with category filtering"""
    category = request.GET.get('category', 'all')
    
    if category == 'all':
        services = Service.objects.filter(is_active=True).order_by('order')
    else:
        services = Service.objects.filter(is_active=True, category=category).order_by('order')
    
    return render(request, 'services/service_list.html', {
        'services': services,
        'current_category': category
    })

def service_detail(request, pk):
    """Show service details"""
    service = get_object_or_404(Service, pk=pk, is_active=True)
    return render(request, 'services/service_detail.html', {'service': service}) 