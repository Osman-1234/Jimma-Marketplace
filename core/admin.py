from django.contrib import admin
from modeltranslation.admin import TranslationAdmin
from .models import Profile, Category, Vendor, Product, Order, OrderItem, Article

@admin.register(Category)
class CategoryAdmin(TranslationAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Vendor)
class VendorAdmin(TranslationAdmin):
    list_display = ('business_name', 'user', 'is_verified')
    list_filter = ('is_verified',)
    search_fields = ('business_name', 'user__username')

@admin.register(Product)
class ProductAdmin(TranslationAdmin):
    list_display = ('name', 'vendor', 'category', 'price', 'stock', 'is_available')
    list_filter = ('is_available', 'category', 'vendor')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'total_price', 'status', 'payment_method', 'created_at')
    list_filter = ('status', 'payment_method', 'created_at')
    inlines = [OrderItemInline]

@admin.register(Article)
class ArticleAdmin(TranslationAdmin):
    list_display = ('title', 'author', 'is_published', 'created_at')
    list_filter = ('is_published', 'created_at', 'author')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}

admin.site.register(Profile)
