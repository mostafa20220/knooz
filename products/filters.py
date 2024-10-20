# filters.py
import django_filters
from .models import Product, ProductVariant


class ProductFilter(django_filters.FilterSet):
    class Meta:
        model = Product
        fields = {
            'name': ['icontains'],    # Case-insensitive search for name
            'category': ['exact'],    # Exact match on category
            'brand': ['exact'],   # Exact match on brand
            'free_shipping': ['exact'], # Exact match on free_shipping
            'free_return': ['exact'],   # Exact match on free_return
            'best_selling': ['exact'],  # Exact match on best_selling
            'best_rated': ['exact'],    # Exact match on best_rated
            'seller': ['exact'],    # Exact match on seller
        }

class ProductVariantFilter(django_filters.FilterSet):
    class Meta:
        model = ProductVariant
        fields = {
            'price': ['lt', 'gt'],    # Filter for less than or greater than price
            'color': ['exact'],   # Exact match on color
            'size': ['exact'],    # Exact match on size
        }