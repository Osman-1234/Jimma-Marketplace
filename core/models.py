from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Avg

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class Vendor(models.Model):
    JIMMA_KEBELES = (
        ('Bosa Addis', 'Bosa Addis'),
        ('Bosa Kitto', 'Bosa Kitto'),
        ('Ginjo', 'Ginjo'),
        ('Ginjo Guduru', 'Ginjo Guduru'),
        ('Hermata', 'Hermata'),
        ('Hermata Merkato', 'Hermata Merkato'),
        ('Jiren', 'Jiren'),
        ('Kofe', 'Kofe'),
        ('Mendera Kochi', 'Mendera Kochi'),
        ('Seto Semero', 'Seto Semero'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    business_name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    address = models.CharField(max_length=255)
    kebele = models.CharField(max_length=100, choices=JIMMA_KEBELES, blank=True)
    phone = models.CharField(max_length=20)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.business_name

class Product(models.Model):
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    vendor = models.ForeignKey(Vendor, related_name='products', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    image = models.ImageField(upload_to='products/', blank=True, null=True) # Main image
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def average_rating(self):
        avg = self.reviews.aggregate(Avg('rating'))['rating__avg']
        return round(avg, 1) if avg else 0

    @property
    def review_count(self):
        return self.reviews.count()

class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/gallery/')
    alt_text = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"Image for {self.product.name}"

class ProductReview(models.Model):
    product = models.ForeignKey(Product, related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True) # Optional user
    full_name = models.CharField(max_length=255) # For guests
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review for {self.product.name} by {self.full_name}"

class Profile(models.Model):
    ROLE_CHOICES = (
        ('customer', 'Customer'),
        ('seller', 'Seller'),
        ('admin', 'Admin'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user.username} Profile"

class Order(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Processing', 'Processing'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    )
    
    JIMMA_KEBELES = (
        ('Bosa Addis', 'Bosa Addis'),
        ('Bosa Kitto', 'Bosa Kitto'),
        ('Ginjo', 'Ginjo'),
        ('Ginjo Guduru', 'Ginjo Guduru'),
        ('Hermata', 'Hermata'),
        ('Hermata Merkato', 'Hermata Merkato'),
        ('Jiren', 'Jiren'),
        ('Kofe', 'Kofe'),
        ('Mendera Kochi', 'Mendera Kochi'),
        ('Seto Semero', 'Seto Semero'),
        # Add more as needed
    )

    TIME_SLOTS = (
        ('Morning', 'Morning (8:00 AM - 12:00 PM)'),
        ('Afternoon', 'Afternoon (12:00 PM - 5:00 PM)'),
        ('Evening', 'Evening (5:00 PM - 8:00 PM)'),
    )

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    full_name = models.CharField(max_length=255)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    kebele = models.CharField(max_length=100, choices=JIMMA_KEBELES, blank=True)
    delivery_time_slot = models.CharField(max_length=50, choices=TIME_SLOTS, default='Morning')
    
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Order {self.id} - {self.full_name}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    @property
    def total_price(self):
        return self.price * self.quantity

class Article(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    content = models.TextField()
    image = models.ImageField(upload_to='articles/', blank=True, null=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='articles')
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
