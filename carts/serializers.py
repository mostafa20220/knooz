from itertools import product

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from carts.models import Cart
from products.models import ProductVariant, Product
from products.serializers import ListProductVariantSerializer
from users.serializers import UserSerializer


class ListCartProduct(serializers.ModelSerializer):
    seller = serializers.StringRelatedField()
    category = serializers.StringRelatedField()
    brand = serializers.StringRelatedField()

    class Meta:
        model = Product
        exclude = ['created_at', 'updated_at','id']

class CartSerializer(serializers.ModelSerializer):
    product_variant = serializers.PrimaryKeyRelatedField(queryset=ProductVariant.objects.all())
    product = ListCartProduct(read_only=True, source='product_variant.product')
    quantity= serializers.IntegerField(min_value=1)

    class Meta:
        model = Cart
        fields = ['id', 'product_variant', 'quantity', 'product']

    def validate(self, data):
        # use the cart item id that is sent as a pk to update the quantity
        if self.instance:
            if 'quantity' in data:
                quantity = data.get('quantity')
                stock = self.instance.product_variant.stock
                self._validate_quantity(quantity, stock)
            return data

        stock = data.get('product_variant').stock
        quantity = data.get('quantity')

        self._validate_quantity(quantity, stock)
        return data


    @staticmethod
    def _validate_quantity(quantity, stock):
        if quantity > stock:
            raise ValidationError(f"Your requested quantity is more than the available right now")


    def create(self, validated_data):
        # check if the cart item already exists and update the quantity
        print("validated_data:", validated_data)
        request = self.context.get('request')
        customer = request.user if request and hasattr(request, 'user') else None
        product_variant = validated_data.get('product_variant')

        cart_item = Cart.objects.filter(customer=customer, product_variant=product_variant).first()
        quantity = validated_data.get('quantity')
        if cart_item:
            new_quantity = cart_item.quantity + quantity
            if new_quantity > product_variant.stock:
                raise serializers.ValidationError(f"Your requested quantity is more than the available right now")

            cart_item.quantity = new_quantity
            cart_item.save()
            return cart_item

        cart = Cart.objects.create(customer=customer, **validated_data)
        return cart


    def to_representation(self, instance):
        data = super().to_representation(instance)
        data.pop('product_variant')
        variant = ListProductVariantSerializer(instance.product_variant).data
        data['product'] = {**data.get('product'), **variant}
        return data


    # def to_representation(self, instance):
    #     data = super().to_representation(instance)
    #     data['product'] = {**data.get('product'), **data.pop('product_variant')}
    #     return data
