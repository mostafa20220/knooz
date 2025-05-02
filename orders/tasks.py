from celery import shared_task
from django.core.management import call_command
from django.utils.timezone import now, timedelta
from django_celery_beat.models import PeriodicTask, IntervalSchedule

from orders.models import Order, PAYMENT_FAILED
from products.models import ProductVariant

#
# @shared_task(bind=True, max_retries=3, default_retry_delay=30)
# def mark_orders_failed_and_restock():
#
#     print("Running mark_orders_failed_and_restock task...")
#
#     # Calculate the time threshold (1 hour ago)
#     one_hour_ago = now() - timedelta(hours=1)
#
#     # Fetch all orders older than 1 hour and with status 'PENDING'
#     orders = Order.objects.filter(status='PENDING', created_at__lt=one_hour_ago)
#
#     # Loop through each order to mark as failed and restock
#     orders_to_update = []
#     variants_to_update = []
#     for order in orders:
#         order.status = TRANSACTION_FAILED
#         orders_to_update.append(order)
#
#         # Loop through order items and restock the products
#         for item in order.order_items.all():
#             variant = item.variant
#             variant.stock += item.quantity
#             variants_to_update.append(variant)
#
#     # Bulk update the orders and variants
#     Order.objects.bulk_update(orders_to_update, ['status', 'updated_at'], 500)
#     ProductVariant.objects.bulk_update(variants_to_update, ['stock', 'updated_at'], 500)
#
#     # Optionally notify the admin about this task
#     print("Order statuses have been updated to TRANSACTION_FAILED and stock has been restocked.")
#
#
# def create_periodic_task():
#     # Create an interval schedule (every 5 minutes)
#     schedule, _ = IntervalSchedule.objects.get_or_create(
#         every=1,  # Run every 1 minutes
#         period=IntervalSchedule.MINUTES,
#     )
#
#     # Check if the periodic task already exists
#     task_name = "Mark Orders Failed and Restock"
#     if not PeriodicTask.objects.filter(name=task_name).exists():
#         PeriodicTask.objects.create(
#             interval=schedule,
#             name=task_name,
#             task="orders.tasks.mark_orders_failed_and_restock",
#         )
#         print("Periodic task created successfully.")
#     else:
#         print("Periodic task already exists.")
#

@shared_task
def handle_unplaced_orders():
    call_command("handle_unplaced_orders")

