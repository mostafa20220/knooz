from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db.transaction import TransactionManagementError
from django_celery_beat.utils import now

from core.constants import CREDIT_CARD
from orders.models import Order, PENDING, CANCELLED, PAYMENT_FAILED, REFUND_FAILED, SYSTEM_CANCELLED
from products.models import ProductVariant


class Command(BaseCommand):
    help = "handle unplaced orders"

    def handle(self, *args, **kwargs):

        self.stdout.write(self.style.SUCCESS('Running mark_orders_failed_and_restock task...'))

        # Calculate the time threshold (1 hour ago)
        one_hour_ago = now() - timedelta(hours=1)

        # Fetch all orders older than 1 hour and with status 'PENDING'
        orders = (Order.objects
                  .filter(payment_method=CREDIT_CARD, order_status__in=[PENDING, PAYMENT_FAILED], created_at__lt=one_hour_ago)
                  .prefetch_related('items__variant')
                  .only('order_status', 'items__quantity', 'items__variant__stock'))

        if not orders:
            self.stdout.write(self.style.SUCCESS('No orders to update.'))
            return

        # Loop through each order to mark as failed and restock
        orders_to_update = []
        variants_to_update = set()
        for order in orders:
            order.order_status = SYSTEM_CANCELLED
            orders_to_update.append(order)

            # Loop through order items and restock the products
            for item in order.items.all():
                variant = item.variant
                variant.stock += item.quantity
                if variant not in variants_to_update:
                    variants_to_update.add(variant)

        # Bulk update the orders and variants
        Order.objects.bulk_update(orders_to_update, ['order_status', 'updated_at'], 500)
        self.stdout.write(self.style.SUCCESS(f'{len(orders_to_update)} orders updated.'))

        ProductVariant.objects.bulk_update(variants_to_update, ['stock', 'updated_at'], 500)
        self.stdout.write(self.style.SUCCESS(f'{len(variants_to_update)} variants updated.'))

        self.stdout.write(self.style.SUCCESS('Order statuses have been updated to CANCELLED and stock has been restocked.'))
