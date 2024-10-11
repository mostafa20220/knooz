from itertools import product

from more_itertools.recipes import quantify
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from carts.models import Cart
from products.models import ProductVariant
from products.serializers import ProductVariantSerializer, ProductSerializer


class CartSerializer(serializers.ModelSerializer):
    product_variant = serializers.PrimaryKeyRelatedField(queryset=ProductVariant.objects.all())

    class Meta:
        model = Cart
        fields = ['id', 'product_variant', 'quantity']
        extra_kwargs = {
            'quantity': {'required': True, 'min_value': 1}
        }

    def validate(self, data):
        stock = data.get('product_variant').stock
        quantity = data.get('quantity')

        self._validate_quantity(quantity, stock)
        return data


    @staticmethod
    def _validate_quantity(quantity, stock):
        if quantity > stock:
            raise ValidationError(f"Only {stock} in stock")


    def create(self, validated_data):
        # check if the cart item already exists and update the quantity

        request = self.context.get('request')
        customer = request.user if request and hasattr(request, 'user') else None
        product_variant = validated_data.get('product_variant')

        cart_item = Cart.objects.filter(customer=customer, product_variant=product_variant).first()
        quantity = validated_data.get('quantity')
        if cart_item:
            new_quantity = cart_item.quantity + quantity
            if new_quantity > product_variant.stock:
                raise serializers.ValidationError(f"Only {product_variant.stock} in stock")

            cart_item.quantity = new_quantity
            cart_item.save()
            return cart_item

        cart = Cart.objects.create(customer=customer, **validated_data)
        return cart


    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['product_variant'] = ProductVariantSerializer(instance.product_variant).data
        return data


