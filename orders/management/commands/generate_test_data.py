import random
from decimal import Decimal
from uuid import uuid4

from django.core.management.base import BaseCommand

from core.constants import CASH_ON_DELIVERY, CREDIT_CARD, SHIPPING_FEE, COD_FEE
from orders.models import Order, OrderItem, PENDING, REFUNDED, RETURNED, DELIVERED, SHIPPED, PLACED, SYSTEM_CANCELLED, \
    REFUND_FAILED, CANCELLED, PAYMENT_FAILED
from users.models import User, ShippingAddress
from products.models import ProductVariant, VariantSize, VariantColor, Category, Brand
from django.db import transaction


PAYMENT_METHODS = [ CASH_ON_DELIVERY,  CREDIT_CARD ]
ORDER_STATUSES = [ PENDING, PAYMENT_FAILED, CANCELLED, REFUND_FAILED, SYSTEM_CANCELLED, PLACED, SHIPPED, DELIVERED, RETURNED, REFUNDED ]

class Command(BaseCommand):
    help = "Generate 1 million orders with related order items"

    def add_arguments(self, parser):
        parser.add_argument('--orders', type=int, default=1_000_000, help="Number of orders to create")
        parser.add_argument('--chunk-size', type=int, default=1_000, help="Chunk size for bulk creation")

    def handle(self, *args, **options):
        num_orders = options['orders']
        chunk_size = options['chunk_size']

        # Fetch related models data
        users = list(User.objects.all())
        addresses = list(ShippingAddress.objects.all())
        product_variants = list(ProductVariant.objects.all())
        sizes = list(VariantSize.objects.all())
        colors = list(VariantColor.objects.all())
        categories = list(Category.objects.all())
        brands = list(Brand.objects.all())

        if not users or not addresses or not product_variants\
                or not sizes or not colors or not categories or not brands:
            self.stderr.write("Ensure there are users, shipping addresses, product variants, sizes, colors, categories, and brands in the database.")
            return

        orders = []
        order_items = []

        self.stdout.write("Generating orders and order items...")
        with transaction.atomic():
            for i in range(num_orders):
                customer = random.choice(users)
                shipping_address = random.choice(addresses)
                items_value = Decimal(random.uniform(10, 500)).quantize(Decimal('0.01'))
                shipping_fee = SHIPPING_FEE
                cod_fee = Decimal(0 if random.choice([True, False]) else COD_FEE)
                discount_amount = Decimal(random.uniform(0, 50)).quantize(Decimal('0.01'))
                order_total = items_value + shipping_fee - discount_amount
                estimated_tax = (order_total * Decimal(0.14)).quantize(Decimal('0.01'))
                payment_method = random.choice(PAYMENT_METHODS)

                order = Order(
                    customer=customer,
                    paymob_transaction_id=uuid4(),
                    shipping_address=shipping_address,
                    shipping_address_snapshot=str(shipping_address),
                    payment_method=random.choice(PAYMENT_METHODS),
                    order_status=random.choice(ORDER_STATUSES),
                    items_value=items_value,
                    shipping_fee=  shipping_fee if items_value < 200  else 0 ,
                    cod_fee=cod_fee if payment_method == CASH_ON_DELIVERY else 0,
                    discount_amount=discount_amount,
                    order_total=order_total,
                    estimated_tax=estimated_tax,
                )
                orders.append(order)

                # Create 1-5 order items per order
                for _ in range(random.randint(1, 5)):
                    variant = random.choice(product_variants)
                    quantity = random.randint(1, 10)
                    item_price = (variant.price * quantity).quantize(Decimal('0.01'))

                    order_items.append(OrderItem(
                        order=order,
                        product_uuid=uuid4(),
                        variant=variant,
                        name=variant.product.name,
                        description=variant.product.description,
                        seller=variant.product.seller,
                        category=random.choice(categories),
                        brand=random.choice(brands),
                        size=random.choice(sizes),
                        color=random.choices(colors),
                        free_shipping=variant.product.free_shipping,
                        free_return=variant.product.free_return,
                        is_returnable=variant.product.is_returnable,
                        best_selling=variant.product.best_selling,
                        best_rated=variant.product.best_rated,
                        quantity=quantity,
                        item_price=item_price,
                    ))

                # Bulk insert in chunks
                if (i + 1) % chunk_size == 0:
                    Order.objects.bulk_create(orders)
                    OrderItem.objects.bulk_create(order_items)
                    orders.clear()
                    order_items.clear()
                    self.stdout.write(f"Inserted {i + 1} orders...")

            # Final insert for remaining records
            if orders:
                Order.objects.bulk_create(orders)
                OrderItem.objects.bulk_create(order_items)

        self.stdout.write(f"Successfully generated {num_orders} orders with items.")

