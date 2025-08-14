from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('<int:id>/', views.product_detail, name='product_detail'),
    path('<int:id>/modal/', views.product_detail_modal, name='product_detail_modal'),
    path('<int:product_id>/reviews/', views.product_reviews, name='product_reviews'),
    path('<int:product_id>/review/add/', views.add_review, name='add_review'),
    path('review/<int:review_id>/edit/', views.edit_review, name='edit_review'),
    path('review/<int:review_id>/delete/', views.delete_review, name='delete_review'),
    path('add/', views.add_product, name='add_product'),
    path('<int:id>/edit/', views.edit_product, name='edit_product'),
    path('<int:id>/delete/', views.delete_product, name='delete_product'),
    path('manage/', views.manage_products, name='manage_products'),
]
