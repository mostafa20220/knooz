import hashlib
import hmac
import json
import requests
from decimal import Decimal
from decouple import config
from django.conf import settings
from core.constants import CREDIT_CARD, CASH_ON_DELIVERY
from django.core.files.base import ContentFile
from django.db import transaction
from rest_framework.exceptions import ValidationError
from carts.services import calc_cod_fee, get_cart_summary
from core.constants import ADDED_VALUE_TAX_RATE
from coupons.serializers import calc_discount_amount
from orders.models import Order, OrderItem, PENDING, PLACED, CANCELLED, PAYMENT_FAILED
from products.models import ProductVariant
from utils.emails import send_email_async
from utils.loggers import log_error, log_info, log_warning
from utils.utils import get_nested_value


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


def increase_coupon_usage_count(coupon):
    coupon.usage_count += 1
    coupon.save()

def update_ordered_products_stock(cart_items):
    # Collect product_variant IDs and required quantities in one go
    cart_data = {item.product_variant.id: item.quantity for item in cart_items}

    # Fetch and lock all required product variants in one query
    variants = (
        ProductVariant.objects.select_for_update()
        .filter(id__in=cart_data.keys())
    )

    # Validate stock and prepare updates
    updates = []
    for variant in variants:
        requested_quantity = cart_data[variant.id]
        if variant.stock < requested_quantity:
            raise ValidationError({
                "non_field_errors": [
                    f"The requested quantity of {variant.product.name} is not available."
                ]
            })
        # Prepare update
        variant.stock -= requested_quantity
        updates.append(variant)

    # Bulk update the locked rows
    ProductVariant.objects.bulk_update(updates, ['stock', 'updated_at'], batch_size=500)

def empty_customer_cart(customer):
    customer.cart.all().delete()

