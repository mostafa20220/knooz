from django.contrib import admin
from .models import Coupon, CouponVariant

class CouponVariantInline(admin.TabularInline):
    model = CouponVariant

class CouponAdmin(admin.ModelAdmin):
    inlines = [CouponVariantInline]

# Register your models here.
admin.site.register(Coupon,CouponAdmin)