import uuid
import base64
from django.core.files.base import ContentFile

from products.services import create_product
from users.serializers import UserSerializer
from rest_framework import serializers
from drf_writable_nested import WritableNestedModelSerializer
from products.models import Product, ProductVariant, VariantImage, VariantSize, VariantColor, Brand, Category


################## Base Serializers ####################

class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        exclude = ['created_at', 'updated_at']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        exclude = ['created_at','updated_at']

class VariantSizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = VariantSize
        exclude = ['created_at','updated_at']

class VariantColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = VariantColor
        exclude = ['created_at','updated_at']


################## Image Serializers ####################

class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        print("image data type:", type(data))
        if isinstance(data, ContentFile):
            return data

        if not (isinstance(data, str) and data.startswith('data:image')):
            raise serializers.ValidationError("Invalid image format or data")
        # Decode the Base64 image
        format, img_str = data.split(';base64,')  # format: data:image/png;base64
        ext = format.split('/')[-1]  # Get image file extension (e.g., png, jpeg)
        img_data = base64.b64decode(img_str)
        file_name = f"{uuid.uuid4()}.{ext}"
        return ContentFile(img_data, name=file_name)


class VariantImageSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = VariantImage
        fields = ['image','image_alt','is_default']


################## List Serializers ####################

class ListProductVariantSerializer(serializers.ModelSerializer):
    size = serializers.CharField(source='size.size')
    color = serializers.CharField(source='color.color')
    images = VariantImageSerializer(many=True, required=False)
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    class Meta:
        model = ProductVariant
        fields = [ 'size', 'color', 'price','images']
        extra_kwargs = {
            'product': {'required': False},
            }


class ListProductSerializer(serializers.ModelSerializer):
    variants = ListProductVariantSerializer(many=True)
    brand = serializers.CharField(source='brand.name')
    category = serializers.CharField(source='category.name')
    seller = UserSerializer(read_only=True, required=False)

    class Meta:
        model = Product
        exclude = ['created_at','updated_at']


############### Create serializers ####################

class CreateProductVariantSerializer(serializers.ModelSerializer):
    images = VariantImageSerializer(many=True, required=False)
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), required=False)
    size = serializers.PrimaryKeyRelatedField(queryset=VariantSize.objects.all())
    color = serializers.PrimaryKeyRelatedField(queryset=VariantColor.objects.all())

    class Meta:
        model = ProductVariant
        fields = ['size', 'color', 'price', 'stock', 'images', 'product', 'id']

    def validate(self, attrs):
        size = attrs.get('size')
        color = attrs.get('color')
        product = attrs.get('product')

        if ProductVariant.objects.filter(product=product, size=size, color=color).exists():
            raise serializers.ValidationError("Variant already exists")
        return attrs


class CreateProductSerializer(serializers.ModelSerializer):
    variants = CreateProductVariantSerializer(many=True)
    brand = serializers.PrimaryKeyRelatedField(queryset=Brand.objects.all())
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    is_active = serializers.BooleanField(default=True, required=False, write_only=True)
    seller = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Product
        exclude = ['created_at', 'updated_at']

    def validate(self, attrs):
        name = attrs.get('name')
        brand = attrs.get('brand')
        seller = self.context['request'].user
        if Product.objects.filter(name=name, brand=brand, seller=seller).exists():
            raise serializers.ValidationError("Product already exists")

        return attrs


    def create(self, validated_data):
        new_product = create_product(validated_data)
        return new_product


################## Detail Serializers ####################

class DetailProductVariantSerializer(WritableNestedModelSerializer):
    id = serializers.IntegerField(required=False)
    size = VariantSizeSerializer(read_only=True)
    color = VariantColorSerializer(read_only=True)
    images = VariantImageSerializer(many=True, required=False)
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    class Meta:
        model = ProductVariant
        fields = ['id', 'size', 'color', 'price','images']
        extra_kwargs = {
            'product': {'required': False},
        }


class DetailProductSerializer(WritableNestedModelSerializer):
    variants = DetailProductVariantSerializer(many=True)
    brand = BrandSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    seller = UserSerializer(read_only=True)

    class Meta:
        model = Product
        fields = '__all__'
