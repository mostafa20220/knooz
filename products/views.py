from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from products.serializers import ListProductSerializer, CreateProductSerializer, DetailProductSerializer
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
