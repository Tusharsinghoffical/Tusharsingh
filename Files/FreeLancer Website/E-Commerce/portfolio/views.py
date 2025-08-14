from django.shortcuts import render, get_object_or_404
from .models import Project

def portfolio_list(request):
    """List all active projects with category filtering"""
    category = request.GET.get('category', 'all')
    
    if category == 'all':
        projects = Project.objects.filter(is_active=True).order_by('-is_featured', '-created_at')
    else:
        projects = Project.objects.filter(is_active=True, category=category).order_by('-is_featured', '-created_at')
    
    return render(request, 'portfolio/portfolio_list.html', {
        'projects': projects,
        'current_category': category
    })

def portfolio_detail(request, pk):
    """Show project details"""
    project = get_object_or_404(Project, pk=pk, is_active=True)
    return render(request, 'portfolio/portfolio_detail.html', {'project': project}) 