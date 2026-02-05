from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Category, Product, Vendor, Order, OrderItem, Profile
from django.contrib import messages
from django.db.models import Q

def home(request):
    categories = Category.objects.all()[:6]
    featured_products = Product.objects.filter(is_available=True)[:8]
    return render(request, 'core/index.html', {
        'categories': categories,
        'featured_products': featured_products,
    })

def product_list(request):
    query = request.GET.get('q')
    products = Product.objects.filter(is_available=True)
    if query:
        products = products.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query)
        )
    return render(request, 'core/product_list.html', {'products': products})

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_available=True)
    return render(request, 'core/product_detail.html', {'product': product})

def category_products(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = category.products.filter(is_available=True)
    return render(request, 'core/category_products.html', {'category': category, 'products': products})

# Basic Cart System using Session
def get_cart(request):
    cart = request.session.get('cart', {})
    return cart

def cart_add(request, product_id):
    cart = get_cart(request)
    product_id_str = str(product_id)
    if product_id_str in cart:
        cart[product_id_str] += 1
    else:
        cart[product_id_str] = 1
    request.session['cart'] = cart
    messages.success(request, "Product added to cart")
    return redirect('cart_detail')

def cart_remove(request, product_id):
    cart = get_cart(request)
    product_id_str = str(product_id)
    if product_id_str in cart:
        del cart[product_id_str]
        request.session['cart'] = cart
    return redirect('cart_detail')

def cart_detail(request):
    cart = get_cart(request)
    cart_items = []
    total = 0
    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, id=product_id)
        subtotal = product.price * quantity
        total += subtotal
        cart_items.append({'product': product, 'quantity': quantity, 'subtotal': subtotal})
    return render(request, 'core/cart_detail.html', {'cart_items': cart_items, 'total': total})

def checkout(request):
    cart = get_cart(request)
    if not cart:
        return redirect('product_list')
    
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        payment_method = request.POST.get('payment_method')
        
        total = 0
        order_items = []
        for product_id, quantity in cart.items():
            product = get_object_or_404(Product, id=product_id)
            total += product.price * quantity
            order_items.append((product, quantity, product.price))
        
        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            full_name=full_name,
            email=email,
            phone=phone,
            address=address,
            total_price=total,
            payment_method=payment_method
        )
        
        for product, quantity, price in order_items:
            OrderItem.objects.create(order=order, product=product, quantity=quantity, price=price)
        
        request.session['cart'] = {}
        return redirect('order_success', order_id=order.id)
        
    return render(request, 'core/checkout.html')

def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'core/order_success.html', {'order': order})

@login_required
def vendor_register(request):
    if hasattr(request.user, 'vendor'):
        return redirect('vendor_dashboard')
    
    if request.method == 'POST':
        business_name = request.POST.get('business_name')
        description = request.POST.get('description')
        address = request.POST.get('address')
        phone = request.POST.get('phone')
        
        Vendor.objects.create(
            user=request.user,
            business_name=business_name,
            description=description,
            address=address,
            phone=phone
        )
        # Update user role
        profile, created = Profile.objects.get_or_create(user=request.user)
        profile.role = 'seller'
        profile.save()
        
        messages.success(request, "Vendor registration successful. Wait for admin verification.")
        return redirect('vendor_dashboard')
        
    return render(request, 'core/vendor_register.html')

@login_required
def vendor_dashboard(request):
    vendor = get_object_or_404(Vendor, user=request.user)
    products = vendor.products.all()
    orders = OrderItem.objects.filter(product__vendor=vendor).select_related('order')
    return render(request, 'core/vendor_dashboard.html', {'vendor': vendor, 'products': products, 'orders': orders})