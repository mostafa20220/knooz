from django.forms import model_to_dict
from rest_framework import serializers

from coupons.serializers import validate_coupon_code
from orders.models import Order, OrderItem, PENDING, PLACED
from core.constants import CASH_ON_DELIVERY, CREDIT_CARD
from orders.services import place_new_order, create_payment_intention, cancel_order
from users.models import ShippingAddress

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    shipping_address = serializers.PrimaryKeyRelatedField(queryset=ShippingAddress.objects.all())
    items = OrderItemSerializer(many=True, read_only=True)
    payment_url = serializers.CharField(read_only=True, required=False)

    class Meta:
        model = Order
        exclude = ['customer']
        # all the other fields are readonly
        extra_kwargs = {
            'items_value': {'read_only': True},
            'shipping_fee': {'read_only': True},
            'cod_fee': {'read_only': True},
            'coupon_code': {'required': False},
            'discount_amount': {'read_only': True},
            'estimated_tax': {'read_only': True},
            'order_total': {'read_only': True},
            'shipping_address_snapshot': {'read_only': True},
        }

    def validate(self, attrs):
        self._validate_the_cart_is_not_empty()
        self._validate_shipping_address(attrs.get('shipping_address'))
        self._validate_payment_method(attrs.get('payment_method'))

        coupon_code = attrs.pop('coupon_code',None)
        if coupon_code:
            coupon = validate_coupon_code(coupon_code, self.context['request'].user)
            attrs['coupon'] = coupon
        return attrs

    def _validate_the_cart_is_not_empty(self):
        customer = self.context.get('request').user
        cart_items = customer.cart.all()
        if not len(cart_items):
            raise serializers.ValidationError("The Cart is Empty, Can't Order Yet.")

    def _validate_shipping_address(self, shipping_address):
        customer = self.context['request'].user
        if shipping_address.user != customer:
            raise serializers.ValidationError("This shipping address does not belong to you")

    def _validate_payment_method(self, payment_method):
        if payment_method not in [CREDIT_CARD, CASH_ON_DELIVERY]:
            raise serializers.ValidationError("Invalid payment method")
        return payment_method

    def create(self, validated_data):
        new_order = place_new_order(**validated_data)
        return new_order


