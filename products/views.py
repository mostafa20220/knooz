from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, DestroyAPIView
from rest_framework.response import Response

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
        queryset = Product.objects.select_related('category', 'brand', 'seller').prefetch_related(
            'variants__images',
            'variants__size',
            'variants__color'
        )
        return queryset

    # # delete variant or variant image if its pk is passed in the url
    # def destroy(self, request, *args, **kwargs):
    #     variant_pk = kwargs.get('variant_pk')
    #     variant_image_pk = kwargs.get('variant_image_pk')
    #
    #     if variant_pk:
    #         variant = ProductVariant.objects.filter(pk=variant_pk).first()
    #         if variant:
    #             variant.delete()
    #             return Response(status=status.HTTP_204_NO_CONTENT)
    #
    #     if variant_image_pk:
    #         variant_image = VariantImage.objects.filter(pk=variant_image_pk).first()
    #         if variant_image:
    #             variant_image.delete()
    #             return Response(status=status.HTTP_204_NO_CONTENT)
    #
    #     return Response(status=status.HTTP_404_NOT_FOUND)
    #
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

class ImageDetailView(DestroyAPIView):
    queryset = VariantImage.objects.all()
    serializer_class = VariantImageSerializer
    permission_classes = [IsSellerOrReadOnly]
