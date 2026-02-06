from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from .models import Category, Product, Vendor, Order, OrderItem, Profile, ProductReview, ProductImage, Article
from .forms import ProductForm, SignUpForm # Added SignUpForm
from django.contrib import messages
from django.db.models import Q, Avg

def home(request):
    categories = Category.objects.all()[:6]
    featured_products = Product.objects.filter(is_available=True)[:8]
    new_arrivals = Product.objects.filter(is_available=True).order_by('-created_at')[:8]
    
    selected_kebele = request.GET.get('kebele')
    local_vendors = Vendor.objects.filter(is_verified=True)
    if selected_kebele:
        local_vendors = local_vendors.filter(kebele=selected_kebele)
    local_vendors = local_vendors[:4]
    
    latest_articles = Article.objects.filter(is_published=True).order_by('-created_at')[:3]
    kebeles = [k[0] for k in Vendor.JIMMA_KEBELES]
    
    return render(request, 'core/index.html', {
        'categories': categories,
        'featured_products': featured_products,
        'new_arrivals': new_arrivals,
        'local_vendors': local_vendors,
        'latest_articles': latest_articles,
        'kebeles': kebeles,
        'selected_kebele': selected_kebele,
    })

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful. Welcome to Jimma Market!")
            return redirect('index')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})

def product_list(request):
    query = request.GET.get('q')
    category_slug = request.GET.get('category')
    sort = request.GET.get('sort')
    kebele = request.GET.get('kebele')
    
    products = Product.objects.filter(is_available=True)
    
    if query:
        products = products.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query)
        )
    
    if category_slug:
        products = products.filter(category__slug=category_slug)
    
    if kebele:
        products = products.filter(vendor__kebele=kebele)
        
    if sort == 'price_low':
        products = products.order_by('price')
    elif sort == 'price_high':
        products = products.order_by('-price')
    elif sort == 'newest':
        products = products.order_by('-created_at')
        
    categories = Category.objects.all()
    kebeles = [k[0] for k in Vendor.JIMMA_KEBELES]
    
    return render(request, 'core/product_list.html', {
        'products': products,
        'categories': categories,
        'kebeles': kebeles,
        'current_category': category_slug,
        'current_sort': sort,
        'current_kebele': kebele,
    })

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_available=True)
    related_products = Product.objects.filter(category=product.category).exclude(id=product.id)[:4]
    reviews = product.reviews.all().order_by('-created_at')
    
    return render(request, 'core/product_detail.html', {
        'product': product,
        'related_products': related_products,
        'reviews': reviews,
    })

def product_review_submit(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        full_name = request.POST.get('full_name', 'Anonymous')
        
        if request.user.is_authenticated:
            full_name = f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username
        
        ProductReview.objects.create(
            product=product,
            user=request.user if request.user.is_authenticated else None,
            full_name=full_name,
            rating=rating,
            comment=comment
        )
        messages.success(request, "Thank you for your review!")
        return redirect('product_detail', slug=product.slug)

def category_products(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = category.products.filter(is_available=True)
    
    kebele = request.GET.get('kebele')
    if kebele:
        products = products.filter(vendor__kebele=kebele)
    
    kebeles = [k[0] for k in Vendor.JIMMA_KEBELES]
    
    return render(request, 'core/category_products.html', {
        'category': category, 
        'products': products,
        'kebeles': kebeles,
        'current_kebele': kebele
    })

# Basic Cart System using Session
def get_cart(request):
    cart = request.session.get('cart', {})
    return cart

def cart_add(request, product_id):
    cart = get_cart(request)
    product_id_str = str(product_id)
    quantity = int(request.POST.get('quantity', 1))
    
    if product_id_str in cart:
        cart[product_id_str] += quantity
    else:
        cart[product_id_str] = quantity
        
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
        try:
            product = Product.objects.get(id=product_id)
            subtotal = product.price * quantity
            total += subtotal
            cart_items.append({'product': product, 'quantity': quantity, 'subtotal': subtotal})
        except Product.DoesNotExist:
            continue
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
        kebele = request.POST.get('kebele')
        delivery_time_slot = request.POST.get('delivery_time_slot')
        payment_method = request.POST.get('payment_method')
        
        total = 0
        order_items_data = []
        for product_id, quantity in cart.items():
            product = get_object_or_404(Product, id=product_id)
            total += product.price * quantity
            order_items_data.append((product, quantity, product.price))
        
        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            full_name=full_name,
            email=email,
            phone=phone,
            address=address,
            kebele=kebele,
            delivery_time_slot=delivery_time_slot,
            total_price=total,
            payment_method=payment_method
        )
        
        for product, quantity, price in order_items_data:
            OrderItem.objects.create(order=order, product=product, quantity=quantity, price=price)
        
        request.session['cart'] = {}
        messages.success(request, "Order placed successfully!")
        return redirect('order_success', order_id=order.id)
        
    kebeles = Order.JIMMA_KEBELES
    time_slots = Order.TIME_SLOTS
    
    total = 0
    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, id=product_id)
        total += product.price * quantity

    return render(request, 'core/checkout.html', {
        'kebeles': kebeles,
        'time_slots': time_slots,
        'total': total,
    })

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
        kebele = request.POST.get('kebele')
        phone = request.POST.get('phone')
        
        Vendor.objects.create(
            user=request.user,
            business_name=business_name,
            description=description,
            address=address,
            kebele=kebele,
            phone=phone
        )
        # Update user role
        profile, created = Profile.objects.get_or_create(user=request.user)
        profile.role = 'seller'
        profile.save()
        
        messages.success(request, "Vendor registration successful. Wait for admin verification.")
        return redirect('vendor_dashboard')
        
    return render(request, 'core/vendor_register.html', {'kebeles': Vendor.JIMMA_KEBELES})

