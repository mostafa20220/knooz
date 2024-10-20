from rest_framework import viewsets, status
from rest_framework.response import Response

from core.permissions import IsCustomer
from wishlists.models import WishlistItem
from wishlists.serializers import WishlistItemSerializer


# Create your views here.
class WishlistViewSet(viewsets.ModelViewSet):
    queryset = WishlistItem.objects.all()
    serializer_class = WishlistItemSerializer
    permission_classes = [IsCustomer]

    def update(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def partial_update(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def get_queryset(self):
        return (WishlistItem.objects.filter(customer=self.request.user)
                .select_related('product_variant')
                .prefetch_related('product_variant__product'))

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user)