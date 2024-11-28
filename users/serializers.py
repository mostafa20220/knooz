from django.db import IntegrityError
from django.db.models import UniqueConstraint
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from users.models import User, ShippingAddress


class ShippingAddressSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShippingAddress
        fields = '__all__'
        extra_kwargs = {
            'user': {'read_only': True}
        }
        constraints = [
            UniqueConstraint(fields=['user', 'country', 'city', 'postal_code', 'street', 'building_number','floor_number','apartment_number'], name='unique_shipping_address')
        ]

    def create(self, validated_data):
        try:
            return super().create(validated_data)
        except IntegrityError:
            raise ValidationError({"detail": "A shipping address with these details already exists."})

class UserSerializer(serializers.ModelSerializer):
    is_active = serializers.BooleanField(default=True,write_only=True)

    class Meta:
        model = User
        fields = ('id', 'first_name','last_name', 'email','is_active','phone', 'password','user_type')
        extra_kwargs = {
            'password': {'write_only': True},
            'user_type': {'write_only': True}
        }

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user