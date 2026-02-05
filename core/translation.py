from modeltranslation.translator import register, TranslationOptions
from .models import Category, Product, Vendor

@register(Category)
class CategoryTranslationOptions(TranslationOptions):
    fields = ('name', 'description')

@register(Product)
class ProductTranslationOptions(TranslationOptions):
    fields = ('name', 'description')

@register(Vendor)
class VendorTranslationOptions(TranslationOptions):
    fields = ('business_name', 'description')
