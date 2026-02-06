from modeltranslation.translator import register, TranslationOptions
from .models import Category, Product, Vendor, Article

@register(Category)
class CategoryTranslationOptions(TranslationOptions):
    fields = ('name', 'description')

@register(Product)
class ProductTranslationOptions(TranslationOptions):
    fields = ('name', 'description')

@register(Vendor)
class VendorTranslationOptions(TranslationOptions):
    fields = ('business_name', 'description')

@register(Article)
class ArticleTranslationOptions(TranslationOptions):
    fields = ('title', 'content')