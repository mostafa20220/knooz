from rest_framework import serializers
from products.models import Product, ProductVariant, VariantImage, VariantSize, VariantColor, Brand, Category
from django.db import transaction

from users.serializers import UserSerializer


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ['name']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['name']

class VariantSizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = VariantSize
        fields = ['size']

class VariantColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = VariantColor
        fields = ['color']

class VariantImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = VariantImage
        fields = '__all__'

class ProductVariantSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    images = serializers.ListField(child=serializers.ImageField(), required=False, write_only=True)

    class Meta:
        model = ProductVariant
        fields = '__all__'
        extra_kwargs = {
            'product': {'required': False},
            }

    def create(self, validated_data):
        product = validated_data.get('product')
        if not product:
            raise serializers.ValidationError("Product is required")

        # check there is no other variant with the same size and color to the same product
        if ProductVariant.objects.filter(product=product, size=validated_data.get('size'), color=validated_data.get('color')).exists():
            raise serializers.ValidationError("Variant already exists for this product")

        images = validated_data.pop('images', [])
        variant = ProductVariant.objects.create(**validated_data)
        variant_images = [VariantImage(variant=variant, image=image) for image in images]
        VariantImage.objects.bulk_create(variant_images)
        return variant

    # return the images along with the variant
    def to_representation(self, instance):
        data = super().to_representation(instance)
        size = VariantSizeSerializer(instance.size).data
        color = VariantColorSerializer(instance.color).data
        images = VariantImageSerializer(instance.variantimage_set.all(), many=True).data
        data['images'] = images
        data = {**data, **size, **color}
        return data

class ProductSerializer(serializers.ModelSerializer):
    variants = ProductVariantSerializer(many=True,write_only=True, required=False)
    class Meta:
        model = Product
        fields = '__all__'
        extra_kwargs = {
            'seller': {'read_only': True, 'required': False},
            }


    # return the variants along with the product
    def to_representation(self, instance):
        data = super().to_representation(instance)
        brand = BrandSerializer(instance.brand).data
        category = CategorySerializer(instance.category).data
        variants = ProductVariantSerializer(instance.productvariant_set.all(), many=True).data
        seller = UserSerializer(instance.seller).data
        data['brand'] = brand.get('name')
        data['category'] = category.get('name')
        data['variants'] = variants
        data['seller'] = seller
        return data

    def create(self, validated_data):
        variants_data = validated_data.pop('variants')
        request = self.context.get('request')
        seller = request.user if request and hasattr(request, 'user') else None

        # check if there is a product with the same name and brand to the same seller
        if Product.objects.filter(name=validated_data.get('name'), brand=validated_data.get('brand'), seller=seller).exists():
            raise serializers.ValidationError("Product already exists")

        with transaction.atomic():
            product = Product.objects.create(seller=seller, **validated_data)
            print("product", product)
            # bulk_create instead of creating one by one
            variants =[ProductVariant(product=product, **variant_data) for variant_data in variants_data]
            ProductVariant.objects.bulk_create(variants)
        return product
    
    @transaction.atomic()
    def update(self, instance, validated_data):
        # Update base product fields
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.category = validated_data.get('category', instance.category)
        instance.brand = validated_data.get('brand', instance.brand)

        instance.free_shipping = validated_data.get('free_shipping', instance.free_shipping)
        instance.free_return = validated_data.get('free_return', instance.free_return)
        instance.best_selling = validated_data.get('best_selling', instance.best_selling)
        instance.best_rated = validated_data.get('best_rated', instance.best_rated)
        instance.is_active = validated_data.get('is_active', instance.is_active)

        instance.save(update_fields=['name', 'description', 'category', 'brand', 'free_shipping', 'free_return', 'best_selling', 'best_rated', 'is_active'])

        # Handle variants update
        if not validated_data.get('variants'):
            return instance
        
        variants_data = validated_data.pop('variants')

        print("variants_data", variants_data)
        variant_ids = [variant_data['id'] for variant_data in variants_data if 'id' in variant_data]
        print("variant_ids", variant_ids)

        # Get existing variants to update
        existing_variants = ProductVariant.objects.filter(id__in=variant_ids, product=instance)

        # Convert queryset to a dictionary for easy access
        variant_dict = {variant.id: variant for variant in existing_variants}

        # List for bulk_update
        variants_to_update = []

        # List for creating new variants (if any)
        variants_to_create = []

        for variant_data in variants_data:
            variant_id = variant_data.get('id', None)

            if variant_id and variant_id in variant_dict:
                # Update the existing variant
                variant = variant_dict[variant_id]
                variant.color = variant_data.get('color', variant.color)
                variant.size = variant_data.get('size', variant.size)
                variant.price = variant_data.get('price', variant.price)
                variant.quantity = variant_data.get('quantity', variant.quantity)

                variants_to_update.append(variant)
            else:
                # Create new variant
                variants_to_create.append(ProductVariant(product=instance, **variant_data))

        # Perform bulk update and bulk create
        with transaction.atomic():
            if variants_to_update:
                ProductVariant.objects.bulk_update(variants_to_update, ['color', 'size', 'price', 'quantity'])
            if variants_to_create:
                ProductVariant.objects.bulk_create(variants_to_create)

        return instance
