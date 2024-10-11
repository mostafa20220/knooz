from django.db import models, transaction
from users.models import User

class Brand(models.Model):
    name = models.CharField(max_length=50, unique=True )
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=50, unique=True )
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    seller = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT)

    free_shipping = models.BooleanField(default=False)
    free_return = models.BooleanField(default=False)
    best_selling = models.BooleanField(default=False)
    best_rated = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['name', 'seller', 'brand']

    def __str__(self):
        return self.name


class VariantSize(models.Model):
    size = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.size

class VariantColor(models.Model):
    color = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.color


class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    size = models.ForeignKey(VariantSize, on_delete=models.PROTECT)
    color = models.ForeignKey(VariantColor, on_delete=models.PROTECT)

    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class VariantImage(models.Model):
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='product_images/')
    image_alt = models.CharField(max_length=255, blank=True)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        with transaction.atomic():
            if self.is_default:
                VariantImage.objects.filter(variant=self.variant).update(is_default=False)
            super().save(*args, **kwargs)

    def __str__(self):
        return self.image.url
