from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='index'),
    path('products/', views.product_list, name='product_list'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('category/<slug:slug>/', views.category_products, name='category_products'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('cart/remove/<int:product_id>/', views.cart_remove, name='cart_remove'),
    path('checkout/', views.checkout, name='checkout'),
    path('order/success/<int:order_id>/', views.order_success, name='order_success'),
    path('vendor/register/', views.vendor_register, name='vendor_register'),
    path('vendor/dashboard/', views.vendor_dashboard, name='vendor_dashboard'),
]
