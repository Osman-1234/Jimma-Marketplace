import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import Product, ProductReview
from django.contrib.auth.models import User

def add_reviews():
    products = Product.objects.all()
    if not products.exists():
        print("No products found.")
        return

    reviews_data = [
        {"product_idx": 0, "name": "Chala Jimma", "rating": 5, "comment": "Excellent quality! Highly recommended for anyone in Jimma."},
        {"product_idx": 0, "name": "Aster K.", "rating": 4, "comment": "Very good service and the product is as described."},
        {"product_idx": 1 if products.count() > 1 else 0, "name": "Dawit H.", "rating": 5, "comment": "Fast delivery to Kochi and great price."},
        {"product_idx": 2 if products.count() > 2 else 0, "name": "Mulu B.", "rating": 3, "comment": "Decent product, but took a bit longer to arrive."},
    ]

    for data in reviews_data:
        p = products[data["product_idx"]]
        ProductReview.objects.create(
            product=p,
            full_name=data["name"],
            rating=data["rating"],
            comment=data["comment"]
        )
    
    print(f"Created {len(reviews_data)} sample reviews.")

if __name__ == "__main__":
    add_reviews()
