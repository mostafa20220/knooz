from django.db import transaction
from products.models import Product, ProductVariant, VariantImage


@transaction.atomic()
def create_product(data):
    variants = data.pop('variants')
    variants_images_list = [variant.pop('images', []) for variant in variants]
    with transaction.atomic():
        new_product = Product.objects.create(**data)
        product_variants = [ProductVariant(product=new_product, **variant) for variant in variants]
        ProductVariant.objects.bulk_create(product_variants, batch_size=500)

        variants_images = [VariantImage(**img, variant=variant) for i, variant in enumerate(product_variants) for img in variants_images_list[i]]
        VariantImage.objects.bulk_create(variants_images, batch_size=500)
    
    return new_product

def get_product_queryset():
     return (Product.objects
            .select_related(
                'category',
                'brand',
                'seller'
            )
            .prefetch_related(
                'variants__images',
                'variants__size',
                'variants__color'
            )
            .order_by('-created_at'))

def get_seller_products_queryset(seller):
    return (Product.objects
            .filter(seller=seller)
            .select_related(
                'category',
                'brand'
            )
            .prefetch_related(
                'variants__images',
                'variants__size',
                'variants__color'
            )
            .order_by('-created_at'))