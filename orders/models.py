from django.db import models

from products.models import ProductVariant
from users.models import User

# payment method choices
CREDIT_CARD = 'credit card'
CASH_ON_DELIVERY = 'cash on delivery'
PAYMENT_METHOD_CHOICES = [
    (CREDIT_CARD, 'Credit Card'),
    (CASH_ON_DELIVERY, 'Cash on Delivery')
]

# order status choices
PENDING = 'pending'
CANCELLED = 'cancelled'  # Order is cancelled by the user (only if the order is not shipped = either pending or placed)
PLACED = 'placed' # Order is placed by the user (after payment step is completed)
SHIPPED = 'shipped'
DELIVERED = 'delivered' # Order is delivered to the user (if the payment method is COD, then we assume the payment is completed)
REFUNDED = 'refunded' # Order is refunded to the user (only could happen after being delivered)

ORDER_STATUS_CHOICES = [
    (PENDING, 'Pending'),
    (CANCELLED, 'Cancelled'),
    (PLACED, 'Placed'),
    (SHIPPED, 'Shipped'),
    (DELIVERED, 'Delivered'),
    (REFUNDED, 'Refunded')
]

class Order(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    shipping_address = models.TextField() # take a snapshot of the shipping address at the time of the order
    payment_method = models.CharField(choices=PAYMENT_METHOD_CHOICES, max_length=20)
    payment_details = models.TextField(blank=True, null=True) # store the payment details (last 4 digits, etc.)
    order_status= models.CharField(choices=ORDER_STATUS_CHOICES, default=PENDING, max_length=20)

    items_value = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_fee = models.DecimalField(max_digits=10, decimal_places=2, default=20)
    coupon_code = models.CharField(max_length=50, blank=True, null=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0) # discount amount (by coupon code percentage * items_total_price)
    order_total = models.DecimalField(max_digits=10, decimal_places=2) # items_total_price + shipping_fee - discount_amount
    estimated_tax = models.DecimalField(max_digits=10, decimal_places=2, default=0) # 14% of order_total

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product_variant = models.ForeignKey(ProductVariant, on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField()
    item_price = models.DecimalField(max_digits=10, decimal_places=2) # product_variant.price * quantity