@login_required
def vendor_dashboard(request):
    vendor = get_object_or_404(Vendor, user=request.user)
    products = vendor.products.all().order_by('-created_at')
    
    # Get all orders that contain products from this vendor
    # We use a set of order IDs to avoid duplicates if multiple products from same vendor in one order
    vendor_order_items = OrderItem.objects.filter(product__vendor=vendor).select_related('order', 'product').order_by('-order__created_at')
    
    return render(request, 'core/vendor_dashboard.html', {
        'vendor': vendor, 
        'products': products, 
        'order_items': vendor_order_items
    })

@login_required
def vendor_product_add(request):
    vendor = get_object_or_404(Vendor, user=request.user)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.vendor = vendor
            product.save()
            messages.success(request, "Product added successfully!")
            return redirect('vendor_dashboard')
    else:
        form = ProductForm()
    
    return render(request, 'core/vendor_product_form.html', {'form': form, 'title': 'Add New Product'})

@login_required
def vendor_product_edit(request, pk):
    vendor = get_object_or_404(Vendor, user=request.user)
    product = get_object_or_404(Product, pk=pk, vendor=vendor)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, "Product updated successfully!")
            return redirect('vendor_dashboard')
    else:
        form = ProductForm(instance=product)
    
    return render(request, 'core/vendor_product_form.html', {'form': form, 'title': f'Edit {product.name}'})

@login_required
def vendor_product_delete(request, pk):
    vendor = get_object_or_404(Vendor, user=request.user)
    product = get_object_or_404(Product, pk=pk, vendor=vendor)
    
    if request.method == 'POST':
        product.delete()
        messages.success(request, "Product deleted successfully!")
        return redirect('vendor_dashboard')
    
    return render(request, 'core/vendor_product_confirm_delete.html', {'product': product})

@login_required
def vendor_order_status_update(request, order_id):
    vendor = get_object_or_404(Vendor, user=request.user)
    order = get_object_or_404(Order, id=order_id)
    
    # Check if this vendor has products in this order
    if not OrderItem.objects.filter(order=order, product__vendor=vendor).exists():
        messages.error(request, "You don't have permission to update this order.")
        return redirect('vendor_dashboard')
        
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.save()
            messages.success(request, f"Order status updated to {new_status}")
    
    return redirect('vendor_dashboard')

# Essential Pages
def about_us(request):
    return render(request, 'core/about_us.html')

def how_it_works(request):
    return render(request, 'core/how_it_works.html')

def seller_info(request):
    return render(request, 'core/seller_info.html')

def delivery_info(request):
    return render(request, 'core/delivery_info.html')

def contact_us(request):
    if request.method == 'POST':
        messages.success(request, "Thank you for your message. We will get back to you soon!")
        return redirect('contact_us')
    return render(request, 'core/contact_us.html')

def track_order(request):
    order = None
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        phone = request.POST.get('phone')
        try:
            order = Order.objects.get(id=order_id, phone=phone)
        except (Order.DoesNotExist, ValueError):
            messages.error(request, "Order not found. Please check your order ID and phone number.")
            
    return render(request, 'core/track_order.html', {'order': order})

# Blog/Article Views
def article_list(request):
    articles = Article.objects.filter(is_published=True).order_by('-created_at')
    return render(request, 'core/article_list.html', {'articles': articles})

def article_detail(request, slug):
    article = get_object_or_404(Article, slug=slug, is_published=True)
    return render(request, 'core/article_detail.html', {'article': article})

def project_log(request):
    """
    View to display project version history and updates.
    """
    logs = [
        {
            "version": "1.1.0",
            "date": "February 6, 2026",
            "description": "Enhanced user experience and neighborhood filtering.",
            "changes": [
                "Implemented Neighborhood (Kebele) filtering for products and categories.",
                "Added user registration (signup) functionality.",
                "Enhanced hero search bar with product and Kebele search combined.",
                "Updated site-wide contact information and social links.",
                "Integrated internationalization (i18n) support for key pages.",
            ]
        },
        {
            "version": "1.0.0",
            "date": "February 1, 2026",
            "description": "Initial launch of Jimma Market platform.",
            "changes": [
                "Core marketplace functionality with multi-vendor support.",
                "Product listing, detail views, and category organization.",
                "Shopping cart and checkout system with order tracking.",
                "Vendor dashboard for product and order management.",
                "Basic news and blog section integration.",
            ]
        }
    ]
    return render(request, 'core/project_log.html', {'logs': logs, 'current_version': '1.1.0'})