import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import Category, Product, Vendor, Profile
from django.contrib.auth.models import User
from django.utils.text import slugify

def populate():
    # Create Superuser if not exists
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@example.com', 'adminpass')
        print("Superuser created: admin / adminpass")

    # Categories
    categories_data = [
        {'name': 'Electronics', 'name_om': 'Meeshaalee Elektirooniksii', 'name_am': 'የኤሌክትሮኒክስ ዕቃዎች'},
        {'name': 'Clothing', 'name_om': 'Uffata', 'name_am': 'ልብስ'},
        {'name': 'Home & Garden', 'name_om': 'Mana fi Muka', 'name_am': 'ቤት እና የአትክልት ቦታ'},
        {'name': 'Food & Groceries', 'name_om': 'Nyaataa fi Meeshaalee Nyaataa', 'name_am': 'ምግብ እና ግሮሰሪ'},
        {'name': 'Handmade Crafts', 'name_om': 'Hojii Harkaa', 'name_am': 'በእጅ የተሰሩ ስራዎች'},
        {'name': 'Books', 'name_om': 'Kitaabota', 'name_am': 'መጽሐፍት'},
    ]

    categories = []
    for cat in categories_data:
        category, created = Category.objects.get_or_create(
            name=cat['name'],
            defaults={
                'name_om': cat['name_om'],
                'name_am': cat['name_am'],
                'slug': slugify(cat['name'])
            }
        )
        categories.append(category)
        if created:
            print(f"Category created: {cat['name']}")

    # Create a Vendor
    vendor_user, created = User.objects.get_or_create(username='vendor1', email='vendor1@example.com')
    if created:
        vendor_user.set_password('vendorpass')
        vendor_user.save()
        Profile.objects.get_or_create(user=vendor_user, role='seller')
        print("Vendor user created: vendor1")

    vendor, created = Vendor.objects.get_or_create(
        user=vendor_user,
        defaults={
            'business_name': 'Ethio Tech Solutions',
            'business_name_om': 'Furmaata Teeknoojii Itiyoophiyaa',
            'description': 'Leading provider of tech gadgets in Addis.',
            'address': 'Bole, Addis Ababa',
            'phone': '+251911000000'
        }
    )
    if created:
        print("Vendor created: Ethio Tech Solutions")

    # Products
    products_data = [
        {
            'name': 'Smartphone X1', 
            'name_om': 'Bilbila Ammayya X1',
            'category': categories[0], 
            'price': 25000, 
            'description': 'High performance smartphone.'
        },
        {
            'name': 'Traditional Coffee Pot (Jebena)', 
            'name_om': 'Jabanaa',
            'category': categories[4], 
            'price': 500, 
            'description': 'Handmade traditional clay pot.'
        },
        {
            'name': 'Cotton Scarf', 
            'name_om': 'Shaashii',
            'category': categories[1], 
            'price': 1200, 
            'description': 'Pure Ethiopian cotton.'
        },
        {
            'name': 'Organic Honey', 
            'name_om': 'Damma',
            'category': categories[3], 
            'price': 800, 
            'description': 'Pure honey from Gojam.'
        },
    ]

    for prod in products_data:
        product, created = Product.objects.get_or_create(
            name=prod['name'],
            defaults={
                'name_om': prod['name_om'],
                'category': prod['category'],
                'vendor': vendor,
                'price': prod['price'],
                'description': prod['description'],
                'slug': slugify(prod['name']),
                'is_available': True
            }
        )
        if created:
            print(f"Product created: {prod['name']}")

if __name__ == '__main__':
    populate()
