from decimal import Decimal

from django.utils import timezone
from rest_framework import serializers

from carts.services import get_cart_items_value
from coupons.models import Coupon


def validate_coupon_code(coupon_code, customer):
    if not coupon_code:
        raise serializers.ValidationError("Coupon code is required")
    coupon = Coupon.objects.filter(code__iexact=coupon_code).first()
    if not coupon:
        raise serializers.ValidationError("Invalid coupon code")
    # check if the coupon is active
    if not coupon.is_active:
        raise serializers.ValidationError("This coupon is not active")
    # check if the coupon is used more than the usage limit
    if coupon.usage_count >= coupon.usage_limit:
        raise serializers.ValidationError("This coupon is expired")
    # check if the coupon is expired
    if not coupon.start_date < timezone.now() < coupon.end_date:
        raise serializers.ValidationError("This coupon is expired")

    # check if the coupon is used more than the max_use_per_user
    if customer.orders.filter(coupon_code=coupon.code).count() >= coupon.max_use_per_user:
        raise serializers.ValidationError("This coupon is used more than the max use per user")

    # check if the order value is more than the min_order_value
    order_value = sum([item.product_variant.price * item.quantity for item in customer.cart.all()])
    if order_value < coupon.min_order_value:
        raise serializers.ValidationError("This coupon is not valid for this order value")

    # check if the coupon is global or for a specific category
    if not coupon.is_global:
        # check if the coupon is for a specific category
        if not coupon.category:
            raise serializers.ValidationError("This coupon is not valid for this category")
        # check if the all cart items from the category
        cart_items = customer.cart.all()
        for item in cart_items:
            if item.product_variant.product.category != coupon.category:
                raise serializers.ValidationError("This coupon is not valid for this category")

    return coupon


def calc_discount_amount(coupon, items_value):
    discount_amount = Decimal('0.00')
    if coupon:
        discount_amount = Decimal(str(coupon.discount_percentage)) * items_value / Decimal('100.00')
        if discount_amount > coupon.max_discount_value:
            discount_amount = coupon.max_discount_value
    return discount_amount


class ApplyCouponSerializer(serializers.Serializer):
    coupon_code = serializers.CharField(max_length=50,write_only=True)
    discount_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    def validate(self, attrs):
        print("attrs:-> ",attrs)
        coupon_code = attrs.get('coupon_code')
        customer = self.context['request'].user

        coupon = validate_coupon_code(coupon_code, customer)
        cart_items = self._validate_cart()

        attrs['coupon'] = coupon
        attrs['cart_items'] = cart_items
        return attrs

    def _validate_cart(self):
        cart_items = self.context['request'].user.cart.all()
        if not cart_items:
            raise serializers.ValidationError("Cart is empty")
        return cart_items

    def create(self, validated_data):
        coupon = validated_data.get('coupon')
        cart_items = validated_data.get('cart_items')

        items_value = get_cart_items_value(cart_items)
        discount_amount = calc_discount_amount(coupon, items_value)
        return {'discount_amount': discount_amount}