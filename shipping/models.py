from django.db import models

class ShippingAddress(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.PROTECT)

    country = models.CharField(max_length=50)
    state = models.CharField(max_length=50,null=True,blank=True)
    city = models.CharField(max_length=50)
    postal_code = models.CharField(max_length=10)
    building_number = models.IntegerField()
    floor_number = models.IntegerField(null=True,blank=True)
    apartment_number = models.IntegerField(null=True,blank=True)
    description = models.CharField(max_length=255, blank=True, null=True)

    is_default = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

# choices for shipment status

# PENDING = 'PENDING'
# COMPLETED = 'COMPLETED'
# SHIPMENT_STATUS_CHOICES = [
#     (PENDING, 'Pending'),
#     (COMPLETED, 'Completed')
# ]

# class Shipment(models.Model):
#     order_id = models.ForeignKey('orders.Order', on_delete=models.PROTECT)
#     shipment_status = models.CharField(choices=SHIPMENT_STATUS_CHOICES, default=PENDING)  # Example: 'pending', 'completed'
#     courier = models.CharField(choices=COURIER_CHOICES, default=ARAMEX)
#     tracking_number = models.CharField(max_length=50)
#     shipment_date = models.DateTimeField(auto_now_add=True)
#     delivery_date = models.DateTimeField(auto_now_add=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#     shipping_address = models.ForeignKey(ShippingAddress, on_delete=models.PROTECT)
