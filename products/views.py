from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.db.models import Q
from products.models import Product, ProductVariant, VariantImage, Brand, Category
from products.serializers import ProductSerializer, ProductVariantSerializer, VariantImageSerializer
from products.permissions import IsSellerOrReadOnly


class VariantImageViewSet(viewsets.ModelViewSet):
    queryset = VariantImage.objects.all()
    serializer_class = VariantImageSerializer
    permission_classes = [IsSellerOrReadOnly]

class ProductVariantViewSet(viewsets.ModelViewSet):
    queryset = ProductVariant.objects.prefetch_related('variantimage_set')
    serializer_class = ProductVariantSerializer
    permission_classes = [IsSellerOrReadOnly]


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsSellerOrReadOnly]
    pagination_class = PageNumberPagination

    def get_queryset(self):
        queryset = Product.objects.prefetch_related('productvariant_set')
        category = self.request.query_params.get('category')
        brand = self.request.query_params.get('brand')

        filters = Q()
        if category:
            category = Category.objects.filter(name=category).first()
            filters &= Q(category=category)
        if brand:
            brand = Brand.objects.filter(name=brand).first()
            filters &= Q(brand=brand)

        queryset = queryset.filter(filters).filter(productvariant__stock__gt=0).distinct()
        return queryset
