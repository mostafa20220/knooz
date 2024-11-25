from decimal import Decimal

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from carts.models import Cart
from core.permissions import IsCustomer
from carts.serializers import CartSerializer
from orders.models import CREDIT_CARD

# should be dynamic based on the shipping address and the weight of the items in the cart and the shipping method
# but for now we will use a fixed value
SHIPPING_FEE = 20
COD_FEE = 10
SHIPPING_FEE_THRESHOLD = 200

def calc_items_value(cart_items):
    return sum([item.product_variant.price * item.quantity for item in cart_items])

def calc_shipping_fee(items_value, cart_items):
    shipping_fee = Decimal('0.00')
    if items_value < Decimal(str(SHIPPING_FEE_THRESHOLD)):
        for item in cart_items:
            is_free_shipping = item.product_variant.product.free_shipping
            if not is_free_shipping:
                shipping_fee = Decimal(str(SHIPPING_FEE))
                break
    return shipping_fee

def calc_cod_fee(payment_method):
    return Decimal('0.00') if payment_method == CREDIT_CARD else COD_FEE


class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartSerializer
    permission_classes = [IsCustomer]
    queryset = Cart.objects.all()

    def get_queryset(self):
        return ((Cart.objects.filter(customer=self.request.user)
        .select_related('product_variant'))
        .prefetch_related(
            'product_variant__size',
            'product_variant__color',
            'product_variant__product',
            'product_variant__product__brand',
            'product_variant__product__category',
            'product_variant__product__seller',
            'product_variant__images'))


    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        shipping_fee = Decimal('0.00')
        items_value = sum([Decimal(str(item.get('product').get('price'))) * item.get('quantity') for item in serializer.data])

        print("serializer.data:", serializer.data)

        if items_value < SHIPPING_FEE_THRESHOLD:
            for item in serializer.data:
                is_free_shipping = item.get('product').get('free_shipping')
                if not is_free_shipping:
                    shipping_fee = Decimal(str(SHIPPING_FEE))
                    break

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
