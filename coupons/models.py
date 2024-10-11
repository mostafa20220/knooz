from django.db import models

# Create your models here.
class Coupon(models.Model):
    code = models.CharField(max_length=50)
    discount_percentage = models.FloatField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    is_active = models.BooleanField(default=True)
    is_global = models.BooleanField()
    category = models.ForeignKey('products.Category', on_delete=models.SET_NULL, null=True, blank=True)

    min_order_value = models.DecimalField(max_digits=10, decimal_places=2)
    max_discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    max_use_per_user = models.IntegerField(default=1)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.code

class CouponVariant(models.Model):
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE)
    productVariant = models.ForeignKey('products.ProductVariant', on_delete=models.CASCADE)
