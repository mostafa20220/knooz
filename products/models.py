from django.db import models, transaction
from users.models import User

class BaseTimeStamp(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Brand(BaseTimeStamp):
    name = models.CharField(max_length=50, unique=True )
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Category(BaseTimeStamp):
    name = models.CharField(max_length=50, unique=True )
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class VariantSize(BaseTimeStamp):
    size = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.size

class VariantColor(BaseTimeStamp):
    color = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.color


class Product(BaseTimeStamp):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='products')
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='products')
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT, related_name='products')

    free_shipping = models.BooleanField(default=False)
    free_return = models.BooleanField(default=False)
    best_selling = models.BooleanField(default=False)
    best_rated = models.BooleanField(default=False)
    is_returnable = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['name', 'seller','brand'], name='unique_product')
        ]

    def __str__(self):
        return self.name

class ProductVariant(BaseTimeStamp):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    size = models.ForeignKey(VariantSize, on_delete=models.PROTECT, blank=True, null=True,related_name='variants')
    color = models.ForeignKey(VariantColor, on_delete=models.PROTECT, blank=True, null=True,related_name='variants')

    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)


class VariantImage(BaseTimeStamp):
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='product_images/')
    image_alt = models.CharField(max_length=255, blank=True)
    is_default = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        with transaction.atomic():
            if self.is_default:
                VariantImage.objects.filter(variant=self.variant).update(is_default=False)
            super().save(*args, **kwargs)

    def __str__(self):
        return self.image.url
