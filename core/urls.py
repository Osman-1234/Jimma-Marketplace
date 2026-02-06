from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='index'),
    path('signup/', views.signup, name='signup'), # Added signup url
    path('products/', views.product_list, name='product_list'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('product/review/<int:product_id>/', views.product_review_submit, name='product_review_submit'),
    path('category/<slug:slug>/', views.category_products, name='category_products'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('cart/remove/<int:product_id>/', views.cart_remove, name='cart_remove'),
    path('checkout/', views.checkout, name='checkout'),
    path('order/success/<int:order_id>/', views.order_success, name='order_success'),
    
    # Vendor URLs
    path('vendor/register/', views.vendor_register, name='vendor_register'),
    path('vendor/dashboard/', views.vendor_dashboard, name='vendor_dashboard'),
    path('vendor/product/add/', views.vendor_product_add, name='vendor_product_add'),
    path('vendor/product/edit/<int:pk>/', views.vendor_product_edit, name='vendor_product_edit'),
    path('vendor/product/delete/<int:pk>/', views.vendor_product_delete, name='vendor_product_delete'),
    path('vendor/order/status/<int:order_id>/', views.vendor_order_status_update, name='vendor_order_status_update'),
    
    # Essential Pages
    path('about/', views.about_us, name='about_us'),
    path('how-it-works/', views.how_it_works, name='how_it_works'),
    path('seller-info/', views.seller_info, name='seller_info'),
    path('delivery-info/', views.delivery_info, name='delivery_info'),
    path('contact/', views.contact_us, name='contact_us'),
    path('track-order/', views.track_order, name='track_order'),
    
    # Blog/Articles
    path('blog/', views.article_list, name='article_list'),
    path('blog/<slug:slug>/', views.article_detail, name='article_detail'),
]
