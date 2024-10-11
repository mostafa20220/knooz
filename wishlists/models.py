from django.db import models

# Create your models here.
class WishlistItem(models.Model):
    customer = models.ForeignKey('users.User', on_delete=models.CASCADE)
    product_variant = models.ForeignKey('products.ProductVariant', on_delete=models.CASCADE)

    def __str__(self):
        return 'wishlist item: ' + self.customer.email + ' - ' + self.product_variant.product.name