@transaction.atomic()
def place_new_order(customer,shipping_address,payment_method,coupon=None):
    cart_items = customer.cart.all()
    items_value, shipping_fee = get_cart_summary(cart_items)
    discount_amount = calc_discount_amount(coupon, items_value) if coupon else Decimal('0.00')

    cod_fee = calc_cod_fee(payment_method)
    order_total = calc_order_total(items_value, shipping_fee, cod_fee, discount_amount)
    estimated_tax = calc_estimated_tax(order_total)

    if coupon:
        increase_coupon_usage_count(coupon)

    # TODO: set the order_status based on the payment method,
    #   if the payment method is cash on delivery then the order_status should be placed
    #   if the payment method is credit card then the order_status should be pending
    # TODO: ask gpt about:
    #  updating order_status if it's credit card payment to cancel the order if the payment is not completed within 15 minute

    # create the order
    order = Order.objects.create(
        customer=customer,
        shipping_address=shipping_address,
        shipping_address_snapshot=str(shipping_address),
        payment_method=payment_method,
        coupon_code=coupon.code if coupon else None,
        items_value=items_value,
        shipping_fee=shipping_fee,
        cod_fee=cod_fee,
        discount_amount=discount_amount,
        order_total=order_total,
        order_status=PENDING if payment_method == CREDIT_CARD else PLACED,
        estimated_tax=estimated_tax
    )

    # create the order items
    order_items = [OrderItem(
        order=order,
        variant=item.product_variant,
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

    OrderItem.objects.bulk_create(order_items, batch_size=500)

    update_ordered_products_stock(cart_items)

    empty_customer_cart(customer)

    if payment_method == CREDIT_CARD:
        payment_intention = create_payment_intention(order, shipping_address)
        order.payment_url = payment_intention.get('payment_url')
    elif payment_method == CASH_ON_DELIVERY:
        send_email_async("Your order has been placed", f"Your order has been placed successfully with order id: {order.id}", [customer.email])

    return order


def restock_order(order):
    variants_to_update = []
    for item in order.items.all():
        item.variant.stock += item.quantity
        variants_to_update.append(item.variant)
    ProductVariant.objects.bulk_update(variants_to_update, ['stock', 'updated_at'], 500)
    log_info(f"Order {order.id} has been restocked successfully")

def create_full_refund(paymob_transaction_id, amount):
    url = 'https://accept.paymob.com/api/acceptance/void_refund/refund'
    payload = json.dumps({
        "transaction_id": paymob_transaction_id,
        "amount_cents": amount * 100,
    })
    headers = {
        'Authorization': f'Token {settings.PAYMOB_SECRET_KEY}',
        'Content-Type': 'application/json',
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    data = response.json()

    if not data.get('success'):
        log_error(f"Error while creating full refund request: {data}")
        return False
    log_info(f"Transaction {paymob_transaction_id} has been full refunded successfully")
    return True



def create_void_refund(paymob_transaction_id):
    url = 'https://accept.paymob.com/api/acceptance/void_refund/void'
    payload = json.dumps({
        "transaction_id": paymob_transaction_id
    })
    headers = {
        'Authorization': f'Token {settings.PAYMOB_SECRET_KEY}',
        'Content-Type': 'application/json',
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    data = response.json()

    if not data.get('success'):
        log_error(f"Error while creating void refund request: {data}")
        return False

    log_info(f"Transaction {paymob_transaction_id} has been void refunded successfully")
    return True

# the user can try to cancel the order if
# the payment method is cash on delivery and the order status is placed
# the payment method is credit card and the order status is placed and the paymob_transaction_id is not null
# the user can't cancel the order if the payment method is credit card and the order status is pending (didn't complete the payment yet)
# the user can't cancel the order if the payment method is cash on delivery and the order status is shipped or delivered
# the user can't cancel the order if the order status is cancelled or system cancelled

@transaction.atomic()
def cancel_order(order):
    try:
        is_restock_and_cancel_needed = order.payment_method == CASH_ON_DELIVERY
        is_restock_and_cancel_needed = is_restock_and_cancel_needed or (order.payment_method == CREDIT_CARD and order.order_status in [PENDING, PAYMENT_FAILED])

        if order.payment_method == CREDIT_CARD and order.order_status == PLACED and order.paymob_transaction_id:
            is_cancelled =  create_void_refund(order.paymob_transaction_id) if order.created_at.date() == order.updated_at.date() else create_full_refund(order.paymob_transaction_id, order.order_total)
            is_restock_and_cancel_needed =  is_cancelled
            if not is_cancelled:
                log_error(f"Error while cancelling the order with paymob_transaction_id {order.paymob_transaction_id}, order id: {order.id}")
                return

        if not is_restock_and_cancel_needed:
            log_error(f"Can't cancel the order with payment method {order.payment_method} and order status {order.order_status} and paymob_transaction_id {order.paymob_transaction_id}, order id: {order.id}")
            return

        # restock the order
        restock_order(order)
        order.order_status = CANCELLED
        order.save()
        send_email_async("Order Cancelled", f"Your order with order id: {order.id} has been cancelled successfully", [order.customer.email])
        return True

    except Exception as e:
        log_error(f"Error while Cancelling the order: {e}")


def create_payment_intention(order, shipping_address):
    payment_method = order.payment_method
    if payment_method != CREDIT_CARD: return {}

    customer = order.customer
    items =  order.items.all()
    # items = model_to_dict(items)
    url = "https://accept.paymob.com/v1/intention/"

    payload = json.dumps({
        "amount": int(order.order_total) * 100,
        "currency": "EGP",
        "payment_methods": config("PAYMOB_PAYMENT_METHODS_IDS", cast=lambda v: [int(x) for x in v.split(",")]),
        # "items":items,
        "billing_data": {
            "first_name": customer.first_name or "first_name",
            "last_name": customer.last_name or "last_name",
            "email": customer.email or "example@domain.com",
            "phone_number": str(customer.phone) or "01000000000",
            "apartment": shipping_address.apartment_number or 1,
            "floor": shipping_address.floor_number or 1,
            "building": shipping_address.building_number or 1,
            "street": shipping_address.street or "Sadat",
            "state": shipping_address.state or "Cairo",
            "country": shipping_address.country or "Egypt",
        },

        "extras": {
            "order_id": order.id,
            "customer_id": customer.id,
        }
    })
    headers = {
        'Authorization': f'Token {config("PAYMOB_SECRET_KEY")}',
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    data = response.json()
    client_secret = data.get('client_secret')
    if not client_secret:
        print("data:", data)
        return data
    print("client_secret:", client_secret)
    payment_url=f"https://accept.paymob.com/unifiedcheckout/?publicKey={config("PAYMOB_PUBLIC_KEY")}&clientSecret={client_secret}"

    return {
        "payment_url": payment_url ,
    }


def validate_hmac(payload, received_hmac):

    if not received_hmac:
        log_warning("Missing HMAC signature in the request.")
        return

    # Step 2: Sort the data by keys lexicographically
    hmac_keys = [
        "amount_cents", "created_at", "currency", "error_occured",
        "has_parent_transaction", "id", "integration_id", "is_3d_secure",
        "is_auth", "is_capture", "is_refunded", "is_standalone_payment",
        "is_voided", "order.id", "owner", "pending", "source_data.pan",
        "source_data.sub_type", "source_data.type", "success"
    ]

    # Extract and sort the relevant keys
    sorted_data = []
    for key in hmac_keys:
        value = get_nested_value(payload, key)
        if value is not None:
            sorted_data.append(value if isinstance(value, str) else json.dumps(value))

    # Step 3: Concatenate the values in the specified order
    concatenated_string = ''.join(sorted_data)

    # Step 4: Compute the HMAC using SHA512
    hmac_secret = settings.PAYMOB_HMAC_SECRET
    computed_hmac = hmac.new(hmac_secret.encode(), concatenated_string.encode(), hashlib.sha512).hexdigest()

    # Step 5: Compare the HMAC values
    if hmac.compare_digest(computed_hmac, received_hmac):
        log_info("HMAC validation succeeded. Processing callback.")
        return True
    log_warning(f"Invalid HMAC signature. Received: {received_hmac}, Computed: {computed_hmac}")
