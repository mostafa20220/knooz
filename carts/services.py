from decimal import Decimal
from carts.models import Cart
from core.constants import SHIPPING_FEE_THRESHOLD, SHIPPING_FEE, COD_FEE, ADDED_VALUE_TAX_RATE
from orders.models import CREDIT_CARD

def get_customer_cart_queryset(customer):
    return (Cart.objects.filter(customer=customer)
    .select_related('product_variant')
    .prefetch_related(
        'product_variant__size',
        'product_variant__color',
        'product_variant__product',
        'product_variant__product__brand',
        'product_variant__product__category',
        'product_variant__product__seller',
        'product_variant__images')
    )

def get_cart_items_value(cart_items):
    return cart_items.aggregate(
        items_value = Sum(F('product_variant__price') * F('quantity')),
    ).get('items_value', Decimal('0.00'))

from django.db.models import F, Sum, Case, When, Value, DecimalField, BooleanField, Count

def get_cart_summary(cart_items):
    # Annotate intermediate values
    cart_summary = cart_items.aggregate(
       items_value=Sum(F('product_variant__price') * F('quantity')),
        free_shipping_count=Sum(Case(
            When(product_variant__product__free_shipping=True, then=1),
            default=0,
            output_field=DecimalField()
        )),
    )

    items_value = cart_summary.get('items_value', Decimal('0.00'))

    # Derive the shipping fee based on conditions
    shipping_fee = (
        0 if cart_summary.pop('free_shipping_count') == cart_items.count()
        else 0 if items_value >= SHIPPING_FEE_THRESHOLD
        else SHIPPING_FEE
    )

    return items_value, shipping_fee



def calc_cod_fee(payment_method):
    return Decimal('0.00') if payment_method == CREDIT_CARD else COD_FEE
