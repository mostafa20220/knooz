from django_filters.rest_framework import DjangoFilterBackend
from oauthlib.uri_validate import query
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, ListAPIView

from products.models import VariantSize, VariantColor, Category, Brand
from products.serializers import ListProductSerializer, CreateProductSerializer, DetailProductSerializer, \
    VariantSizeSerializer, VariantColorSerializer, CategorySerializer, BrandSerializer
from core.permissions import ReadOnly, IsSeller
from products.filters import ProductFilter
from products.services import get_product_queryset, get_seller_products_queryset


class ProductListView(ListCreateAPIView):
    permission_classes = [ReadOnly | IsSeller]
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductFilter

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ListProductSerializer
        return CreateProductSerializer

    def get_queryset(self):
        self.queryset = get_product_queryset()
        return self.queryset

    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)


class ProductDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = DetailProductSerializer
    permission_classes = [ReadOnly | IsSeller]

    def get_queryset(self):
        if self.request.method == 'GET':
            return get_product_queryset()

        seller = self.request.user
        queryset = get_seller_products_queryset(seller)
        return queryset

class SizeListView(ListAPIView):
    queryset = VariantSize.objects.all()
    serializer_class = VariantSizeSerializer
    permission_classes = [ReadOnly]

class ColorListView(ListAPIView):
    queryset = VariantColor.objects.all()
    serializer_class = VariantColorSerializer
    permission_classes = [ReadOnly]

class CategoryListView(ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [ReadOnly]

class BrandListView(ListAPIView):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    permission_classes = [ReadOnly]

    def get_queryset(self):
        queryset = Brand.objects.all()
        print("queryset: ",queryset)
        return queryset


