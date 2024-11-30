from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from carts.models import Cart
from carts.services import get_customer_cart_queryset, get_cart_summary
from core.permissions import IsCustomer
from carts.serializers import CartSerializer


class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartSerializer
    permission_classes = [IsCustomer]
    queryset = Cart.objects.all()

    def get_queryset(self):
        return get_customer_cart_queryset(self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        items_value, shipping_fee = get_cart_summary(queryset)


        response = {
            'cart': serializer.data,
            'items_value': items_value,
            'shipping_fee': shipping_fee,
            'total': items_value + shipping_fee
        }

        return Response(response)

    @action(detail=False, methods=['delete'], url_path='all')
    def empty_cart(self, request):
        Cart.objects.filter(customer=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
