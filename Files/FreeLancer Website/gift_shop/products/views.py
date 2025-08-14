from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, Min, Max
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse, HttpResponse
from django.db import models
from decimal import Decimal
from .models import Product, Review
from django import forms

def product_list(request):
    # Get all available products
    products = Product.objects.filter(available=True)
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Price filtering
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)
    
    # Sorting
    sort_by = request.GET.get('sort', 'name')  # Default sort by name
    if sort_by == 'price_low':
        products = products.order_by('price')
    elif sort_by == 'price_high':
        products = products.order_by('-price')
    elif sort_by == 'newest':
        products = products.order_by('-created')
    else:  # sort_by == 'name'
        products = products.order_by('name')
    
    # Stock filtering
    in_stock = request.GET.get('in_stock')
    if in_stock:
        products = products.filter(stock__gt=0)
    
    # Pagination
    page = request.GET.get('page', 1)
    paginator = Paginator(products, 9)  # Show 9 products per page
    
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)
    
    # Get min and max prices for the filter
    price_range = Product.objects.filter(available=True).aggregate(
        min_price=models.Min('price'),
        max_price=models.Max('price')
    )
    
    context = {
        'products': products,
        'search_query': search_query,
        'min_price': min_price or '',
        'max_price': max_price or '',
        'sort_by': sort_by,
        'in_stock': in_stock,
        'price_range': price_range,
    }
    return render(request, 'products/list.html', context)

def product_detail(request, id):
    product = get_object_or_404(Product, id=id, available=True)
    # Get related products (same category or similar price range)
    price_min = product.price * Decimal('0.8')
    price_max = product.price * Decimal('1.2')
    
    related_products = Product.objects.filter(
        Q(available=True) &
        (Q(price__range=(price_min, price_max)) |
         Q(name__icontains=product.name.split()[0]))
    ).exclude(id=product.id)[:4]
    
    # Get reviews with pagination
    reviews = product.reviews.all()
    paginator = Paginator(reviews, 5)  # Show 5 reviews per page
    page = request.GET.get('page')
    try:
        reviews = paginator.page(page)
    except PageNotAnInteger:
        reviews = paginator.page(1)
    except EmptyPage:
        reviews = paginator.page(paginator.num_pages)

    # Get rating distribution
    rating_distribution = product.get_rating_distribution()
    
    return render(request, 'products/detail.html', {
        'product': product,
        'related_products': related_products,
        'reviews': reviews,
        'rating_distribution': rating_distribution
    })

@login_required
def add_review(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id, available=True)
        rating = request.POST.get('rating')
        content = request.POST.get('content')
        
        if not rating or not content:
            messages.error(request, 'Both rating and review content are required.')
            return redirect('products:product_detail', id=product_id)
            
        try:
            # Update existing review if it exists
            review = Review.objects.get(product=product, user=request.user)
            review.rating = rating
            review.content = content
            review.save()
            messages.success(request, 'Your review has been updated.')
        except Review.DoesNotExist:
            # Create new review
            Review.objects.create(
                product=product,
                user=request.user,
                rating=rating,
                content=content
            )
            messages.success(request, 'Your review has been added.')
            
        return redirect('products:product_detail', id=product_id)
    return redirect('products:product_detail', id=product_id)

@login_required
def edit_review(request, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)
    if request.method == 'POST':
        rating = request.POST.get('rating')
        content = request.POST.get('content')
        
        if rating and content:
            review.rating = rating
            review.content = content
            review.save()
            messages.success(request, 'Your review has been updated.')
        else:
            messages.error(request, 'Both rating and review content are required.')
            
    return redirect('products:product_detail', id=review.product.id)

@login_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)
    product_id = review.product.id
    review.delete()
    messages.success(request, 'Your review has been deleted.')
    return redirect('products:product_detail', id=product_id)

def product_reviews(request, product_id):
    product = get_object_or_404(Product, id=product_id, available=True)
    reviews = product.reviews.all()
    paginator = Paginator(reviews, 10)  # Show 10 reviews per page
    
    page = request.GET.get('page')
    try:
        reviews = paginator.page(page)
    except PageNotAnInteger:
        reviews = paginator.page(1)
    except EmptyPage:
        reviews = paginator.page(paginator.num_pages)
        
    return render(request, 'products/reviews.html', {
        'product': product,
        'reviews': reviews,
        'rating_distribution': product.get_rating_distribution()
    })

def product_detail_modal(request, id):
    product = get_object_or_404(Product, id=id, available=True)
    return render(request, 'products/modal_detail.html', {'product': product})

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'slug', 'description', 'price', 'image', 'stock', 'available', 'featured']

@login_required
def add_product(request):
    if not request.user.is_authenticated or not request.user.is_staff:
        return redirect('users:login')
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product added successfully!')
            return redirect('products:product_list')
    else:
        form = ProductForm()
    return render(request, 'products/add_product.html', {'form': form})

@login_required
def edit_product(request, id):
    if not request.user.is_authenticated or not request.user.is_staff:
        return redirect('users:login')
    product = get_object_or_404(Product, id=id)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully!')
            return redirect('products:product_list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'products/edit_product.html', {'form': form, 'product': product})

@login_required
def manage_products(request):
    if not request.user.is_authenticated or not request.user.is_staff:
        return redirect('users:login')
    products = Product.objects.all().order_by('-created')
    form = ProductForm()
    return render(request, 'products/manage_products.html', {'products': products, 'form': form})

@login_required
def delete_product(request, id):
    if not request.user.is_authenticated or not request.user.is_staff:
        return redirect('users:login')
    product = get_object_or_404(Product, id=id)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product deleted successfully!')
        return redirect('products:manage_products')
    return redirect('products:manage_products')
