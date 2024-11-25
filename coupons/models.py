from django.core.exceptions import ValidationError
from django.db import models

from core.models import BaseTimeStamp

DEFAULT_USAGE_LIMIT = 1_000

# Create your models here.
class Coupon(BaseTimeStamp):
    code = models.CharField(max_length=50)
    discount_percentage = models.FloatField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    is_active = models.BooleanField(default=True)
    is_global = models.BooleanField()
    category = models.ForeignKey('products.Category', on_delete=models.SET_NULL, null=True, blank=True,related_name='coupons')

    min_order_value = models.DecimalField(max_digits=10, decimal_places=2)
    max_discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    max_use_per_user = models.IntegerField(default=1)
    usage_limit = models.PositiveIntegerField(default=DEFAULT_USAGE_LIMIT)
    usage_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.code


    def clean(self):
        if self.usage_count >= self.usage_limit:
            raise ValidationError('Usage count cannot be greater than or equal to usage limit.')
        if self.max_use_per_user > self.usage_limit:
            raise ValidationError('Max use per user cannot be greater than usage limit.')
        if self.start_date >= self.end_date:
            raise ValidationError('Start date must be before end date.')

    def save(self, *args, **kwargs):
        self.clean()  # Call the clean method to perform validation
        super().save(*args, **kwargs)

class CouponVariant(models.Model):
    coupon = models.ForeignKey('coupons.Coupon', on_delete=models.CASCADE,related_name='variants')
    productVariant = models.ForeignKey('products.ProductVariant', on_delete=models.CASCADE,related_name='coupons')
