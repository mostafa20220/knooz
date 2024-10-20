from decimal import Decimal

from django.db import transaction
from django.utils import timezone
from rest_framework import serializers

from carts.views import SHIPPING_FEE, COD_FEE
from coupons.models import Coupon
from orders.models import Order, OrderItem, CASH_ON_DELIVERY, CREDIT_CARD, PENDING, PLACED, CANCELLED
from users.models import ShippingAddress, CreditCard

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
        self._validate_shipping_address(attrs.get('shipping_address'))
        self._validate_payment_method(attrs.get('payment_method'))
        if attrs.get('payment_method') == CREDIT_CARD:
            self._validate_credit_card(attrs.get('credit_card'))

        coupon = self._validate_coupon_code(attrs.get('coupon_code'))
        attrs['coupon'] = coupon
        return attrs

    def _validate_shipping_address(self, shipping_address):
        customer = self.context['request'].user
        if shipping_address.user != customer:
            raise serializers.ValidationError("This shipping address does not belong to you")

    def _validate_coupon_code(self, coupon_code):
        if not coupon_code:
            return
        customer = self.context['request'].user
        coupon = Coupon.objects.filter(code__iexact=coupon_code).first()
        if not coupon:
            raise serializers.ValidationError("Invalid coupon code")
        # check if the coupon is active
        if not coupon.is_active:
            raise serializers.ValidationError("This coupon is not active")
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
        shipping_address = validated_data.get('shipping_address')
        fields = ['apartment_number', 'floor_number', 'building_number', 'street', 'postal_code', 'city', 'state', 'country', 'description']
        # create the shipping address snapshot where each field : field value is separated by a comma
        address_list = []
        for field in fields:
            value = getattr(shipping_address, field)
            if value:
                address_list.append(f"{field}: {value}")
        shipping_address_snapshot = ', '.join(address_list)

        cart_items = customer.cart.all()
        print("cart_items:", cart_items)

        shipping_fee = Decimal('0.00')
        items_value = sum([Decimal(str(item.product_variant.price * item.quantity)) for item in cart_items])

        if items_value < Decimal('2000.00'):
            for item in cart_items:
                is_free_shipping = item.product_variant.product.free_shipping
                if not is_free_shipping:
                    shipping_fee = Decimal(str(SHIPPING_FEE))
                    break

        # calculate the payment details based on the payment method
        payment_details = None
        cod_fee = Decimal('0.00')
        payment_method = validated_data.get('payment_method')
        if  payment_method == CREDIT_CARD:
            credit_card = validated_data.get('credit_card')
            payment_details = f"**** **** **** {credit_card.card_number[-4:]}"
        else: # cash on delivery
            payment_details = "Cash on delivery"
            cod_fee = COD_FEE

        # calculate the discount amount based on the coupon
        discount_amount = Decimal('0.00')
        coupon = validated_data.get('coupon')
        if coupon:
            discount_amount = Decimal(str(coupon.discount_percentage)) * items_value / Decimal('100.00')
            if discount_amount > coupon.max_discount_value:
                discount_amount = coupon.max_discount_value

        order_total = items_value + shipping_fee + cod_fee - discount_amount
        estimated_tax = Decimal('0.14') * order_total

        # create the order
        order = Order.objects.create(
            customer=customer,
            shipping_address=shipping_address_snapshot,
            payment_method=payment_method,
            payment_details=payment_details,
            coupon_code=validated_data.get('coupon_code'),
            items_value=items_value,
            shipping_fee=shipping_fee,
            cod_fee=cod_fee,
            discount_amount=discount_amount,
            order_total=order_total,
            estimated_tax=estimated_tax
        )

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
            image = item.product_variant.images.first() if item.product_variant.images.first() else None
        ) for item in cart_items ]

        print("order_items:", order_items)
        OrderItem.objects.bulk_create(order_items, batch_size=500)

        # delete the cart items
        # cart_items.delete()

        return order

    def update(self, instance, validated_data):
        order_status = validated_data.get('order_status')

        # can only cancel the order if it is not shipped yet (either pending or placed)
        if order_status == CANCELLED and instance.order_status in [PENDING,PLACED]:
            instance.order_status = order_status
            instance.save()