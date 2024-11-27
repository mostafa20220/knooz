from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, DestroyAPIView

from products.filters import ProductFilter
from products.models import Product, ProductVariant, VariantImage
from products.serializers import VariantImageSerializer, ListProductSerializer, \
    CreateProductSerializer, ProductDetailSerializer, DetailProductVariantSerializer
from products.permissions import IsSellerOrReadOnly

class ProductListView(ListCreateAPIView):
    queryset = Product.objects.all()
    permission_classes = [IsSellerOrReadOnly]
    serializer_class = ListProductSerializer
    filter_backends = [DjangoFilterBackend]  # Use DjangoFilterBackend to enable filtering
    filterset_class = ProductFilter  # Specify the filterset

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ListProductSerializer
        return CreateProductSerializer

    def get_queryset(self):
        self.queryset = (Product.objects
                    .select_related(
                        'category',
                        'brand',
                        'seller'
                    )
                    .prefetch_related(
                        'variants__images',
                        'variants__size',
                        'variants__color'
                    )
                    .order_by('-created_at'))
        return self.queryset

    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)


class ProductDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductDetailSerializer
    permission_classes = [IsSellerOrReadOnly]

    def get_queryset(self):
        queryset = Product.objects.select_related('category', 'brand', 'seller').prefetch_related(
            'variants__images',
            'variants__size',
            'variants__color'
        )
        return queryset

class VariantDetailView(DestroyAPIView):
    queryset = ProductVariant.objects.all()
    serializer_class = DetailProductVariantSerializer
    permission_classes = [IsSellerOrReadOnly]

    def get_queryset(self):
        self.queryset = ProductVariant.objects.filter("product__seller" == self.request.user)
        return self.queryset

class ImageDetailView(DestroyAPIView):
    queryset = VariantImage.objects.all()
    serializer_class = VariantImageSerializer
    permission_classes = [IsSellerOrReadOnly]
