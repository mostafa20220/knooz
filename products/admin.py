from django.contrib import admin

from reviews.models import ProductReview
from .models import Product, ProductVariant, Category, Brand, VariantImage, VariantSize, VariantColor
# Register your models here.
class ProductReviewInline(admin.StackedInline):
    model = ProductReview
    extra = 0

class ProductVariantInline(admin.StackedInline):
    model = ProductVariant
    extra = 0

class VariantImageInline(admin.StackedInline):
    model = VariantImage
    extra = 0

class ProductVariantAdmin(admin.ModelAdmin):
    inlines = [
        VariantImageInline,
    ]

class ProductAdmin(admin.ModelAdmin):
    inlines = [
        ProductVariantInline,
        ProductReviewInline,
    ]

admin.site.register(Product, ProductAdmin)
admin.site.register(ProductVariant, ProductVariantAdmin)
admin.site.register([Category, Brand, VariantSize, VariantColor])
