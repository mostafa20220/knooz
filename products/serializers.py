from encodings.base64_codec import base64_decode

from rest_framework import serializers
from products.models import Product, ProductVariant, VariantImage, VariantSize, VariantColor, Brand, Category
from django.db import transaction

from users.serializers import UserSerializer


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

class VariantImageSerializer(serializers.ModelSerializer):
    image = serializers.CharField(write_only=True)
    class Meta:
        model = VariantImage
        fields = ['image','image_alt','is_default']

class CreateProductVariantSerializer(serializers.ModelSerializer):
    size = serializers.PrimaryKeyRelatedField(queryset=VariantSize.objects.all())
    color = serializers.PrimaryKeyRelatedField(queryset=VariantColor.objects.all())
    images = VariantImageSerializer(many=True, required=False)

    class Meta:
        model = ProductVariant
        fields = ['size', 'color', 'price', 'stock', 'images']
        extra_kwargs = {
            'product': {'required': False}}

    def create(self, validated_data):
        product = validated_data.get('product')
        if not product:
            raise serializers.ValidationError("Product is required")

        # check there is no other variant with the same size and color to the same product
        if ProductVariant.objects.filter(product=product, size=validated_data.get('size'), color=validated_data.get('color')).exists():
            raise serializers.ValidationError("Variant already exists for this product")

        images = validated_data.pop('images', [])
        variant = ProductVariant.objects.create(**validated_data)
        img_file = base64_decode(images[0].get('image'))
        print("img_file:", img_file)
        variant_images = [VariantImage(variant=variant, image=image) for image in images]
        VariantImage.objects.bulk_create(variant_images, batch_size=500)
        return variant

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

class DetailProductVariantSerializer(serializers.ModelSerializer):
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


class ListProductSerializer(serializers.ModelSerializer):
    variants = ListProductVariantSerializer(many=True)
    brand = serializers.CharField(source='brand.name')
    category = serializers.CharField(source='category.name')
    seller = UserSerializer(read_only=True, required=False)

    class Meta:
        model = Product
        exclude = ['created_at','updated_at']



class CreateProductSerializer(serializers.ModelSerializer):
    variants = CreateProductVariantSerializer(many=True)
    brand = serializers.PrimaryKeyRelatedField(queryset=Brand.objects.all())
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    is_active = serializers.BooleanField(default=True, required=False, write_only=True)
    seller = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Product
        exclude = ['created_at', 'updated_at']

    def create(self, data):
        variants_data = data.pop('variants')

        print("seller:", data.get('seller'))

        # check if there is a product with the same name and brand to the same seller
        if Product.objects.filter(name=data.get('name'), brand=data.get('brand'),
                                  seller=data.get('seller')).exists():
            raise serializers.ValidationError("Product already exists")

        # creating the product and its variants and its images in a transaction
        with transaction.atomic():
            product = Product.objects.create(**data)
            images = []
            for variant_data in variants_data:
                variant_images = variant_data.pop('images', [])
                variant = ProductVariant.objects.create(**variant_data, product=product)
                images.extend([VariantImage(variant=variant, **image) for image in variant_images])
            VariantImage.objects.bulk_create(images, batch_size=500)
        return product


class ProductDetailSerializer(serializers.ModelSerializer):
    variants = DetailProductVariantSerializer(many=True)
    brand = BrandSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    seller = UserSerializer(read_only=True)

    class Meta:
        model = Product
        fields = '__all__'

    @transaction.atomic()
    def update(self, instance, validated_data):

        #  product update
        update_fields = ['name', 'description', 'category', 'brand', 'free_shipping', 'free_return',
                         'best_selling', 'best_rated', 'is_active']
        for field in update_fields:
            setattr(instance, field, validated_data.get(field, getattr(instance, field)))
        instance.save(update_fields=update_fields)

        # variants update and create
        if not validated_data.get('variants'):
            return instance

        variants = validated_data.pop('variants')
        update_fields = ['color', 'size', 'price', 'stock']

        variants_to_create = []
        variants_to_update = []
        for variant in variants:
            variant_id = variant.get('id')
            if not variant_id:
                variants_to_create.append(variant)
            else:
                product_variant = ProductVariant.objects.get(id=variant_id)
                for field in update_fields:
                    setattr(product_variant, field, variant.get(field, getattr(product_variant, field)))
                variants_to_update.append(product_variant)

        ProductVariant.objects.bulk_create(variants_to_create,batch_size=500)
        ProductVariant.objects.bulk_update(variants_to_update, fields=update_fields, batch_size=500)

        return instance
