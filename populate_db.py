import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import Category, Product, Vendor, Profile, Article
from django.contrib.auth.models import User
from django.utils.text import slugify

def populate():
    # Create Superuser if not exists
    admin_user, created = User.objects.get_or_create(username='admin', defaults={'email': 'admin@example.com'})
    if created:
        admin_user.set_password('adminpass')
        admin_user.save()
        print("Superuser created: admin / adminpass")
    else:
        admin_user = User.objects.get(username='admin')

    # Categories
    categories_data = [
        {'name': 'Electronics', 'name_om': 'Meeshaalee Elektirooniksii', 'name_am': 'የኤሌክትሮኒክስ ዕቃዎች'},
        {'name': 'Fashion', 'name_om': 'Faashinii', 'name_am': 'ፋሽን'},
        {'name': 'Groceries', 'name_om': 'Meeshaalee Nyaataa', 'name_am': 'ግሮሰሪ'},
        {'name': 'Home & Living', 'name_om': 'Meeshaa Manaa', 'name_am': 'ቤት እና ኑሮ'},
        {'name': 'Agriculture', 'name_om': 'Qonnaa', 'name_am': 'ግብርና'},
    ]

    categories = []
    for cat in categories_data:
        category, created = Category.objects.get_or_create(
            name=cat['name'],
            defaults={
                'name_om': cat.get('name_om', cat['name']),
                'name_am': cat.get('name_am', cat['name']),
                'slug': slugify(cat['name'])
            }
        )
        categories.append(category)
        if created:
            print(f"Category created: {cat['name']}")

    # Create Jimma Vendors
    vendors_data = [
        {
            'username': 'jimma_electronics',
            'business_name': 'Jimma Tech Hub',
            'business_name_om': 'Giddu-gala Teeknoojii Jimmaa',
            'address': 'Hermata Merkato, Jimma',
            'kebele': 'Hermata Merkato',
            'phone': '0911223344'
        },
        {
            'username': 'aba_jifar_honey',
            'business_name': 'Abba Jifar Honey',
            'business_name_om': 'Damma Abbaa Jifaar',
            'address': 'Jiren, Jimma',
            'kebele': 'Jiren',
            'phone': '0922334455'
        },
        {
            'username': 'kochi_furniture',
            'business_name': 'Kochi Modern Furniture',
            'business_name_om': 'Meeshaa Manaa Kochi',
            'address': 'Mendera Kochi, Jimma',
            'kebele': 'Mendera Kochi',
            'phone': '0933445566'
        }
    ]

    for v_data in vendors_data:
        user, created = User.objects.get_or_create(username=v_data['username'], email=f"{v_data['username']}@example.com")
        if created:
            user.set_password('vendorpass')
            user.save()
            Profile.objects.get_or_create(user=user, role='seller')
        
        vendor, created = Vendor.objects.get_or_create(
            user=user,
            defaults={
                'business_name': v_data['business_name'],
                'business_name_om': v_data['business_name_om'],
                'address': v_data['address'],
                'kebele': v_data['kebele'],
                'phone': v_data['phone'],
                'is_verified': True
            }
        )
        if not created:
            vendor.kebele = v_data['kebele']
            vendor.save()
            print(f"Updated Vendor kebele: {v_data['business_name']} -> {v_data['kebele']}")
        else:
            print(f"Vendor created: {v_data['business_name']}")

    # Products
    products_data = [
        {
            'name': 'Samsung Galaxy A54', 
            'name_om': 'Saamsangi Gaalaaksii A54',
            'category': categories[0], 
            'price': 45000, 
            'description': 'Latest Samsung smartphone with great camera.',
            'vendor_username': 'jimma_electronics'
        },
        {
            'name': 'Pure Jimma Forest Honey', 
            'name_om': 'Damma Bosona Jimmaa qulqulluu',
            'category': categories[2], 
            'price': 1200, 
            'description': '100% organic honey from the forests of Jimma.',
            'vendor_username': 'aba_jifar_honey'
        },
        {
            'name': 'Jimma Coffee Beans (1kg)', 
            'name_om': 'Bunna Jimmaa (kg 1)',
            'category': categories[2], 
            'price': 900, 
            'description': 'World famous Jimma coffee beans, roasted to perfection.',
            'vendor_username': 'aba_jifar_honey'
        },
        {
            'name': 'Modern Sofa Set', 
            'name_om': 'Sofaa Ammayya',
            'category': categories[3], 
            'price': 85000, 
            'description': 'High quality sofa set for your living room.',
            'vendor_username': 'kochi_furniture'
        },
    ]

    for prod in products_data:
        vendor = Vendor.objects.get(user__username=prod['vendor_username'])
        product, created = Product.objects.get_or_create(
            name=prod['name'],
            defaults={
                'name_om': prod.get('name_om', prod['name']),
                'category': prod['category'],
                'vendor': vendor,
                'price': prod['price'],
                'description': prod['description'],
                'slug': slugify(prod['name']),
                'is_available': True,
                'stock': 10
            }
        )
        if created:
            print(f"Product created: {prod['name']}")

    # Articles
    articles_data = [
        {
            'title': 'The Rise of E-commerce in Jimma',
            'content': 'Jimma is witnessing a digital transformation in how people shop. With the launch of Jimma Market, local residents can now access a wide range of products from their favorite local vendors with just a few clicks. This shift is not only providing convenience but also opening new opportunities for small businesses in the region.',
            'author': admin_user
        },
        {
            'title': 'Vendor Spotlight: Abba Jifar Honey',
            'content': 'Meet the people behind the finest honey in Jimma. Abba Jifar Honey has been a staple in the local market for years, and now they are bringing their 100% organic forest honey to the digital space. Discover their journey from traditional beekeeping to becoming a top-selling vendor on Jimma Market.',
            'author': admin_user
        },
        {
            'title': 'Jimma Coffee: From Farm to Your Cup',
            'content': 'Jimma is world-renowned for its exceptional coffee. In this article, we explore the rich heritage of coffee farming in the region and how Jimma Market is helping local farmers reach a broader audience. Learn about the unique flavors of Jimma coffee and why it remains a favorite among coffee enthusiasts worldwide.',
            'author': admin_user
        }
    ]

    for art_data in articles_data:
        article, created = Article.objects.get_or_create(
            title=art_data['title'],
            defaults={
                'content': art_data['content'],
                'author': art_data['author'],
                'is_published': True,
                'slug': slugify(art_data['title'])
            }
        )
        if created:
            print(f"Article created: {art_data['title']}")

if __name__ == '__main__':
    populate()