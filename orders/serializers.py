from decimal import Decimal

from django.db import transaction
from django.db.models import F
from rest_framework import serializers

from carts.views import  calc_cod_fee, calc_shipping_fee, calc_items_value
from coupons.serializers import validate_coupon_code, calc_discount_amount
from orders.models import Order, OrderItem, CASH_ON_DELIVERY, CREDIT_CARD
from products.models import ProductVariant
from users.models import ShippingAddress, CreditCard


def calc_estimated_tax(order_total):
    return Decimal('0.14') * order_total

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    shipping_address = serializers.PrimaryKeyRelatedField(queryset=ShippingAddress.objects.all())
    credit_card = serializers.PrimaryKeyRelatedField(queryset=CreditCard.objects.all(), required=False,write_only=True)
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        exclude = ['customer']
        # all the other fields are readonly
        extra_kwargs = {
            'items_value': {'read_only': True},
            'shipping_fee': {'read_only': True},
            'cod_fee': {'read_only': True},
            'discount_amount': {'read_only': True},
            'order_total': {'read_only': True},
            'estimated_tax': {'read_only': True},
        }

    def validate(self, attrs):
        self._validate_the_cart_is_not_empty()
        self._validate_shipping_address(attrs.get('shipping_address'))
        self._validate_payment_method(attrs.get('payment_method'))
        if attrs.get('payment_method') == CREDIT_CARD:
            self._validate_credit_card(attrs.get('credit_card'))

        coupon = validate_coupon_code(attrs.get('coupon_code'), self.context['request'].user)
        attrs['coupon'] = coupon
        return attrs

    def _validate_the_cart_is_not_empty(self):
        customer = self.context.get('request').user
        cart_items = customer.cart.all()
        print("cart_items: ",cart_items)
        print("len(cart_items)",len(cart_items))
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

    def _validate_credit_card(self, credit_card):
        if not credit_card:
            raise serializers.ValidationError("Credit card details are required")

        # validate the credit card that its belongs to the user
        customer = self.context['request'].user
        if credit_card.user != customer:
            raise serializers.ValidationError("This credit card does not belong to you")

        return credit_card

    @transaction.atomic()
    def create(self, validated_data):
        # prepare the needed data to create the order
        customer = self.context['request'].user
        cart_items = customer.cart.all()

        shipping_address = str(validated_data.get('shipping_address'))
        payment_method = validated_data.get('payment_method')
        coupon = validated_data.get('coupon')
        coupon_code = validated_data.get('coupon_code')

        items_value = calc_items_value(cart_items)
        shipping_fee = calc_shipping_fee(items_value, cart_items)
        cod_fee = calc_cod_fee(payment_method)
        discount_amount = calc_discount_amount(coupon, items_value)

        order_total = sum([items_value, shipping_fee, cod_fee]) - discount_amount

        estimated_tax = calc_estimated_tax(order_total)

        # create the order
        order = Order.objects.create(
            customer=customer,
            shipping_address=shipping_address,
            payment_method=payment_method,
            coupon_code=coupon_code,
            items_value=items_value,
            shipping_fee=shipping_fee,
            cod_fee=cod_fee,
            discount_amount=discount_amount,
            order_total=order_total,
            estimated_tax=estimated_tax
        )

        # update the coupon usage count
        coupon.usage_count += 1
        coupon.save()

        # create the order items
        order_items = [OrderItem(
            order = order,
            name= item.product_variant.product.name,
            description= item.product_variant.product.description,
            seller= item.product_variant.product.seller,
            category= item.product_variant.product.category.name,
            brand= item.product_variant.product.brand.name,
            size= item.product_variant.size.size,
            color= item.product_variant.color.color,
            free_shipping= item.product_variant.product.free_shipping,
            free_return= item.product_variant.product.free_return,
            is_returnable= item.product_variant.product.is_returnable,
            best_selling= item.product_variant.product.best_selling,
            best_rated= item.product_variant.product.best_rated,
            quantity= item.quantity,
            item_price= item.product_variant.price * item.quantity,
            product_uuid= item.product_variant.product.product_uuid,
            # image = item.product_variant.images.first() if item.product_variant.images.first() else None
        ) for item in cart_items ]

        print("order_items:", order_items)
        OrderItem.objects.bulk_create(order_items, batch_size=500)

        # update the stock of the products
        updated_products =  []
        for cart_item in customer.cart.all():
            cart_item.product_variant.stock -= cart_item.quantity
            updated_products.append(cart_item.product_variant)
        ProductVariant.objects.bulk_update(updated_products, ['stock','updated_at'], 500)

        # delete the cart items
        cart_items.delete()

        return order