from django.contrib import admin
from .models import Product, ProductVariant, Category, Brand, VariantImage, VariantSize, VariantColor
# Register your models here.
admin.site.register([Product, ProductVariant, Category, Brand, VariantImage, VariantSize, VariantColor])
