from django.contrib import admin
from .models import Coupon, CouponVariant

# Register your models here.
admin.site.register(Coupon)
admin.site.register(CouponVariant)