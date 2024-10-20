from django.db import IntegrityError
from django.db.models import UniqueConstraint
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from carts.serializers import ListCartProduct
from products.models import ProductVariant
from products.serializers import ListProductVariantSerializer
from wishlists.models import WishlistItem


class WishlistItemSerializer(serializers.ModelSerializer):
    product_variant = serializers.PrimaryKeyRelatedField(queryset=ProductVariant.objects.all())
    product = ListCartProduct(read_only=True, source='product_variant.product')

    class Meta:
        model = WishlistItem
        exclude = ['customer']
        constraints = [
            UniqueConstraint(fields=['customer', 'product_variant'], name='unique_wishlist_item')
        ]

    # handle the possible integrity error when creating a wishlist item
    def create(self, validated_data):
        try:
            return super().create(validated_data)
        except IntegrityError:
            raise ValidationError({"detail": "This item is already in your wishlist."})

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data.pop('product_variant')
        variant = ListProductVariantSerializer(instance.product_variant).data
        data['product'] = {**data.get('product'), **variant}
        return data
