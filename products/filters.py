# filters.py
import django_filters

from .models import Product


class ProductFilter(django_filters.FilterSet):
    price_min = django_filters.NumberFilter(field_name='variants__price', lookup_expr='gte')
    price_max = django_filters.NumberFilter(field_name='variants__price', lookup_expr='lte')
    color = django_filters.CharFilter(field_name='variants__color', lookup_expr='exact')
    size = django_filters.CharFilter(field_name='variants__size', lookup_expr='exact')
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')
    
    class Meta:
        model = Product
        fields = {
            'category': ['exact'],    # Exact match on category
            'brand': ['exact'],   # Exact match on brand
            'free_shipping': ['exact'], # Exact match on free_shipping
            'free_return': ['exact'],   # Exact match on free_return
            'best_selling': ['exact'],  # Exact match on best_selling
            'best_rated': ['exact'],    # Exact match on best_rated
            'seller': ['exact'],    # Exact match on seller
        }
