
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from core.permissions import IsCustomer, ReadOnly
from orders.models import Order, DELIVERED
from products.models import Product
from reviews.models import ProductReview, CustomerReviewsLikes
from reviews.serializers import ProductReviewSerializer
from users.models import CUSTOMER, SELLER


class ProductReviewsViewSet(viewsets.ModelViewSet):
    queryset = ProductReview.objects.all()
    serializer_class = ProductReviewSerializer
    permission_classes = [ReadOnly | IsCustomer]

    def perform_create(self, serializer):
        customer = self.request.user
        product = serializer.validated_data['product']
        is_verified = Order.objects.filter(customer=customer, product=product, status=DELIVERED).exists()
        serializer.save(customer=self.request.user,seller=serializer.validated_data['product'].seller,is_verified=is_verified)

    def get_queryset(self):
        product_pk = self.request.data.get('product')

        try:
            product_pk = int(product_pk)
        except (TypeError, ValueError):
            product_pk = None

        if product_pk:
            product = Product.objects.filter(id=product_pk).first()
            if product:
                return self.queryset.filter(product=product_pk).select_related('customer')

        if self.request.user.user_type == CUSTOMER:
            return self.queryset.filter(customer=self.request.user).select_related('product')
        if self.request.user.user_type == SELLER:
            return self.queryset.filter(seller=self.request.user).select_related('product', 'customer')
        if self.request.user.is_staff:
            return self.queryset.select_related('product', 'customer', 'seller')

        return self.queryset.select_related('customer')

    @action(detail=True, methods=['post'], permission_classes=[IsCustomer])
    def like(self, request, pk=None):
        review = self.get_object()
        customer = request.user

        if CustomerReviewsLikes.objects.filter(review=review, customer=customer).exists():
            return Response({"detail": "You have already liked this review."}, status=status.HTTP_400_BAD_REQUEST)

        CustomerReviewsLikes.objects.create(review=review, customer=customer)
        ProductReview.objects.filter(id=review.id).update(likes_count=review.likes_count + 1)
        return Response({"detail": "Review liked successfully."}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], permission_classes=[IsCustomer])
    def unlike(self, request, pk=None):
        review = self.get_object()
        customer = request.user

        like = CustomerReviewsLikes.objects.filter(review=review, customer=customer).first()
        if not like:
            return Response({"detail": "You have not liked this review."}, status=status.HTTP_400_BAD_REQUEST)

        like.delete()
        ProductReview.objects.filter(id=review.id).update(likes_count=review.likes_count - 1)
        return Response({"detail": "Review unliked successfully."}, status=status.HTTP_200_OK)