from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from utils.emails import send_welcome_email
from django.contrib.auth.models import User
from django.contrib import messages
from django import forms
from products.models import Product
from orders.models import Order

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            # Send welcome email
            send_welcome_email(user)
            return redirect('products:product_list')
    else:
        form = UserCreationForm()
    return render(request, 'users/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('products:product_list')
    else:
        form = AuthenticationForm()
    return render(request, 'users/login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    return redirect('products:product_list')

@login_required
def profile(request):
    return render(request, 'users/profile.html')

class ProfileForm(forms.ModelForm):
    address = forms.CharField(max_length=255, required=False)
    phone = forms.CharField(max_length=20, required=False)
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

@login_required
def edit_profile(request):
    user = request.user
    profile = getattr(user, 'profile', None)
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            # Save address and phone if profile exists
            if profile:
                profile.address = form.cleaned_data.get('address', '')
                profile.phone = form.cleaned_data.get('phone', '')
                profile.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('users:profile')
    else:
        initial = {'address': profile.address if profile else '', 'phone': profile.phone if profile else ''}
        form = ProfileForm(instance=user, initial=initial)
    return render(request, 'users/edit_profile.html', {'form': form})

@login_required
def admin_dashboard(request):
    if not request.user.is_staff:
        return redirect('users:login')
    user_count = User.objects.count()
    product_count = Product.objects.count()
    order_count = Order.objects.count()
    search_query = request.GET.get('q', '')
    users = User.objects.filter(username__icontains=search_query) if search_query else User.objects.all()
    products = Product.objects.filter(name__icontains=search_query) if search_query else Product.objects.all()
    orders = Order.objects.filter(id__icontains=search_query) if search_query else Order.objects.all()
    return render(request, 'users/admin_dashboard.html', {
        'user_count': user_count,
        'product_count': product_count,
        'order_count': order_count,
        'users': users[:10],
        'products': products[:10],
        'orders': orders[:10],
        'search_query': search_query
    })
