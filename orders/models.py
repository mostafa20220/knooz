from django.db import models
from core.constants import PAYMENT_METHOD_CHOICES, CASH_ON_DELIVERY
from core.models import BaseTimeStamp
from products.models import ProductVariant
from users.models import User

# payment method choices

# order status choices
PENDING = 'pending'
CANCELLED = 'cancelled'  # Order is cancelled by the user (only if the order is not shipped = either pending or placed)
PLACED = 'placed' # Order is placed by the user (after payment step is completed)
SHIPPED = 'shipped'
DELIVERED = 'delivered' # Order is delivered to the user (if the payment method is COD, then we assume the payment is completed)
RETURNED = 'returned' # Order is returned by the user (only could happen after being delivered)
REFUNDED = 'refunded' # Order is refunded to the user (only could happen after being delivered)

ORDER_STATUS_CHOICES = [
    (PENDING, 'Pending'),
    (PLACED, 'Placed'),
    (CANCELLED, 'Cancelled'),
    (SHIPPED, 'Shipped'),
    (DELIVERED, 'Delivered'),
    (RETURNED, 'Returned'),
    (REFUNDED, 'Refunded')
]

class Order(BaseTimeStamp):
    customer = models.ForeignKey('users.User', on_delete=models.CASCADE,related_name='orders')
    shipping_address = models.TextField() # take a snapshot of the shipping address at the time of the order
    payment_method = models.CharField(choices=PAYMENT_METHOD_CHOICES, max_length=20, default=CASH_ON_DELIVERY)
    order_status= models.CharField(choices=ORDER_STATUS_CHOICES, default=PENDING, max_length=20)

    items_value = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_fee = models.DecimalField(max_digits=10, decimal_places=2, default=20)
    cod_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0) # cash on delivery fee
    coupon_code = models.CharField(max_length=50, blank=True, null=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0) # discount amount (by coupon code percentage * items_total_price)
    order_total = models.DecimalField(max_digits=10, decimal_places=2) # items_total_price + shipping_fee - discount_amount
    estimated_tax = models.DecimalField(max_digits=10, decimal_places=2, default=0) # 14% of order_total


class OrderItem(models.Model):
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE,related_name='items')

    product_uuid = models.CharField(max_length=50) # product unique id
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    seller = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='ordered_products') # I am not sure
    category = models.CharField(max_length=50)
    brand = models.CharField(max_length=50)
    size = models.CharField(max_length=10, blank=True, null=True)
    color = models.CharField(max_length=50, blank=True, null=True)
    image = models.ImageField(upload_to='order_product_images/', blank=True, null=True)

    free_shipping = models.BooleanField(default=False)
    free_return = models.BooleanField(default=False)
    is_returnable = models.BooleanField(default=True)
    best_selling = models.BooleanField(default=False)
    best_rated = models.BooleanField(default=False)

    quantity = models.PositiveSmallIntegerField()
    item_price = models.DecimalField(max_digits=10, decimal_places=2) # product_variant.price * quantity