from rest_framework import serializers
from users.models import User


class UserSerializer(serializers.ModelSerializer):
    is_active = serializers.BooleanField(default=True)
    
    
    class Meta:
        model = User
        fields = ('id', 'first_name','last_name', 'email','user_type','is_active','phone', 'password')
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        print("validated_data: ", validated_data)
        user = User.objects.create_user(**validated_data)
        return user