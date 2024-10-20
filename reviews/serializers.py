from rest_framework import serializers
from reviews.models import ProductReview


class ProductReviewSerializer(serializers.ModelSerializer):
    customer = serializers.StringRelatedField(read_only=True)
    class Meta:
        model = ProductReview
        fields = '__all__'
        read_only_fields = ['customer', 'seller', 'likes_count']


    def validate(self, attrs):
        customer = self.context.get('request').user
        product = attrs.get('product')
        if ProductReview.objects.filter(customer=customer, product=product).exists():
            raise serializers.ValidationError("You have already reviewed this product.")
        return attrs
