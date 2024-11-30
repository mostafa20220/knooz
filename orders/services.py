from decimal import Decimal

from django.core.files.base import ContentFile
from django.db import transaction

from carts.services import calc_cod_fee, get_cart_summary
from core.constants import ADDED_VALUE_TAX_RATE
from coupons.serializers import calc_discount_amount
from orders.models import Order, OrderItem
from products.models import ProductVariant


def copy_img(img_instance):
    if not img_instance:
        raise ValueError("Image instance is required to copy the image")

    # Open and read the image content
    img_instance.open()
    image_content = img_instance.read()

    # create a new image instance with the same content
    new_img = ContentFile(image_content, name=img_instance.name)
    return new_img

def calc_order_total(items_value, shipping_fee, cod_fee, discount_amount):
    return sum([items_value, shipping_fee, cod_fee]) - discount_amount

def calc_estimated_tax(order_total):
    return ADDED_VALUE_TAX_RATE * order_total


def decrease_coupon_usage_count(coupon):
    coupon.usage_count -= 1
    coupon.save()

def update_ordered_products_stock(cart_items):
    updated_products = []
    for cart_item in cart_items:
        cart_item.product_variant.stock -= cart_item.quantity
        updated_products.append(cart_item.product_variant)
    ProductVariant.objects.bulk_update(updated_products, ['stock', 'updated_at'], 500)

def empty_customer_cart(customer):
    customer.cart.all().delete()

@transaction.atomic()
def place_new_order(customer,coupon,shipping_address,payment_method):
    cart_items = customer.cart.all()
    items_value, shipping_fee = get_cart_summary(cart_items)
    discount_amount = calc_discount_amount(coupon, items_value) if coupon else Decimal('0.00')

    cod_fee = calc_cod_fee(payment_method)
    order_total = calc_order_total(items_value, shipping_fee, cod_fee, discount_amount)
    estimated_tax = calc_estimated_tax(order_total)

    if coupon:
        decrease_coupon_usage_count(coupon)

    # create the order
    order = Order.objects.create(
        customer=customer,
        shipping_address=shipping_address,
        payment_method=payment_method,
        coupon_code=coupon.code if coupon else None,
        items_value=items_value,
        shipping_fee=shipping_fee,
        cod_fee=cod_fee,
        discount_amount=discount_amount,
        order_total=order_total,
        estimated_tax=estimated_tax
    )

    # create the order items
    order_items = [OrderItem(
        order=order,
        name=item.product_variant.product.name,
        description=item.product_variant.product.description,
        seller=item.product_variant.product.seller,
        category=item.product_variant.product.category.name,
        brand=item.product_variant.product.brand.name,
        size=item.product_variant.size.size,
        color=item.product_variant.color.color,
        free_shipping=item.product_variant.product.free_shipping,
        free_return=item.product_variant.product.free_return,
        is_returnable=item.product_variant.product.is_returnable,
        best_selling=item.product_variant.product.best_selling,
        best_rated=item.product_variant.product.best_rated,
        quantity=item.quantity,
        item_price=item.product_variant.price * item.quantity,
        product_uuid=item.product_variant.product.product_uuid,
        image=copy_img(item.product_variant.images.first().image) if item.product_variant.images.first() else None
    ) for item in cart_items]

    print("order_items:", order_items)
    OrderItem.objects.bulk_create(order_items, batch_size=500)

    update_ordered_products_stock(cart_items)

    empty_customer_cart(customer)

    return order



