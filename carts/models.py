from django.db import models
from products.models import ProductVariant
from users.models import User


class Cart(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE, editable=False)
    product_variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, editable=False)
    quantity = models.IntegerField()

    # don't allow duplicate product_variant for the same customer instead update the quantity
    class Meta:
        unique_together = ['customer', 'product_variant']