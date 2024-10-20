from django.db import models

from core.models import BaseTimeStamp


# Create your models here.
class WishlistItem(BaseTimeStamp):
    customer = models.ForeignKey('users.User', on_delete=models.CASCADE,related_name='wishlist')
    product_variant = models.ForeignKey('products.ProductVariant', on_delete=models.CASCADE,related_name='wishlist')

    def __str__(self):
        return 'wishlist item: ' + self.customer.email + ' - ' + self.product_variant.product.name

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['customer', 'product_variant'], name='unique_wishlist_item')
        ]